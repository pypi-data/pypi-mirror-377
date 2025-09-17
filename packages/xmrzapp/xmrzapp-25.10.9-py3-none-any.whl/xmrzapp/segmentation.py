import cv2
import numpy as np
from . import DEFAULT_FACE_PROTOTXT, DEFAULT_FACE_CAFFEMODEL, DEFAULT_SEGMENTATION_MODEL
import tensorflow as tf

Interpreter = tf.lite.Interpreter


class SegmentationNetwork:
    """Performs MRZ segmentation using a TFLite model."""

    def __init__(self, model_path: str = DEFAULT_SEGMENTATION_MODEL):
        self.interpreter = Interpreter(model_path=model_path)
        self.interpreter.allocate_tensors()
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

    def process(self, image):
        if isinstance(image, str):
            img = cv2.imread(image, cv2.IMREAD_COLOR)
        else:
            img = image
        img = cv2.resize(img, (256, 256), interpolation=cv2.INTER_NEAREST)
        img = np.float32(img / 255.0)
        if img.shape[-1] > 3:
            img = img[:, :, :3]
        return np.expand_dims(img, axis=0)

    def output(self, output_data, image):
        if isinstance(image, str):
            img = cv2.imread(image, cv2.IMREAD_COLOR)
        else:
            img = image
        h, w = img.shape[:2]
        kernel = np.ones((5, 5), np.uint8)
        mask = (output_data[0, :, :, 0] > 0.35).astype(np.uint8) * 255
        mask = cv2.resize(mask, (w, h))
        mask = cv2.erode(mask, kernel, iterations=3)
        contours, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if not contours:
            return None
        c = max(contours, key=cv2.contourArea)
        x, y, w, h = cv2.boundingRect(c)
        return img[y:y + h, x:x + w].copy()

    def predict(self, image):
        img_array = self.process(image)
        self.interpreter.set_tensor(self.input_details[0]['index'], img_array)
        self.interpreter.invoke()
        output_data = self.interpreter.get_tensor(self.output_details[0]['index'])
        return self.output(output_data, image)


class FaceDetection:
    """Detects faces using Caffe model."""

    def __init__(self, prototxt: str = DEFAULT_FACE_PROTOTXT, caffemodel: str = DEFAULT_FACE_CAFFEMODEL):
        self.faceNet = cv2.dnn.readNet(prototxt, caffemodel)

    def detect(self, image, confidence_input=0.5):
        if isinstance(image, str):
            img = cv2.imread(image, cv2.IMREAD_COLOR)
        else:
            img = image
        h, w = img.shape[:2]
        blob = cv2.dnn.blobFromImage(cv2.resize(img, (300, 300)), 1.0,
                                     (300, 300), (104.0, 177.0, 123.0))
        self.faceNet.setInput(blob)
        detections = self.faceNet.forward()
        for i in range(detections.shape[2]):
            confidence = detections[0, 0, i, 2]
            if confidence > confidence_input:
                box = (detections[0, 0, i, 3:7] * np.array([w, h, w, h])).astype(int)
                x1, y1, x2, y2 = box
                return img[y1:y2, x1:x2].copy(), confidence
        return None, None
