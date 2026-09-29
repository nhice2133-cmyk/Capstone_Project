"""
SMART ENTRY — Student Management Routes
Face enrollment (capture images + trigger LBPH training) and CRUD.
"""
import os
import cv2
import base64
import numpy as np
from flask import Blueprint, render_template, request, jsonify, redirect, url_for, flash
from flask_login import login_required
from database import database as db
from recognition.training import train_model
from config import Config

students_bp = Blueprint("students", __name__)


# ── Student list & management ─────────────────────────────────────────────────

@students_bp.route("/admin/students")
@login_required
def list_students():
    students = db.get_all_students()
    return render_template("admin/students.html", students=students)


@students_bp.route("/admin/students/delete/<int:student_db_id>", methods=["POST"])
@login_required
def delete_student(student_db_id):
    db.delete_student(student_db_id)
    # Remove face data folder
    face_dir = os.path.join(Config.FACE_DATA_DIR, str(student_db_id))
    if os.path.exists(face_dir):
        import shutil
        shutil.rmtree(face_dir)
    # Retrain without deleted student
    train_model()
    flash("Student deleted and model retrained.", "success")
    return redirect(url_for("students.list_students"))


@students_bp.route("/admin/students/toggle/<int:student_db_id>", methods=["POST"])
@login_required
def toggle_student(student_db_id):
    student = db.get_student_by_db_id(student_db_id)
    if student:
        new_status = "inactive" if student["status"] == "active" else "active"
        db.update_student_status(student_db_id, new_status)
        flash(f"Student status updated to {new_status}.", "success")
    return redirect(url_for("students.list_students"))


# ── Face Enrollment ───────────────────────────────────────────────────────────

@students_bp.route("/admin/enroll", methods=["GET"])
@login_required
def enroll_page():
    return render_template("admin/enrollment.html")


@students_bp.route("/admin/enroll/create", methods=["POST"])
@login_required
def create_student():
    """Step 1: create student record and return the new DB id."""
    full_name = request.form.get("full_name", "").strip()
    student_id = request.form.get("student_id", "").strip()
    program = request.form.get("program", "").strip()

    if not all([full_name, student_id, program]):
        return jsonify({"success": False, "message": "All fields are required."}), 400

    existing = db.get_student_by_student_id(student_id)
    if existing:
        return jsonify({"success": False,
                        "message": f"Student ID {student_id} is already enrolled."}), 409

    new_id = db.create_student(full_name, student_id, program)
    os.makedirs(os.path.join(Config.FACE_DATA_DIR, str(new_id)), exist_ok=True)
    return jsonify({"success": True, "student_db_id": new_id})


@students_bp.route("/admin/enroll/capture", methods=["POST"])
@login_required
def capture_face():
    """
    Step 2: receive a base64-encoded JPEG frame, detect a face,
    save the face crop, and return progress.
    """
    data = request.get_json()
    student_db_id = data.get("student_db_id")
    image_data = data.get("image")  # base64 data URL: "data:image/jpeg;base64,..."
    img_index = data.get("img_index", 0)

    if not image_data or not student_db_id:
        return jsonify({"success": False, "message": "Missing data."}), 400

    # Decode base64 image
    header, encoded = image_data.split(",", 1)
    img_bytes = base64.b64decode(encoded)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    from recognition.face_detection import FaceDetector
    detector = FaceDetector()
    faces, gray = detector.detect(frame)

    if not faces:
        return jsonify({"success": False, "message": "No face detected in frame. Adjust position."})

    face_roi = detector.crop_face(gray, faces[0])
    save_dir = os.path.join(Config.FACE_DATA_DIR, str(student_db_id))
    os.makedirs(save_dir, exist_ok=True)
    img_path = os.path.join(save_dir, f"img_{img_index:03d}.jpg")
    cv2.imwrite(img_path, face_roi)

    return jsonify({"success": True, "saved_path": img_path})


@students_bp.route("/admin/enroll/train", methods=["POST"])
@login_required
def trigger_training():
    """Step 3: train the LBPH model after enrollment images are captured."""
    result = train_model()
    return jsonify(result)
