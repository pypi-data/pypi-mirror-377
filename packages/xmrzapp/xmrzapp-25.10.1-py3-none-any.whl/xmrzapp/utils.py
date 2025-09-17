import cv2
import numpy as np
import os


def load_image(path: str) -> np.ndarray:
    """
    Load an image from disk (BGR format).

    Args:
        path (str): Path to image.

    Returns:
        np.ndarray: BGR image.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Image not found: {path}")
    image = cv2.imread(path)
    if image is None:
        raise ValueError(f"Failed to load image: {path}")
    return image


def save_image(path: str, image: np.ndarray):
    """
    Save an image to disk.

    Args:
        path (str): Output path.
        image (np.ndarray): Image to save.
    """
    cv2.imwrite(path, image)


def crop_mrz(image: np.ndarray, mask: np.ndarray) -> np.ndarray | None:
    """
    Crop MRZ region from image using segmentation mask.

    Args:
        image (np.ndarray): Original image.
        mask (np.ndarray): Binary mask (255 for MRZ region).

    Returns:
        np.ndarray | None: Cropped MRZ region, or None if not found.
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return None

    # Get largest contour (assumed MRZ region)
    contour = max(contours, key=cv2.contourArea)
    x, y, w, h = cv2.boundingRect(contour)
    mrz_crop = image[y:y + h, x:x + w]
    return mrz_crop


def crop_faces(image: np.ndarray, boxes: list) -> list:
    """
    Crop faces from image given bounding boxes.

    Args:
        image (np.ndarray): Original BGR image.
        boxes (list): List of bounding boxes [(x1, y1, x2, y2), ...]

    Returns:
        list: List of cropped face images.
    """
    faces = []
    for (x1, y1, x2, y2) in boxes:
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(image.shape[1], x2), min(image.shape[0], y2)
        face = image[y1:y2, x1:x2]
        if face.size > 0:
            faces.append(face)
    return faces


def preprocess_mrz(image: np.ndarray) -> np.ndarray:
    """
    Preprocess MRZ image for OCR:
    - Convert to grayscale
    - Apply thresholding

    Args:
        image (np.ndarray): MRZ cropped image.

    Returns:
        np.ndarray: Preprocessed image.
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return binary


def clean_text(text: str) -> str:
    """
    Clean MRZ text output by removing invalid characters.

    Args:
        text (str): Raw OCR text.

    Returns:
        str: Cleaned MRZ text.
    """
    allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789<"
    return "".join([c if c in allowed_chars else "" for c in text])
