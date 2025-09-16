# binaexperts/SDKs/tracker/deep_sort_tracker.py

import os
import logging
from deep_sort_realtime.deepsort_tracker import DeepSort

logger = logging.getLogger(__name__)


class DeepSORTTracker:
    """
    A wrapper for the DeepSORT algorithm with expert-tuned parameters for robust
    re-identification of people/faces.
    """

    def __init__(self):
        """
        Initializes the DeepSORT tracker with pre-tuned parameters for high accuracy.
        """
        logger.info("Initializing and tuning DeepSORT tracker for long-term memory...")

        # These are the expert parameters from the standalone script for high-accuracy tracking.
        self.tracker = DeepSort(
            max_age=900,  # Remember a lost track, How long to remember a lost track (in frames). Prevents incorrect re-ID.
            n_init=5,  # Number of consecutive detections to start a track. Reduces false positives.
            max_cosine_distance=0.5  # Appearance matching strictness (lower is stricter). Slightly more lenient on appearance to handle varying angles.
        )

    def update_tracks(self, detections_tensor, frame, class_names):
        """
        Updates the tracker with new detections from the YOLO model.

        Args:
            detections_tensor (torch.Tensor): The raw detection tensor from the inference service.
                                              Format: [x1, y1, x2, y2, conf, cls_id]
            frame (np.ndarray): The current video frame for appearance feature extraction.
            class_names (list): A list of class names from the model.

        Returns:
            list: A list of active track objects from the DeepSORT tracker.
        """
        if detections_tensor is None or detections_tensor.numel() == 0:
            # If no detections, update the tracker with an empty list to manage track ages.
            return self.tracker.update_tracks([], frame=frame)

        # Convert the YOLOv8 tensor to the format DeepSORT expects:
        # A list of tuples, where each tuple is ([bbox], confidence, class_name)
        detections_for_tracker = []
        for det in detections_tensor:
            x1, y1, x2, y2, conf, cls_id = det
            class_id = int(cls_id)

            # --- SAFEGUARD ---
            # Check if the class_id is valid before trying to access it.
            if 0 <= class_id < len(class_names):
                # Bbox format for DeepSORT is [left, top, width, height]
                bbox = [int(x1), int(y1), int(x2 - x1), int(y2 - y1)]

                detections_for_tracker.append(
                    (bbox, float(conf), class_names[class_id])
                )
            else:
                logger.warning(f"Invalid class ID '{class_id}' detected and skipped.")

        # Update the tracker with the formatted detections
        tracks = self.tracker.update_tracks(detections_for_tracker, frame=frame)
        return tracks