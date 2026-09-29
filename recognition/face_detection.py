"""
SMART ENTRY — Face Detection Module
Wraps OpenCV's Haar Cascade Classifier for real-time face detection.
"""
import cv2
import os
from config import Config


class FaceDetector:
    """
    Detects frontal faces in a grayscale image using the Haar Cascade
    Classifier. Returns bounding boxes for all detected faces.
    """

    def __init__(self):
        if not os.path.exists(Config.HAAR_CASCADE_PATH):
            raise FileNotFoundError(
                f"Haar Cascade XML not found at: {Config.HAAR_CASCADE_PATH}\n"
                "Please place haarcascade_frontalface_default.xml in "
                "recognition/haarcascade/"
            )
        self._classifier = cv2.CascadeClassifier(Config.HAAR_CASCADE_PATH)

    def detect(self, frame):
        """
        Detect faces in a BGR frame (as captured by OpenCV VideoCapture).

        Parameters
        ----------
        frame : np.ndarray
            BGR image frame from the webcam.

        Returns
        -------
        faces : list of (x, y, w, h) tuples
            Bounding boxes for each detected face.
        gray : np.ndarray
            Grayscale version of the input frame (reused by the recognizer).
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # Equalize histogram to improve detection under varying lighting
        gray = cv2.equalizeHist(gray)

        faces = self._classifier.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80),
            flags=cv2.CASCADE_SCALE_IMAGE,
        )
        if len(faces) == 0:
            return [], gray
        return list(faces), gray

    @staticmethod
    def draw_rectangles(frame, faces, color=(0, 255, 0), thickness=2):
        """Draw bounding rectangles on a frame for visualization."""
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x + w, y + h), color, thickness)
        return frame

    @staticmethod
    def crop_face(gray, face_bbox):
        """Crop and resize a face region for the recognizer."""
        x, y, w, h = face_bbox
        face_roi = gray[y : y + h, x : x + w]
        return cv2.resize(face_roi, (200, 200))
