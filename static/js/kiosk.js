/**
 * SMART ENTRY — Kiosk JavaScript
 * Controls the webcam feed, recognition loop, state transitions,
 * and attendance logging for both Entry and Exit modes.
 */

// ── Constants ──────────────────────────────────────────────────────────────
const MODE = typeof KIOSK_MODE !== "undefined" ? KIOSK_MODE : "entry";
const RECOGNITION_INTERVAL_MS = 2000;   // how often to send a frame for recognition
const CONFIRM_DISPLAY_MS       = 4000;  // how long to show confirmed / exit-logged state
const ALERT_DISPLAY_MS         = 5000;  // how long to show the alert state

// ── DOM refs ────────────────────────────────────────────────────────────────
const video    = document.getElementById("webcamVideo");
const canvas   = document.getElementById("webcamCanvas");
const clock    = document.getElementById("kioskClock");

const overlayScanning = document.getElementById("overlayScanning");
const overlaySuccess  = document.getElementById("overlaySuccess");
const overlayAlert    = document.getElementById("overlayAlert");

const stateDefault         = document.getElementById("stateDefault");
const stateIdentifySuccess = document.getElementById("stateIdentifySuccess");
const statePurpose         = document.getElementById("statePurpose");
const stateConfirmed       = document.getElementById("stateConfirmed");
const stateExitLogged      = document.getElementById("stateExitLogged");
const stateExitError       = document.getElementById("stateExitError");
const stateAlert           = document.getElementById("stateAlert");

let transitionTimeout = null;

// ── State machine ───────────────────────────────────────────────────────────
let currentState   = "idle";       // idle | recognized | confirmed | exit_logged | alert
let recognitionLoop = null;
let studentDbId    = null;

// ── Clock ───────────────────────────────────────────────────────────────────
function updateClock() {
  clock.textContent = new Date().toLocaleTimeString("en-PH", {
    hour: "2-digit", minute: "2-digit", second: "2-digit"
  });
}
updateClock();
setInterval(updateClock, 1000);

// ── Webcam init ─────────────────────────────────────────────────────────────
async function initWebcam() {
  try {
    const constraints = {
      video: {
        width:  { ideal: 640 },
        height: { ideal: 480 },
        facingMode: "user"
      }
    };
    const stream = await navigator.mediaDevices.getUserMedia(constraints);
    video.srcObject = stream;
    video.onloadedmetadata = () => {
      canvas.width  = video.videoWidth;
      canvas.height = video.videoHeight;
      startRecognitionLoop();
    };
  } catch (err) {
    console.error("Webcam error:", err);
    showMsg(overlayScanning, "📵 Camera not available.\nCheck webcam connection.");
  }
}

// ── Capture frame as base64 JPEG ────────────────────────────────────────────
function captureFrame() {
  const ctx = canvas.getContext("2d");
  ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
  return canvas.toDataURL("image/jpeg", 0.85);
}

// ── Recognition API call ────────────────────────────────────────────────────
async function runRecognition() {
  if (currentState !== "idle") return;  // Don't interrupt an active state

  const imageData = captureFrame();
  try {
    const res = await fetch("/kiosk/recognize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ image: imageData, camera: MODE }),
    });
    const data = await res.json();
    handleRecognitionResult(data);
  } catch (err) {
    console.warn("Recognition request failed:", err);
  }
}

// ── Result handler ──────────────────────────────────────────────────────────
function handleRecognitionResult(data) {
  if (data.status === "no_face" || data.status === "cooldown") {
    // Remain in idle scanning state
    return;
  }

  if (data.status === "recognized") {
    studentDbId = data.student_db_id;

    if (MODE === "exit") {
      // Log time out automatically
      logExit(data);
    } else {
      // Prompt for visit purpose directly
      promptVisitPurpose(data);
    }
    return;
  }

  if (data.status === "unknown") {
    showAlertState();
  }
}

// ── Entry: prompt for visit purpose ─────────────────────────────────────────
function promptVisitPurpose(data) {
  currentState = "purpose_selection";
  stopRecognitionLoop();

  // Populate student card for purpose screen
  document.getElementById("purposeStudentName").textContent = data.full_name;
  document.getElementById("purposeStudentProg").textContent = data.program;

  // Switch info panel to purpose selection
  switchInfoState(statePurpose);

  // Camera overlay
  document.getElementById("successName").textContent = `✅ ${data.full_name}`;
  switchOverlay(overlaySuccess);
}

// ── Exit: auto log time-out ─────────────────────────────────────────────────
async function logExit(data) {
  currentState = "exit_logged";
  stopRecognitionLoop();

  try {
    const res = await fetch("/kiosk/log_exit", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_db_id: data.student_db_id }),
    });
    const logData = await res.json();
    
    if (logData.success) {
      document.getElementById("exitStudentName").textContent = data.full_name;
      document.getElementById("exitStudentProg").textContent = data.program;
      switchInfoState(stateExitLogged);
      switchOverlay(overlaySuccess);
    } else {
      document.getElementById("exitErrorName").textContent = data.full_name;
      document.getElementById("exitErrorProg").textContent = data.program;
      switchInfoState(stateExitError);
      switchOverlay(null);
    }
  } catch (err) {
    console.warn("Log exit failed:", err);
    // fallback if fetch fails
    document.getElementById("exitStudentName").textContent = data.full_name;
    document.getElementById("exitStudentProg").textContent = data.program;
    switchInfoState(stateExitLogged);
    switchOverlay(overlaySuccess);
  }

  setTimeout(resetToIdle, CONFIRM_DISPLAY_MS);
}

// ── Visit purpose selection ─────────────────────────────────────────────────
const purposeGrid = document.getElementById("purposeGrid");
if (purposeGrid) {
  purposeGrid.addEventListener("click", async (e) => {
    const btn = e.target.closest(".purpose-btn");
    if (!btn || currentState !== "purpose_selection") return;

    const purpose = btn.dataset.purpose;
    // Visual feedback
    purposeGrid.querySelectorAll(".purpose-btn").forEach(b => b.classList.remove("selected"));
    btn.classList.add("selected");

    // Log entry
    try {
      await fetch("/kiosk/log_entry", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ student_db_id: studentDbId, visit_purpose: purpose }),
      });
    } catch (err) {
      console.warn("Log entry failed:", err);
    }

    // Show confirmed
    showConfirmedState(purpose);
  });
}

function showConfirmedState(purpose) {
  currentState = "confirmed";

  const name = document.getElementById("purposeStudentName").textContent;
  document.getElementById("confirmedName").textContent    = name;
  document.getElementById("confirmedPurpose").textContent = purpose;

  switchInfoState(stateConfirmed);
  switchOverlay(null);  // hide overlays

  setTimeout(resetToIdle, CONFIRM_DISPLAY_MS);
}

// ── Alert state ─────────────────────────────────────────────────────────────
function showAlertState() {
  currentState = "alert";
  stopRecognitionLoop();

  switchInfoState(stateAlert);
  switchOverlay(overlayAlert);

  setTimeout(resetToIdle, ALERT_DISPLAY_MS);
}

// ── Reset ───────────────────────────────────────────────────────────────────
function resetToIdle() {
  if (transitionTimeout) clearTimeout(transitionTimeout);
  currentState = "idle";
  studentDbId  = null;

  switchInfoState(stateDefault);
  switchOverlay(overlayScanning);
  purposeGrid && purposeGrid.querySelectorAll(".purpose-btn").forEach(b => b.classList.remove("selected"));

  startRecognitionLoop();
}

// ── Overlay & info panel helpers ─────────────────────────────────────────────
function switchOverlay(target) {
  [overlayScanning, overlaySuccess, overlayAlert].forEach(el => {
    if (el) el.classList.toggle("hidden", el !== target);
  });
}

function switchInfoState(target) {
  [stateDefault, stateIdentifySuccess, statePurpose, stateConfirmed, stateExitLogged, stateExitError, stateAlert].forEach(el => {
    if (el) el.classList.toggle("hidden", el !== target);
  });
}

// ── Recognition loop ────────────────────────────────────────────────────────
function startRecognitionLoop() {
  if (recognitionLoop) return;
  recognitionLoop = setInterval(runRecognition, RECOGNITION_INTERVAL_MS);
}

function stopRecognitionLoop() {
  if (recognitionLoop) {
    clearInterval(recognitionLoop);
    recognitionLoop = null;
  }
}

// ── Boot ─────────────────────────────────────────────────────────────────────
initWebcam();
