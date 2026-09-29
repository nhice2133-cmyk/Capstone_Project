# SMART ENTRY
## Face Recognition-Based Attendance & Security Surveillance Kiosk System
### CSUCC Library — Athenaeum

---

## Quick Start

### 1. Prerequisites
- **Python 3.10 or higher**
- **Two USB webcams** (Entry + Exit cameras) — or one webcam for testing
- A PC meeting or exceeding AMD A10-7700K-class performance
- Windows 10/11 (tested) or Linux

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

> **Important:** `opencv-contrib-python` (not `opencv-python`) is required for LBPH face recognition.

### 3. Run the Application

```bash
python app.py
```

The server starts at: `http://localhost:5000`

---

## Access URLs

| URL | Description |
|-----|-------------|
| `http://localhost:5000/kiosk` | Entry Kiosk (full-screen, open in a dedicated browser window) |
| `http://localhost:5000/kiosk/exit` | Exit Monitor (passive departure logging) |
| `http://localhost:5000/admin` | Admin Dashboard |
| `http://localhost:5000/login` | Admin Login |

**Default Admin Credentials:**
- Username: `admin`
- Password: `smart_entry_2026`

> Change the default password after first login!

---

## Project Structure

```
smart_entry/
├── app.py                    # Flask app factory & entry point
├── config.py                 # All configurable parameters
├── requirements.txt          # Python dependencies
├── README.md                 # This file
│
├── database/
│   ├── database.py           # Schema creation & all CRUD helpers
│   └── smart_entry.db        # SQLite database (auto-created on first run)
│
├── recognition/
│   ├── face_detection.py     # Haar Cascade detection wrapper
│   ├── face_recognition.py   # LBPH recognizer wrapper
│   ├── training.py           # LBPH model trainer
│   └── haarcascade/
│       └── haarcascade_frontalface_default.xml
│
├── routes/
│   ├── auth.py               # Admin login / logout
│   ├── students.py           # Student enrollment & management
│   ├── attendance.py         # Attendance logs & CSV export & analytics
│   ├── dashboard.py          # Admin home & live stats
│   └── kiosk.py              # Kiosk stream, recognition API, alerts
│
├── templates/
│   ├── base.html
│   ├── auth/login.html
│   ├── kiosk/kiosk.html      # Full-screen kiosk UI
│   └── admin/                # All admin panel pages
│
├── static/
│   ├── css/main.css, kiosk.css, admin.css
│   ├── js/kiosk.js, enrollment.js, dashboard.js
│   └── snapshots/            # Stranger alert snapshots (auto-created)
│
└── face_data/                # Enrolled face images (auto-created)
    └── <student_db_id>/
        ├── img_000.jpg
        └── img_001.jpg …
```

---

## Configuration (`config.py`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ENTRY_CAMERA_INDEX` | `0` | USB index of the Entry webcam |
| `EXIT_CAMERA_INDEX` | `1` | USB index of the Exit webcam |
| `RECOGNITION_THRESHOLD` | `80` | LBPH confidence threshold (lower = stricter) |
| `ENROLLMENT_IMAGE_COUNT` | `20` | Face images captured per enrollment |
| `ALERT_COOLDOWN_SECONDS` | `10` | Seconds between repeated stranger alerts |
| `SESSION_TIMEOUT_MINUTES` | `30` | Admin session expiry |

---

## Enrollment Workflow

1. Log in to the Admin Panel at `/admin`
2. Navigate to **Enroll Student**
3. **Step 1:** Enter student Full Name, Student ID, and Program
4. **Step 2:** Click **Start Auto-Capture** — the system captures 20 face images automatically
5. **Step 3:** The LBPH model is retrained automatically

---

## System Workflow

### Entry Kiosk
1. Webcam streams continuously
2. Every ~2 seconds a frame is sent to the recognition API
3. If face detected → Haar Cascade crops face → LBPH predicts identity
4. If recognized → student info displayed → Visit Purpose menu shown
5. Student selects purpose → Time In logged to SQLite
6. If unknown → Dashboard alert logged + snapshot saved

### Exit Monitor
1. Webcam streams continuously (passive)
2. If recognized → Time Out logged automatically (no student interaction needed)

---

## Security Notes

- Admin passwords stored using `bcrypt` hashing
- No biometric data is transmitted externally — all data stays on local SQLite
- Stranger snapshots stored locally at `static/snapshots/`
- Session expires after 30 minutes of inactivity

---

## Technology Stack

| Component | Technology |
|-----------|-----------|
| Face Detection | OpenCV Haar Cascade Classifier |
| Face Recognition | LBPH (Local Binary Patterns Histograms) |
| Backend | Python 3.11 + Flask 2.3 |
| Database | SQLite (via sqlite3) |
| Auth | Flask-Login + Flask-Bcrypt |
| Frontend | HTML5 + CSS3 + Vanilla JavaScript |
| Charts | Chart.js 4.4 |
| Webcam | EMEET S600 4K Streaming Webcam (or any USB webcam) |

---

## For the Capstone Manuscript

**Project Title:** SMART ENTRY: Face Recognition-Based Attendance and Security Surveillance Kiosk System for the CSUCC Library

**Institution:** Caraga State University – Cabadbaran Campus (CSUCC)

**Department:** Information Technology

**Algorithms:**
- Face Detection: Haar Cascade Classifier (Viola-Jones)
- Face Recognition: Local Binary Patterns Histograms (LBPH)

**Target Location:** CSUCC Library — Athenaeum

---

*Developed as a BSIT Undergraduate Capstone Project, CSUCC, 2026.*
