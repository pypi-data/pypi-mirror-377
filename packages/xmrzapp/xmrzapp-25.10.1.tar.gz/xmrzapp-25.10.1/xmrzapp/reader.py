import cv2
import numpy as np
import easyocr

from .segmentation import SegmentationNetwork, FaceDetection
from . import utils


def instantiate_from_config_easyocr(config, reload=False):
    """
    Instantiates an EasyOCR Reader object using a configuration dictionary.

    Parameters
    ----------
    config : dict
        Parameters for easyocr.Reader (e.g., {"lang_list": ["en"], "gpu": False}).
    reload : bool, optional
        If True, reloads the module before instantiation.

    Returns
    -------
    easyocr.Reader
        Configured EasyOCR reader.
    """
    return get_obj_from_str("easyocr.Reader", reload)(**config)


def get_obj_from_str(string, reload=False):
    """
    Dynamically load and return a class/function from a string.

    Parameters
    ----------
    string : str
        Fully qualified name, e.g., "easyocr.Reader".
    reload : bool, optional
        Reload module if True.

    Returns
    -------
    object
        The class or function.
    """
    import importlib

    module, cls = string.rsplit(".", 1)
    if reload:
        module_imp = importlib.import_module(module)
        importlib.reload(module_imp)
    return getattr(importlib.import_module(module, package=None), cls)


class MRZReader:
    """
    Read Machine-Readable Zone (MRZ) data from images using:
    - Segmentation (TFLite model)
    - Face detection (Caffe model)
    - OCR (EasyOCR)

    Example
    -------
    >>> from xmrzapp import MRZReader
    >>> reader = MRZReader({"lang_list": ["en"], "gpu": False})
    >>> text, segmented, face = reader.predict("passport.jpg")
    """

    def __init__(
        self,
        easy_ocr_params: dict,
        facedetection_protxt: str,
        facedetection_caffemodel: str,
        segmentation_model: str,
    ):
        self.segmentation = SegmentationNetwork(segmentation_model)
        self.face_detection = FaceDetection(facedetection_protxt, facedetection_caffemodel)
        self.ocr_reader = instantiate_from_config_easyocr(easy_ocr_params)

    def predict(self, image, do_facedetect=False, facedetect_coef=0.1, preprocess_config=None):
        """
        Predict MRZ text from an image.

        Parameters
        ----------
        image : str or numpy.ndarray
            Path to image file or loaded image.
        do_facedetect : bool, optional
            Run face detection. Default False.
        facedetect_coef : float, optional
            Confidence threshold for face detection.
        preprocess_config : dict, optional
            Preprocessing config: {"do_preprocess": True, "skewness": True, ...}

        Returns
        -------
        tuple
            (text_results, segmented_image, face_roi or None)
        """
        if isinstance(image, str):
            img = cv2.imread(image, cv2.IMREAD_COLOR)
        else:
            img = image

        # Segmentation prediction
        segmented_image = self.segmentation.predict(img)
        if segmented_image is None:
            return [], None, None

        # Optional face detection
        face = None
        if do_facedetect:
            face, _ = self.face_detection.detect(img, facedetect_coef)

        # OCR
        text_results = self.recognize_text(segmented_image, preprocess_config or {})

        return text_results, segmented_image, face

    def recognize_text(self, image, preprocess_config):
        """
        Recognize text from a segmented image.

        Parameters
        ----------
        image : str or numpy.ndarray
            Path to image or loaded image.
        preprocess_config : dict
            Preprocessing options.

        Returns
        -------
        list
            OCR results (text + bounding box).
        """
        if isinstance(image, str):
            img = cv2.imread(image, cv2.IMREAD_COLOR)
        else:
            img = image

        # Preprocessing if requested
        if preprocess_config.get("do_preprocess", False):
            img = self._preprocess_image(img, preprocess_config)

        return self.ocr_reader.readtext(img)

    def _preprocess_image(self, img, preprocess_config):
        """Apply preprocessing steps (skew, shadow, background, morphology, threshold)."""
        img = utils.resize(img)

        if preprocess_config.get("skewness", False):
            try:
                angle, img = utils.correct_skew(img)
            except Exception as e:
                print(f"Skew correction failed: {e}")

        if preprocess_config.get("delete_shadow", False):
            try:
                img = utils.delete_shadow(img)
            except Exception as e:
                print(f"Shadow deletion failed: {e}")

        if preprocess_config.get("clear_background", False):
            try:
                img = utils.clear_background(img)
            except Exception as e:
                print(f"Background clearing failed: {e}")

        img = self._apply_morphological_operations(img)
        img = self._apply_threshold(img)

        return img

    def _apply_morphological_operations(self, img):
        """Apply dilation + erosion."""
        kernel = np.ones((2, 2), np.uint8)
        img = cv2.dilate(img, kernel, iterations=1)
        img = cv2.erode(img, kernel, iterations=1)
        return img

    def _apply_threshold(self, img):
        """Apply binary + adaptive thresholding."""
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
        _, _, v = cv2.split(hsv)
        v = np.uint8(cv2.normalize(v, v, 50, 255, cv2.NORM_MINMAX))
        _, thresh0 = cv2.threshold(v, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        thresh1 = cv2.adaptiveThreshold(
            v, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 33, 2
        )
        return cv2.bitwise_or(thresh0, thresh1)
