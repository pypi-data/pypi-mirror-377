# binaexperts/app/inference/inference.py
import cv2
import torch
import numpy as np
import time
import logging
from collections import deque  # For rolling average FPS
from threading import Thread, Event  # Import Event for graceful shutdown
import queue  # For thread-safe frame queue
from .base import BaseInference  # Import BaseInference
from binaexperts.common.yolo_utils import save_annotated_image, preprocess_image, draw_detections  # Import yolo_utils functions
from binaexperts.common.loadhelpers import get_image_paths_from_source
import shutil
import os
from binaexperts.common.utils import select_source_path, select_destination_path  # UI Utils
from binaexperts.SDKs.tracker.deep_sort_tracker import DeepSORTTracker  # Import the tracker
from binaexperts.app.services.inference_service import InferenceService
from binaexperts.SDKs.camera.camera_manager import CameraManager
from binaexperts.SDKs.camera.multi_camera import CameraThread
from ultralytics import YOLO

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Inference:
    """
    A unified class for performing both local (static image) and live (video) YOLO model inference.
    The primary user-facing class for the SDK's inference capabilities.
    It initializes a core InferenceService and provides methods to perform
    detection on static images or to create a controller for live inference.
    """

    def __init__(self, model_type='yolov5', device='cpu', model_path=None, iou=0.5, confidence_thres=0.5,
                 img_size=None):
        """
        Initialize the Inference class.

        Parameters:
            model_type (str): The model architecture to use (e.g., 'yolov5', 'yolov7', 'yolo8').
            model_path (str): The file path to the pre-trained model weights (.pt).
            device (str, optional): The compute device ('cuda' or 'cpu').
                Defaults to 'cuda'.
            iou (float, optional): The Intersection over Union (IoU) threshold
                for non-max suppression. Defaults to 0.5.
            confidence_thres (float, optional): The confidence threshold for
                filtering detections. Defaults to 0.5.
            img_size (tuple, optional): The target image size for inference
                (e.g., (height, width)). If None, it's inferred from the model.
                Defaults to None.

        Raises:
            FileNotFoundError: If the specified `model_path` does not exist.
            Exception: On critical model loading or warmup failures.
        """
        self.model_type = model_type
        self.device = device
        self.iou = iou
        self.confidence_thres = confidence_thres
        self.model_path = model_path
        self.img_size = img_size  # Propagate img_size to BaseInference

        # Initialize list to store monitoring data
        self.monitoring_data = []
        # Create and load the core service engine ONCE.
        logger.info("Initializing and loading the core InferenceService...")
        self.inference_service = InferenceService(
            model_type=self.model_type,
            device=self.device,
            img_size=self.img_size
        )
        # Initialize base inference for shared functionality
        self.base = BaseInference(inference_service_instance=self.inference_service,
                                  monitoring_data=self.monitoring_data)

        try:
            self.inference_service.load_model(self.model_path)
            # Perform model warm-up after loading
            self.inference_service.warmup()
            logger.info("✅ Core service loaded successfully.")
        except Exception as e:
            logger.critical(f"❌ Failed to load model in main Inference class: {str(e)}")
            # Depending on desired behavior, you might want to exit or raise here
            raise

    def get_monitoring_data(self):
        """
        Retrieves the collected monitoring data from all inference runs.

        Returns:
            list: A list of dictionaries, each containing monitoring details for an image or frame.
        """
        return self.monitoring_data

    # batch, zip single image processing
    def local_inference(self, source_path: str, destination_dir: str, output_format="jpg"):
        """
        Runs local inference on a single image, a folder of images, or a zip file.
        This method gets a list of images from the source, processes each one,
        and saves the annotated result to the destination directory.

        Parameters:
            source_path (str): Path to a single image, a folder, or a .zip archive.
            destination_dir (str): Directory where annotated images will be saved.
            output_format (str): The format for the saved images (e.g., 'jpg', 'png').
        """
        logger.info(f"Starting local inference for source: {source_path}")
        local_tool = LocalInference(
            inference_service_instance=self.inference_service,
            monitoring_data=self.monitoring_data
        )
        # local_infer = LocalInference(
        #     model_type=self.model_type,
        #     device=self.device,
        #     model_path=self.model_path, # Pass model_path to LocalInference for its own loading
        #     img_size=self.img_size, # Pass img_size for consistency
        #     monitoring_data=self.monitoring_data # Pass the shared monitoring list
        # )
        os.makedirs(destination_dir, exist_ok=True)
        logger.info(f"Output will be saved in: {os.path.abspath(destination_dir)}")

        image_files, temp_dir = get_image_paths_from_source(source_path)
        if not image_files:
            return  # The helper function will have already logged a warning.

        try:
            logger.info(f"Found {len(image_files)} image(s) to process.")
            for i, image_path in enumerate(image_files):
                filename = os.path.basename(image_path)
                print(f"\\nProcessing image {i + 1}/{len(image_files)}: {filename}")
                output_base_name = os.path.splitext(filename)[0]
                destination_save_path = os.path.join(destination_dir, output_base_name)

                local_tool.predict(
                    image_path=image_path,  # Pass single image path
                    iou_thres=self.iou,
                    confidence_thres=self.confidence_thres,
                    destination=destination_save_path,
                    output_format=output_format
                )
            logger.info("✅ Batch processing complete.")
        finally:
            if temp_dir:
                logger.info("Cleaning up temporary directory...")
                shutil.rmtree(temp_dir)

    def live_inference(self, source=0, tracker=False, segmentation=False):
        """
        Creates and returns a non-blocking, multi-camera live inference controller.
        Perform real-time inference on a video source (webcam or video file).

        Parameters:
            source (int or str): The video source (0 for webcam or a file path for a video file).
            tracker (bool): If True, enables DeepSORT tracking mode. Defaults to False.
            segmentation (bool): If True, enables segmentation mode. Defaults to False.
        """
        # Translate boolean flags into the controller's 'mode' system
        mode = 'detection'
        if tracker:
            mode = 'tracker'
        elif segmentation:
            mode = 'segmentation'

        logger.info(f"Creating live inference controller in '{mode}' mode...")
        live_controller = LiveInference(
            inference_service_instance=self.inference_service,
            mode=mode,
            iou=self.iou,
            source=source,
            model_path=self.model_path, # Pass model_path to LiveInference
            confidence_thres=self.confidence_thres,
            monitoring_data=self.monitoring_data # Pass the shared monitoring list
        )
        return live_controller

    # Interactive Session Method
    def run_interactive_session(self):
        """Launches a fully interactive session for running batch inference.

        This method guides the user to select a source and destination, then
        calls the `local_inference` method to perform the processing.
       """
        print("--- Starting BinaExperts Interactive Inference Session ---")
        source_path = select_source_path()
        if not source_path: return

        destination_dir = select_destination_path()
        if not destination_dir: return

        print(f"\\nSource: {source_path}\\nDestination: {destination_dir}\\nModel: {self.model_path}\\n")
        self.local_inference(source_path=source_path, destination_dir=destination_dir)
        print("\\n--- Interactive session finished. ---")


class LocalInference(BaseInference):
    """Tool for running inference on a single, static image file."""

    def __init__(self, inference_service_instance: InferenceService, monitoring_data=None):
        """Initializes the LocalInference tool.
        This class provides a simplified interface for loading a YOLO model and running
        inference on images.

        Args:
            inference_service_instance (InferenceService): An already initialized
                and loaded InferenceService object that will be used to run
                the model.
            monitoring_data (list, optional): A shared list for logging data.
                Defaults to None.
        """
        super().__init__(inference_service_instance=inference_service_instance, monitoring_data=monitoring_data)

    def predict(self, image_path: str, iou_thres=0.5, confidence_thres=0.5, destination=None, output_format="jpg"):
        """Runs inference on a single image file and optionally saves the result.

        This method takes a file path to an image, runs the full detection
        pipeline, draws the results on the image, and saves the annotated
        image if a destination is provided.

        Args:
            image_path (str): The file path to the image to be processed.
            iou_thres (float, optional): The IoU threshold for non-max
                suppression. Defaults to 0.5.
            confidence_thres (float, optional): The confidence threshold for
                filtering detections. Defaults to 0.5.
            destination (str, optional): The file path (without extension)
                to save the annotated image to. If None, the image is not
                saved. Defaults to None.

        Returns:
            np.ndarray | None: A NumPy array containing the detection data in
            the format [x1, y1, x2, y2, conf, cls], or None if no objects
            were detected or an error occurred.
        """
        if not self.service.model:
            raise RuntimeError("❌ Model is not loaded in the provided InferenceService.")

        try:
            # Load original image for annotation later
            original_img = cv2.imread(image_path)
            if original_img is None:
                logger.warning(f"⚠ Could not load image at {image_path}. Skipping.")
                return None

            # Correctly pass the loaded image (NumPy array) to the preprocessor
            preprocessed_tensor = self._preprocess_image(original_img)

            # Get the raw detection tensor from the service
            results_list = self.service.predict(
                preprocessed_tensor, original_image=original_img,
                iou_thres=iou_thres, confidence_thres=confidence_thres
            )
            detections = results_list[0] if results_list and results_list[0] is not None and len(
                results_list[0]) > 0 else None # This should be a tensor or None

            if detections is None or detections.numel() == 0:
                logger.info(f"⚠ No detections for image: {image_path}")
                return None

            # Draw the results on a copy of the image
            annotated_img = draw_detections(
                original_img.copy(), # Work on a copy to preserve original
                detections, self.names,
                self.service.scale_coords, self.imgsz
            )
            # Optionally save the annotated image if destination is provided
            if destination:
                save_annotated_image(annotated_img, destination, output_format)

            return detections.cpu().numpy() # Return results as a NumPy array

        except Exception as e:
            logger.error(f"❌ Error during local inference for {image_path}: {str(e)}")
            return None

class ProcessingThread(Thread):
    """A dedicated thread for processing one camera's video stream."""

    def __init__(self, live_inference_controller, camera_thread, cam_id):
        super().__init__(daemon=True)
        self.live_controller = live_inference_controller
        self.camera_thread = camera_thread
        self.cam_id = cam_id
        self.is_running = True
        self.fps_buffer = deque(maxlen=30)
        self.prev_frame_time = 0

    def run(self):
        """The main processing loop for this camera."""
        while self.is_running:
            frame = self.camera_thread.get_latest_frame()
            if frame is None:
                time.sleep(0.01)  # Wait briefly if no new frame
                continue

            final_frame = frame.copy()
            # Deconstruct controller attributes for clarity
            service = self.live_controller.service
            mode = self.live_controller.mode

            if mode in ['detection', 'tracker']:
                classes_to_detect = [0] if mode == 'tracker' else None
                results_list = service.predict(
                    self.live_controller._preprocess_image(frame),
                    original_image=frame,
                    iou_thres=self.live_controller.iou_thres,
                    confidence_thres=self.live_controller.confidence_thres,
                    classes=classes_to_detect
                )
                detections = results_list[0] if results_list else None

                if mode == 'tracker':
                    # Fetch the dedicated tracker for this specific camera thread
                    camera_tracker = self.live_controller.trackers.get(self.cam_id)
                    if camera_tracker and detections is not None:
                        tracks = camera_tracker.update_tracks(detections, frame, service.names)
                        for track in tracks:
                            if not track.is_confirmed() or track.time_since_update > 0: continue
                            track_id, ltrb = track.track_id, track.to_ltrb()
                            x1, y1, x2, y2 = map(int, ltrb)
                            cv2.rectangle(final_frame, (x1, y1), (x2, y2), (0, 255, 0), 2)
                            cv2.putText(final_frame, f"ID: {track_id}", (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7,
                                        (0, 255, 0), 2)

                elif mode == 'detection' and detections is not None:
                    draw_detections(final_frame, detections, service.names, service.scale_coords, service.imgsz)

            elif mode == 'segmentation' and self.live_controller.model_seg:
                results = self.live_controller.model_seg(frame, verbose=False)
                final_frame = self.live_controller._draw_segmentation_results(final_frame, results)

            self.live_controller.processed_frames[self.cam_id] = final_frame
            # FPS Calculation and Drawing
            # Calculate FPS
            new_frame_time = time.time()
            if self.prev_frame_time > 0:
                time_diff = new_frame_time - self.prev_frame_time
                if time_diff > 0:
                    current_fps = 1 / time_diff
                    self.fps_buffer.append(current_fps)
            self.prev_frame_time = new_frame_time

            if self.fps_buffer:
                avg_fps = sum(self.fps_buffer) / len(self.fps_buffer)
                fps_text = f"FPS: {avg_fps:.1f}"
                # Draw the FPS on the top-left corner of the frame
                cv2.putText(final_frame, fps_text, (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

    def stop(self):
        self.is_running = False

class LiveInference(BaseInference):
    """Non-blocking controller for multi-camera inference.
    An all-in-one, non-blocking controller for multi-camera inference.

    This class provides a high-level interface to manage the entire lifecycle of
    a real-time, multi-camera computer vision application. It handles camera
    discovery, multithreaded frame grabbing, and AI model inference in the
    background, allowing it to be integrated into responsive applications.

    The controller can be configured to run in different modes, such as 'detection'
    (for bounding boxes) or 'segmentation' (for pixel-level masks).

    Attributes:
        mode (str): The operational mode ('detection' or 'segmentation').
        model_path (str): The file path to the AI model weights.
        is_running (bool): A flag indicating if the processing threads are active.

    Example:
        >>> inference_controller = LiveInference(
        ...     mode='segmentation',
        ...     model_path='yolov8n-seg.pt'
        ... )
        >>> inference_controller.start()
        >>> # Main app loop runs here, getting frames...
        >>> # frame = inference_controller.get_latest_frame('USB_0')
        >>> inference_controller.stop()
    """
    def __init__(self, inference_service_instance: InferenceService, model_path, mode, source=0, iou=0.45, confidence_thres=0.25, monitoring_data=None):
        """Initializes the LiveInference controller.

        Args:
            mode (str): The inference mode to run. Must be either 'detection' or
                'segmentation'.
            model_path (str): The path to the AI model file (e.g., yolov7.pt).
            model_type (str, optional): The model architecture. Required for
                'detection' mode (e.g., 'yolov5', 'yolov7'). Defaults to None.
            device (str, optional): The compute device ('cuda' or 'cpu').
                Defaults to 'cuda'.
            iou (float, optional): The Intersection over Union (IoU) threshold for
                detection. Defaults to 0.45.
            confidence_thres (float, optional): The confidence threshold for
                detection. Defaults to 0.25.
        """
        # 1. Create the InferenceService instance first
        # inference_service = InferenceService(model_type=model_type, device=device)
        # 2. Pass the created instance to the parent (BaseInference) constructor
        super().__init__(inference_service_instance=inference_service_instance, monitoring_data=monitoring_data)
        # --- Configuration --
        self.mode = mode
        self.source = source
        self.iou_thres = iou
        self.confidence_thres = confidence_thres
        # --- State Variables ---
        self.model_path = model_path
        self.trackers = {}  # Plural: holds multiple tracker instances
        self.model_seg = None
        self.camera_threads = {}
        self.processed_frames = {}
        self.is_running = False
        self.processing_threads = {}
        # Use a dynamic number of colors based on the loaded model
        num_classes = 80 # Default for COCO
        if self.service and self.service.names:
            num_classes = len(self.service.names)
        self.colors = self._generate_distinct_colors(num_classes)

    def _generate_distinct_colors(self, num_colors):
        """Generates a list of visually distinct BGR colors."""
        hues = np.linspace(0, 179, num_colors, dtype=np.uint8)
        saturations = np.full_like(hues, 255)
        values = np.full_like(hues, 200)
        hsv_colors = np.stack([hues, saturations, values], axis=1)
        bgr_colors = cv2.cvtColor(hsv_colors.reshape(-1, 1, 3), cv2.COLOR_HSV2BGR)
        return bgr_colors.reshape(-1, 3)

    def _draw_segmentation_results(self, image, results, alpha=0.4):
        """Draws segmentation masks and labels."""
        overlay = image.copy()
        labels_to_draw = []
        # Ensure there are masks to process
        if results[0].masks is not None:
            # Get the original frame dimensions for resizing
            frame_height, frame_width = image.shape[:2]
            for i, mask in enumerate(results[0].masks.data):
                # 1. Get the small mask as a NumPy array
                # Resize the mask to the original frame size
                mask_np = mask.cpu().numpy()
                # 2. Resize the small mask to match the full-size frame
                resized_mask = cv2.resize(
                    mask_np.astype(np.uint8),
                    (frame_width, frame_height),
                    interpolation=cv2.INTER_NEAREST
                ).astype(bool)

                # Get color and apply the mask to the overlay
                box = results[0].boxes[i]
                class_id = int(box.cls)
                color = self.colors[class_id].tolist()
                # Apply the correctly-sized mask to the overlay
                overlay[resized_mask] = color

                # Prepare the label text and position
                class_name = results[0].names[class_id]
                label = f"{class_name}: {float(box.conf):.2f}"
                x1, y1, _, _ = box.xyxy[0].cpu().numpy().astype(int)
                labels_to_draw.append({'text': label, 'pos': (x1, y1)})

        # Combine the overlay with the original image
        image = cv2.addWeighted(overlay, alpha, image, 1 - alpha, 0)

        # Draw the text labels on top
        for item in labels_to_draw:
            label, (x1, y1) = item['text'], item['pos']
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
            cv2.rectangle(image, (x1, y1 - h - 10), (x1 + w + 10, y1), (0, 0, 0), cv2.FILLED)
            cv2.putText(image, label, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

        return image

    def _initialize_cameras(self):
        """
        Initializes camera threads based on the `self.source` attribute.
        - If `source` is an integer or string path, it initializes that single camera.
        - If `source` is 'auto', it discovers and initializes all available cameras.
        """
        logger.info("Initializing camera(s)...")
        device_lister = CameraManager()

        if self.source != 'auto':
            # Handle a single, specified source
            cam_id = f"source_{self.source}"
            manager = CameraManager()
            is_opened = manager.open_usb_camera(self.source)  # Assumes USB/file path

            if is_opened:
                self.camera_threads[cam_id] = CameraThread(manager, cam_id)
                logger.info(f"✅ Successfully initialized source: {self.source}")
            else:
                logger.error(f"❌ Failed to open specified source: {self.source}")
        else:
            # Handle multi-camera auto-discovery
            logger.info("Discovering all connected cameras...")
            all_cameras_info = (device_lister.list_usb_cameras() +
                                device_lister.list_daheng_cameras() +
                                device_lister.list_zds_cameras())
            for cam_info in all_cameras_info:
                cam_id = f"{cam_info['type']}_{cam_info['index']}"
                manager = CameraManager()
                is_opened = False
                if cam_info['type'] == "USB":
                    is_opened = manager.open_usb_camera(cam_info['index'])
                # (Add other camera types like Daheng/ZDS here if needed)

                if is_opened:
                    self.camera_threads[cam_id] = CameraThread(manager, cam_id)

    # --- PUBLIC CONTROL METHODS ---
    def start(self):
        """Initializes and starts the non-blocking inference process."""
        if self.is_running:
            print("Inference is already running.")
            return
        self._initialize_cameras()

        self.is_running = True
        # Start the camera frame-grabbing threads
        for thread in self.camera_threads.values():
            thread.start()
        # INITIALIZE THE CORRECT ENGINE
        logger.info(f"Loading '{self.mode}' engine...")
        if self.mode == 'segmentation':
            logger.info(f"Loading segmentation engine from: {self.model_path}")
            # For segmentation, the model is the YOLO object
            self.model_seg = YOLO(self.model_path)
        # Create and start one processing thread FOR EACH camera
        for cam_id, camera_thread in self.camera_threads.items():
            # If in tracker mode, create a NEW, DEDICATED tracker for this camera
            if self.mode == 'tracker':
                logger.info(f"Creating a dedicated DeepSORT tracker for camera: {cam_id}")
                self.trackers[cam_id] = DeepSORTTracker()
                logger.info("✅ DeepSORT Tracker enabled.")

            proc_thread = ProcessingThread(self, camera_thread, cam_id)
            self.processing_threads[cam_id] = proc_thread
            proc_thread.start()
            logger.info(f"LiveInference started.")

    def stop(self):
        """Stops all background threads and performs cleanup."""
        if not self.is_running: return
        logger.info("Stopping LiveInference...")

        self.is_running = False
        # Stop all processing threads
        for thread in self.processing_threads.values():
            thread.stop()
            thread.join()

        logger.info("✅ LiveInference stopped.")

    def get_latest_frame(self, cam_id):
        """Public method to get the latest processed frame for a specific camera."""
        return self.processed_frames.get(cam_id)