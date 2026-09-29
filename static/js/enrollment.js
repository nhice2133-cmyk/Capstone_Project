/**
 * SMART ENTRY — Face Enrollment JavaScript
 * Three-step enrollment flow:
 *   1. Student info form → POST /admin/enroll/create
 *   2. Auto-capture 20 face images → POST /admin/enroll/capture (per frame)
 *   3. Trigger LBPH training → POST /admin/enroll/train
 */

const TOTAL_IMAGES = 20;
const CAPTURE_INTERVAL_MS = 500;   // ms between captures

// ── DOM refs ─────────────────────────────────────────────────────────────────
const step1       = document.getElementById("step1");
const step2       = document.getElementById("step2");
const step3       = document.getElementById("step3");
const step1Ind    = document.getElementById("step1Indicator");
const step2Ind    = document.getElementById("step2Indicator");
const step3Ind    = document.getElementById("step3Indicator");

const infoForm       = document.getElementById("studentInfoForm");
const fullNameInput  = document.getElementById("fullName");
const studentIdInput = document.getElementById("studentId");
const programInput   = document.getElementById("program");
const infoMessage    = document.getElementById("infoMessage");
const btnSaveInfo    = document.getElementById("btnSaveInfo");

const enrollVideo    = document.getElementById("enrollVideo");
const enrollCanvas   = document.getElementById("enrollCanvas");
const captureCount   = document.getElementById("captureCount");
const captureMsg     = document.getElementById("captureMsg");
const progressFill   = document.getElementById("captureProgressFill");
const btnStart       = document.getElementById("btnStartCapture");
const btnRetake      = document.getElementById("btnRetake");

const previewName = document.getElementById("previewName");
const previewId   = document.getElementById("previewId");
const previewProg = document.getElementById("previewProg");

const trainingAnim   = document.getElementById("trainingAnim");
const trainingResult = document.getElementById("trainingResult");
const btnEnrollAnother = document.getElementById("btnEnrollAnother");
const btnGoStudents  = document.getElementById("btnGoStudents");

let studentDbId  = null;
let captureTimer = null;
let capturedCount = 0;
let stream = null;



// ── Step 1: Save student info ─────────────────────────────────────────────────
infoForm.addEventListener("submit", async (e) => {
  e.preventDefault();
  setMsg(infoMessage, "", "");
  btnSaveInfo.disabled = true;
  btnSaveInfo.textContent = "Saving…";

  const payload = {
    full_name:  fullNameInput.value.trim(),
    student_id: studentIdInput.value.trim(),
    program:    programInput.value.trim(),
  };

  try {
    const res = await fetch("/admin/enroll/create", {
      method: "POST",
      body: new URLSearchParams(payload),
    });
    const data = await res.json();
    if (data.success) {
      studentDbId = data.student_db_id;
      previewName.textContent = payload.full_name;
      previewId.textContent   = payload.student_id;
      previewProg.textContent = payload.program;
      goToStep(2);
      initWebcam();
    } else {
      setMsg(infoMessage, data.message, "error");
    }
  } catch (err) {
    setMsg(infoMessage, "Network error. Please try again.", "error");
  }

  btnSaveInfo.disabled = false;
  btnSaveInfo.textContent = "Save & Proceed to Capture →";
});

// ── Webcam init ───────────────────────────────────────────────────────────────
async function initWebcam() {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
    enrollVideo.srcObject = stream;
    enrollVideo.onloadedmetadata = () => {
      enrollCanvas.width  = enrollVideo.videoWidth;
      enrollCanvas.height = enrollVideo.videoHeight;
    };
  } catch (err) {
    setMsg(captureMsg, "Camera not accessible. Check webcam permissions.", "err");
  }
}

// ── Step 2: Auto-capture ──────────────────────────────────────────────────────
btnStart.addEventListener("click", () => {
  if (!studentDbId) { alert("Please save student info first."); return; }
  capturedCount = 0;
  updateProgress(0);
  setMsg(captureMsg, "Hold still and look at the camera…", "ok");
  btnStart.classList.add("hidden");
  btnRetake.classList.add("hidden");
  captureTimer = setInterval(captureFrame, CAPTURE_INTERVAL_MS);
});

btnRetake.addEventListener("click", () => {
  capturedCount = 0;
  updateProgress(0);
  setMsg(captureMsg, "Ready to capture again.", "ok");
  btnStart.classList.remove("hidden");
  btnRetake.classList.add("hidden");
});

async function captureFrame() {
  const ctx = enrollCanvas.getContext("2d");
  ctx.drawImage(enrollVideo, 0, 0, enrollCanvas.width, enrollCanvas.height);
  const imageData = enrollCanvas.toDataURL("image/jpeg", 0.85);

  try {
    const res = await fetch("/admin/enroll/capture", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ student_db_id: studentDbId, image: imageData, img_index: capturedCount }),
    });
    const data = await res.json();
    if (data.success) {
      capturedCount++;
      updateProgress(capturedCount);
      setMsg(captureMsg, `✅ Image ${capturedCount} of ${TOTAL_IMAGES} saved.`, "ok");

      if (capturedCount >= TOTAL_IMAGES) {
        clearInterval(captureTimer);
        captureTimer = null;
        setMsg(captureMsg, "✅ All images captured! Proceeding to training…", "ok");
        setTimeout(() => goToStep(3), 800);
        setTimeout(trainModel, 1500);
      }
    } else {
      setMsg(captureMsg, `⚠️ ${data.message}`, "err");
    }
  } catch {
    setMsg(captureMsg, "Network error. Retrying…", "err");
  }
}

function updateProgress(count) {
  const pct = (count / TOTAL_IMAGES) * 100;
  progressFill.style.width = pct + "%";
  captureCount.textContent = count;
}

// ── Step 3: Train model ───────────────────────────────────────────────────────
async function trainModel() {
  trainingAnim.classList.remove("hidden");
  trainingResult.classList.add("hidden");
  btnEnrollAnother.classList.add("hidden");
  btnGoStudents.classList.add("hidden");

  // Stop webcam stream
  if (stream) { stream.getTracks().forEach(t => t.stop()); stream = null; }

  try {
    const res = await fetch("/admin/enroll/train", { method: "POST" });
    const data = await res.json();

    trainingAnim.classList.add("hidden");
    trainingResult.classList.remove("hidden");

    if (data.success) {
      trainingResult.className = "training-result ok";
      trainingResult.innerHTML = `<strong>✅ Model trained successfully!</strong><br/>
        <small>${data.num_images} images • ${data.num_subjects} enrolled user(s)</small>`;

      // Hot-reload model in recognition module
      await fetch("/kiosk/reload_model", { method: "POST" });

      step3Ind.classList.add("done");
    } else {
      trainingResult.className = "training-result err";
      trainingResult.innerHTML = `<strong>❌ Training failed</strong><br/><small>${data.message}</small>`;
    }
  } catch {
    trainingAnim.classList.add("hidden");
    trainingResult.classList.remove("hidden");
    trainingResult.className = "training-result err";
    trainingResult.innerHTML = "<strong>❌ Network error during training.</strong>";
  }

  btnEnrollAnother.classList.remove("hidden");
  btnGoStudents.classList.remove("hidden");
}

// ── Helpers ───────────────────────────────────────────────────────────────────
function goToStep(n) {
  [step1, step2, step3].forEach((el, i) => el.classList.toggle("hidden", i !== n - 1));
  [step1Ind, step2Ind, step3Ind].forEach((el, i) => {
    el.classList.toggle("active", i === n - 1);
    if (i < n - 1) el.classList.add("done");
  });
}

function setMsg(el, text, cls) {
  if (!el) return;
  el.textContent = text;
  el.className = cls ? `form-msg ${cls}` : "form-msg";
}
