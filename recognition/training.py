"""
SMART ENTRY — LBPH Training Module
Trains the LBPH model from enrolled face images stored under face_data/.

Directory structure expected:
    face_data/
        <student_db_id>/
            img_001.jpg
            img_002.jpg
            ...

Each sub-directory name must be a valid integer matching a student.id
in the database. That integer is used directly as the LBPH label, so
the label → student_db_id mapping is trivial (label == student_db_id).
"""
import cv2
import os
import numpy as np
from config import Config
from recognition.face_detection import FaceDetector


def train_model() -> dict:
    """
    Scan face_data/, extract LBPH features, train the recognizer,
    and save the model to Config.LBPH_MODEL_PATH.

    Returns
    -------
    result : dict
        {
            'success': bool,
            'message': str,
            'num_subjects': int,
            'num_images': int
        }
    """
    detector = FaceDetector()
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    face_data_dir = Config.FACE_DATA_DIR
    if not os.path.exists(face_data_dir):
        return {"success": False, "message": "face_data/ directory not found.",
                "num_subjects": 0, "num_images": 0}

    labels = []
    faces = []
    num_subjects = 0

    for subject_id_str in os.listdir(face_data_dir):
        subject_path = os.path.join(face_data_dir, subject_id_str)
        if not os.path.isdir(subject_path):
            continue
        try:
            label = int(subject_id_str)
        except ValueError:
            continue  # Skip non-integer folder names

        num_subjects += 1
        for img_file in os.listdir(subject_path):
            img_path = os.path.join(subject_path, img_file)
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is None:
                continue
            img_resized = cv2.resize(img, (200, 200))
            faces.append(img_resized)
            labels.append(label)

    if len(faces) < 1:
        return {"success": False,
                "message": "No training images found. Enroll at least one student first.",
                "num_subjects": 0, "num_images": 0}

    recognizer.train(faces, np.array(labels))

    os.makedirs(os.path.dirname(Config.LBPH_MODEL_PATH), exist_ok=True)
    recognizer.save(Config.LBPH_MODEL_PATH)

    return {
        "success": True,
        "message": f"Model trained successfully with {len(faces)} images "
                   f"from {num_subjects} enrolled user(s).",
        "num_subjects": num_subjects,
        "num_images": len(faces),
    }


def get_training_stats() -> dict:
    """Return quick stats about available training data."""
    face_data_dir = Config.FACE_DATA_DIR
    if not os.path.exists(face_data_dir):
        return {"num_subjects": 0, "num_images": 0, "model_exists": False}

    num_subjects = 0
    num_images = 0
    for subject_id_str in os.listdir(face_data_dir):
        subject_path = os.path.join(face_data_dir, subject_id_str)
        if os.path.isdir(subject_path):
            try:
                int(subject_id_str)
                num_subjects += 1
                num_images += len([
                    f for f in os.listdir(subject_path)
                    if f.lower().endswith((".jpg", ".jpeg", ".png"))
                ])
            except ValueError:
                pass

    return {
        "num_subjects": num_subjects,
        "num_images": num_images,
        "model_exists": os.path.exists(Config.LBPH_MODEL_PATH),
    }
