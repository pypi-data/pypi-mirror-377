# BinaExperts SDK

**BinaExperts SDK** is a comprehensive toolkit for computer vision, designed to empower developers and researchers in building innovative visual solutions. Focused on scalability and versatility, it provides a robust foundation for creating state-of-the-art computer vision applications. Its architecture supports seamless integration with various platforms and is continuously evolving to address emerging challenges and opportunities in the field.


## Installation

Install the BinaExperts SDK directly from PyPI:

```bash
pip install binaexperts
```
If you need additional dependencies for inference, install with:

```bash
pip install binaexperts[inference]
```

This will install additional packages required for running inference tasks, such as PyTorch and torchvision.
Ensure that you have a compatible CUDA setup if using GPU acceleration.

## Usage

Once installed, you can start leveraging the SDK’s two core functionalities:

- **Dataset Conversion**: Easily convert datasets between various formats using a unified API. The conversion module supports both file-based and in-memory operations and currently supports the following formats:
  - **COCO**
  - **YOLO**
  - **YOLO - Oriented Bounding Boxes**
  - **BinaExperts**
  - **Inference**: Perform predictions on static images, folders, or zip files or live video streams. Inference currently supports YOLOv5, YOLOv7 and YOLOv8 models for local and live applications.
  - **Live Tracking**: A standalone, high-performance live tracker with persistent ID re-assignment.

## 1. Dataset Conversion

The `Convertor` class simplifies the process of converting datasets between formats such as COCO, YOLO, and BinaExperts.

```python
import binaexperts.convertors

# Initialize the Convertor
convertor = binaexperts.convertors.Convertor()

# Convert from a source dataset to a target format
converted_output = convertor.convert(
    target_format='yolo',
    source='path/to/source_dataset.zip',  # Use 'source' instead of 'source_path' to match method signature
    destination='path/to/target_dataset.zip'  # Optional; if omitted, returns a file-like object.
)

# Save the output if it's returned as an in-memory object
if converted_output:
    with open("output_dataset.zip", "wb") as f:
        f.write(converted_output.read())

print("Conversion completed successfully!")
```
### In-Memory IO Conversion Example

In this example, we demonstrate how to convert a dataset directly from an in-memory BytesIO object and obtain the result in memory—no disk I/O required.
```python
import io
from binaexperts.convertors import Convertor

# Initialize the Convertor
convertor = Convertor()


# Replace 'zip_file_path/file.zip' with the actual path to your zip file
try:
    with open('zip_file_path/file.zip', 'rb') as f:
        source_in_memory_zip = io.BytesIO(f.read())
except FileNotFoundError:
    print("Error: The source file was not found. Please check the path.")
    exit()

print(source_in_memory_zip)
# If you want the output to also be an in-memory BytesIO object, set destination=None
converted_output = convertor.convert(
    target_format='coco',
    source=source_in_memory_zip,
    # destination=None
    destination='path/to/target_dataset.zip'  # Set to None to get BytesIO object as return
)

# Save the output if it's returned as an in-memory object
if converted_output:
    # Ensure the BytesIO object's pointer is at the beginning before reading for saving
    converted_output.seek(0)
    with open("output_dataset.zip", "wb") as f:
        data_written_bytes = f.write(converted_output.read())

    print("Conversion completed successfully!")
    print(f"Data written to output_dataset.zip: {data_written_bytes} bytes")
    print(f"Type of converted_output: {type(converted_output)}")
    print(f"Converted output object: {converted_output}")
else:
    print(
        """Conversion completed, but no in-memory object was 
           returned (possibly due to a destination path being provided to the convert method).""")
```
**Summary**: Use the conversion module to seamlessly switch between dataset formats with minimal configuration, whether working with files on disk or in-memory streams.

---
## 2. Inference

The SDK's `Inference` class provides a unified interface for prediction on images, videos, and live streams.

### Local Inference (Single Image, Folder, or Zip)

The `local_inference` method intelligently handles different sources. Whether you provide a path to a single image, a folder of images, or a `.zip` archive, it will process them all and save the results. It supports **YOLOv5**, **YOLOv7**, and **YOLOv8** models.

```python
from binaexperts.app import Inference

# Initialize the Inference engine (YOLOv8 is now newest valid model_type)
inf = Inference(model_type='yolov8',
                device='cuda', # or 'cpu'
                model_path="path/to/your/model.pt",
                confidence_thres=0.5)
# Process an entire folder or a zip file or a single file
inf.run_interactive_session()
```
For a complete, runnable example demonstrating how to use this class, please refer to the `run_local_inference.py` script located in the project's root directory.

### How to Run

The script is launched from the terminal. You must provide the path to a model file and the image you want to process.

### General Usage
```bash
python run_local_inference.py --model-path <path_to_model> --model-type <type> --source-path <path/to/your/image/folder/zip> --destination-dir <path/to/your/output/folder>   
```
**Arguments:**
* `--model-path <path_to_model>`: The path to the detection model file (e.g., `yolov8.pt`).
* `--source-path <path_to_image_folder_zip>`: The path to the image file, complete folder or zip file you want to analyze.
* `--model-type <type>`: The model architecture.`'yolov8'` recommended.
    * Use `'yolov5'` for YOLOv5 models.
    * Use `'yolov7'` for YOLOv7 models.
    * Use `'yolov8'` for YOLOv8 models.

### Live Inference

For real-time applications, the SDK provides the advanced `LiveInference` class. This non-blocking controller is designed for high-performance, multi-camera scenarios and can be configured to run in different modes, such as `'detection'`, `'tracking'` or `'segmentation'`.
The SDK includes a standalone, high-performance tracker for robust, real-time tracking of people with persistent ID re-assignment. It uses a tuned YOLOv8 and DeepSORT combination.
It abstracts away the complexity of concurrent video processing. By dedicating a background thread to each camera, it provides a simple yet powerful interface for building responsive, multi-camera applications without needing to manage threads manually.
```python
from binaexperts.app import Inference

# Initialize live inference (choose 'yolov5', 'yolov7' or 'yolov8')
inf = Inference(
    model_type='yolov8',
    model_path="path/to/yolov8.pt",
)
# Available modes: 'detection', 'tracking' 'segmentation'
live_controller = inf.live_inference(mode='tracker')
```
For a complete, runnable example demonstrating how to use this class, please refer to the `run_live_inference.py` script located in the project's root directory.

### How to Run 

The script is launched from the terminal. You must specify an inference mode and provide a path to a compatible model file using the following command structure.

### General Usage
```bash
python run_live_inference.py --model-path <path_to_model> --model-type <type> [options]
```
**Arguments:**
* Default inference mode to run is detection (do nothing).
    * Use `'--tracker'` to enable Tracker.
    * Use `'--segmentation'` for precise outlines (masks).
* `--multi-camera` For ≥ 2 cameras
* `--model-path <path_to_model>`: The path to the corresponding model file.
* `--model-type <type>`: yolov8 Highly recommended when `mode` is `'--tracker'` or `'--segmentation'`.
    * Use `'yolov5'` for YOLOv5 models.
    * Use `'yolov7'` for YOLOv7 models. 
    * Use `'yolov8'` for YOLOv8 models.
**Example**: run ```python run_live_inference.py --model-path yolov8n-seg.pt --model-type yolov8 --multi-camera --segmentation```
**Summary**: The inference module extends the SDK’s capabilities, enabling both static and live predictions. It supports YOLOv5, YOLOv7, YOLOv8 models, allowing you to integrate computer vision inference into various applications seamlessly.

---


## Features

- **Unified Inference**: Run predictions on single images, folders, or zip archives and live streams with one method.
- **Dataset Conversion**: Convert datasets effortlessly between various formats.
- **Flexible Multi-Camera LiveInference**: Run high-performance, non-blocking inference on multiple live camera streams using a unified controller with switchable modes for tasks like object detection, Tracking and instance segmentation.
- **Multi-Model Support**: Supports YOLOv5, YOLOv7, and YOLOv8 models within the same interface.
- **Modular Design**: Easily extendable for future formats, training pipelines, and additional inference features.
- **Flexible IO**: Supports both file-based and in-memory operations for versatile deployment scenarios.
- **Live Tracking**: Real-time, multi-object tracking with persistent ID re-assignment using YOLO and DeepSORT.

---

## Future Roadmap

### Data Preparation
- Enhanced conversion tools and additional format support.
- Automated dataset validation to ensure data integrity.

### Training
- Auto-training workflows with model selection, hyperparameter tuning, and comprehensive training pipelines.

### Inference Enhancements
- Further improvements for local fast Inference
- Further improvements for live inference.
- Expanded support for additional model architectures.

### Community Suggestions
- We welcome your ideas and contributions to further enhance the SDK.

---

## Project Structure

```
binaexperts/
│
├── bina/
│   ├── app/
│   ├── services/
│   ├── __init__.py
│   
├── common/
│   ├── __init__.py
│   ├── loadhelpers.py
│   ├── logger.py
│   ├── setup_utils.py
│   ├── utils.py
│   ├── yolo_utils.py
│
├── convertors/
│   ├── schema/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── const.py
│   │   ├── convertor.py
│
├── SDKs/
│   ├── camera/
│   ├── tracker/
│   ├── YOLO/
│   │   ├── yolov5/
│   │   ├── yolov7/
│   │   ├── yolov8/
│   │   ├── __init__.py
├── __init__.py
```

---

## Contributing

The **BinaExperts SDK** was designed and developed by the technical team at **BinaExperts**, led by **Nastaran Dab** and **Mahdi Tajdari**. Contributions, bug reports, documentation improvements, and feature suggestions are welcome. Please reach out to the project team for contribution guidelines.

---

## Acknowledgments

Special thanks to **Nastaran Dab** and **Mahdi Tajdari** for their leadership and contributions in developing and maintaining the **BinaExperts SDK**.

---

## License

This project is licensed under the **MIT License**.
