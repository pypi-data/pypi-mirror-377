"""
xmrzapp
==========

MRZ Passport Reader From Image.

This package provides utilities for:
- MRZ segmentation (TFLite model)
- Face detection (Caffe model)
- Preprocessing helpers

Example:
--------
>>> from xmrzapp import MRZReader
>>> reader = MRZReader({"lang_list": ["en"], "gpu": False})
>>> text, segmented, face = reader.predict("example.jpg")
"""

from pathlib import Path
import importlib.resources as pkg_resources

from .reader import MRZReader
from .segmentation import SegmentationNetwork, FaceDetection
from . import utils

# Expose default weights directory
weights_dir = Path(pkg_resources.files("xmrzapp") / "weights")

# Default model paths
DEFAULT_FACE_PROTOTXT = str(weights_dir / "face_detector/deploy.prototxt")
DEFAULT_FACE_CAFFEMODEL = str(weights_dir / "face_detector/res10_300x300_ssd_iter_140000.caffemodel")
DEFAULT_SEGMENTATION_MODEL = str(weights_dir / "mrz_detector/mrz_seg.tflite")

__all__ = [
    "MRZReader",
    "SegmentationNetwork",
    "FaceDetection",
    "utils",
    "weights_dir",
    "DEFAULT_FACE_PROTOTXT",
    "DEFAULT_FACE_CAFFEMODEL",
    "DEFAULT_SEGMENTATION_MODEL",
]

# Package version
__version__ = "25.10.9"
