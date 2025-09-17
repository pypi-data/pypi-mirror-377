import cv2
import numpy as np
import os
import tensorflow as tf
from . import weights_dir


class SegmentationNetwork:
    """
    Segmentation network for detecting MRZ regions using a TFLite model.
    """

    def __init__(self, model_path: str = None):
        if model_path is None:
            model_path = os.path.join(weights_dir, "mrz_detector", "mrz_seg.tflite")

        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Segmentation model not found: {model_path}")

        # Load TensorFlow Lite interpreter
        self.interpreter = tf.lite.Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()

        # Get input and output details
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def predict(self, image: np.ndarray) -> np.ndarray:
        """
        Run MRZ segmentation on an image.

        Args:
            image (np.ndarray): BGR image (OpenCV format)

        Returns:
            np.ndarray: Segmentation mask (binary)
        """
        input_shape = self.input_details[0]["shape"]
        h, w = input_shape[1], input_shape[2]

        # Preprocess image
        resized = cv2.resize(image, (w, h))
        input_data = np.expand_dims(resized.astype(np.float32) / 255.0, axis=0)

        # Run inference
        self.interpreter.set_tensor(self.input_details[0]["index"], input_data)
        self.interpreter.invoke()

        # Get output and resize to original
        output_data = self.interpreter.get_tensor(self.output_details[0]["index"])[0]
        mask = cv2.resize(output_data, (image.shape[1], image.shape[0]))

        # Binarize mask
        mask = (mask > 0.5).astype(np.uint8) * 255
        return mask


class FaceDetection:
    """
    Face detection using OpenCV DNN with Caffe model.
    """

    def __init__(self, prototxt_path: str = None, model_path: str = None):
        if prototxt_path is None:
            prototxt_path = os.path.join(weights_dir, "face_detector", "deploy.prototxt")
        if model_path is None:
            model_path = os.path.join(weights_dir, "face_detector", "res10_300x300_ssd_iter_140000.caffemodel")

        if not os.path.exists(prototxt_path):
            raise FileNotFoundError(f"Face detector prototxt not found: {prototxt_path}")
        if not os.path.exists(model_path):
            raise FileNotFoundError(f"Face detector model not found: {model_path}")

        self.net = cv2.dnn.readNetFromCaffe(prototxt_path, model_path)

    def detect(self, image: np.ndarray, confidence_threshold: float = 0.5):
        """
        Detect faces in an image.

        Args:
            image (np.ndarray): BGR image (OpenCV format)
            confidence_threshold (float): Minimum confidence threshold

        Returns:
            list: Bounding boxes [(x1, y1, x2, y2), ...]
        """
        (h, w) = image.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(image, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0))
        self.net.setInput(blob)
        detections = self.net.forward()

        boxes = []
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > confidence_threshold:
                box = detections[0, 0, i, 3:7] * np.array([w, h, w, h])
                (x1, y1, x2, y2) = box.astype("int")
                boxes.append((x1, y1, x2, y2))

        return boxes
