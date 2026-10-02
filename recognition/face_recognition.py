"""
SMART ENTRY — LBPH Face Recognition Module
Wraps OpenCV's LBPHFaceRecognizer for prediction and label mapping.
"""
import cv2
import os
from config import Config


class FaceRecognizer:
    """
    Loads a pre-trained LBPH model and predicts the identity of a
    cropped, grayscale face region.

    The LBPH model is trained by training.py and saved to
    Config.LBPH_MODEL_PATH. The label → student DB id mapping is
    managed by training.py and must be consistent with the stored model.
    """

    def __init__(self):
        self._recognizer = cv2.face.LBPHFaceRecognizer_create()
        self._model_loaded = False
        self.load_model()

    def load_model(self) -> bool:
        """Load the LBPH model from disk if it exists."""
        if os.path.exists(Config.LBPH_MODEL_PATH):
            self._recognizer.read(Config.LBPH_MODEL_PATH)
            self._model_loaded = True
            return True
        self._model_loaded = False
        return False

    @property
    def is_ready(self) -> bool:
        """True if a trained model is loaded."""
        return self._model_loaded

    def predict(self, face_roi):
        """
        Predict identity for a cropped, 200×200 grayscale face image.

        Returns
        -------
        label : int
            The predicted LBPH label (maps to student DB id via label map).
        confidence : float
            LBPH distance metric. Lower = more confident match.
            Values above Config.RECOGNITION_THRESHOLD are classified as
            unknown / unrecognized.
        """
        if not self._model_loaded:
            return -1, 999.0
        label, confidence = self._recognizer.predict(face_roi)
        return label, confidence

    def is_recognized(self, confidence: float) -> bool:
        """Return True if the confidence value indicates a valid match."""
        return confidence <= Config.RECOGNITION_THRESHOLD
