import easyocr
from .segmentation import SegmentationNetwork, FaceDetection
from . import DEFAULT_FACE_PROTOTXT, DEFAULT_FACE_CAFFEMODEL, DEFAULT_SEGMENTATION_MODEL
from . import utils

class MRZReader:
    """MRZ Reader integrating segmentation, face detection, and OCR."""

    def __init__(self,
                 facedetection_protxt: str = DEFAULT_FACE_PROTOTXT,
                 facedetection_caffemodel: str = DEFAULT_FACE_CAFFEMODEL,
                 segmentation_model: str = DEFAULT_SEGMENTATION_MODEL,
                 easy_ocr_params: dict = {"lang_list": ["en"], "gpu": False}):

        self.segmenter = SegmentationNetwork(segmentation_model)
        self.face_detector = FaceDetection(facedetection_protxt, facedetection_caffemodel)
        self.ocr_reader = easyocr.Reader(**easy_ocr_params)

    def predict(self, image_path, do_facedetect=True, preprocess_config=None):
        """Predict MRZ text and optionally detect face."""
        preprocess_config = preprocess_config or {}
        img = utils.load_image(image_path)

        # Preprocessing
        if preprocess_config.get("do_preprocess", True):
            if preprocess_config.get("skewness", True):
                _, img = utils.correct_skew(img)
            if preprocess_config.get("delete_shadow", True):
                img = utils.delete_shadow(img)
            if preprocess_config.get("clear_background", True):
                img = utils.clear_background(img)

        # Segmentation
        segmented = self.segmenter.predict(img)

        # Face detection
        face = None
        if do_facedetect:
            face, _ = self.face_detector.detect(img)

        # OCR on segmented MRZ
        text_results = []
        if segmented is not None:
            ocr_results = self.ocr_reader.readtext(segmented)
            for bbox, text, conf in ocr_results:
                text_results.append((bbox, text, conf))

        return text_results, segmented, face
