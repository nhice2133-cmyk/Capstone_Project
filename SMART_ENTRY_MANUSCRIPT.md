# SMART ENTRY: A Face Recognition-Based Attendance and Security Surveillance Kiosk System Using LBPH Algorithm

---

## Chapter 1: Introduction and Background

### Introduction
The rapid integration of biometric systems into educational and corporate institutions has fundamentally transformed how access control and identity verification are managed. Traditional attendance and security mechanisms, such as manual logbooks, ID cards, and barcode scanners, have proven susceptible to proxy attendance, physical loss, and unauthorized access [1]. In recent years, facial recognition technology has emerged as a robust, non-intrusive alternative, leveraging unique physiological characteristics for seamless identification. The deployment of smart edge-devices and localized computing has further enabled the real-time processing of high-resolution video streams, circumventing the latency and privacy issues associated with cloud-based APIs [2]. By automating the logging process and enhancing spatial security through facial biometrics, institutions can achieve a higher standard of operational efficiency and safety.

### Project Context
At the CSUCC (Caraga State University Cabadbaran City) Library Athenaeum, the daily influx of students, faculty, and visitors presents a continuous logistical challenge for the library personnel. Currently, the library relies on conventional ID scanning or manual logbooks to track time-in and time-out records. This manual process is not only prone to human error and deliberate circumvention but also fails to provide real-time security alerts when an unauthorized individual (a "stranger") enters the premises. Without an automated way to verify if an exiting student actually timed in, data integrity is compromised. This existing problem leads the researchers to propose the development of "SMART ENTRY," a localized, dual-kiosk system that combines automated attendance logging with real-time security surveillance using the Local Binary Pattern Histogram (LBPH) algorithm.

### General and Specific Objectives
**General Objective:**  
To design, develop, and evaluate the "SMART ENTRY" Face Recognition-Based Attendance and Security Surveillance Kiosk System for the CSUCC Library.

**Specific Objectives:**
1. To design a dual-node kiosk interface (Entry and Exit) that provides real-time visual feedback and state management.
2. To develop the core facial recognition engine using Python and OpenCV, specifically utilizing the LBPH algorithm for efficient edge-computing.
3. To integrate an automated security mechanism that captures and logs snapshot alerts when an unrecognized face is detected within the camera's field of view.
4. To evaluate the system's software quality based on the ISO 25010 standard, focusing on Functional Suitability, Usability, and Reliability.

### Scope and Limitation of the Study
**Scope:**  
The project covers the development of a localized, web-based software application featuring an Admin Dashboard and two distinct Kiosk Views (IN and OUT). It encompasses the enrollment of users (students and faculty), automated attendance tracking with anti-spoofing cooldowns, and a security alert dashboard that flags unresolved stranger entries. The facial recognition relies on the OpenCV library's Haar Cascade classifier for face detection and the LBPH algorithm for identification. 

**Limitation:**  
The system's scope is strictly software and webcam-based; it does not include the installation of physical turnstiles or automatic door locks. The recognition accuracy is highly dependent on adequate environmental lighting and direct facial angles. Furthermore, the current iteration of the system does not natively support facial mask detection or thermal scanning. 

### Significance of the Study
This study aligns with **SDG 9: Industry, Innovation, and Infrastructure**, by modernizing institutional infrastructure through the application of localized artificial intelligence and automated data processing. The beneficiaries of this project include:
- **Library Administrators and Security Personnel:** Will benefit from automated, real-time alerts regarding unauthorized entries, drastically reducing the manual labor required for surveillance.
- **Students and Faculty:** Will experience a frictionless, non-intrusive entry and exit process without the need to present physical identification cards.
- **Future Researchers:** Will gain a foundational reference for deploying LBPH-based facial recognition systems in high-traffic, localized environments using web-based frameworks like Flask.

---

## Chapter 2: Review of Related Literature and Studies

### Review of Related Literature (RRL)
Recent advancements in edge computing have shifted the paradigm of biometric authentication from cloud-dependent architectures to localized processing. According to [3], executing facial recognition algorithms on local networks significantly reduces latency and mitigates privacy concerns associated with transmitting biometric data over the internet. Furthermore, studies on the Local Binary Pattern Histogram (LBPH) algorithm highlight its resilience against illumination variations and its computational efficiency on lower-end hardware compared to heavy Convolutional Neural Networks (CNNs) [4]. 
*Takeaway:* The findings on LBPH's computational efficiency strongly support its selection as the primary recognition algorithm for the SMART ENTRY localized kiosk system.

The integration of biometric systems into educational environments has also been shown to improve administrative efficiency. A study by [5] demonstrated that automated attendance systems eliminate proxy attendance and reduce the time spent on manual logging by over 80%. 
*Takeaway:* This validates the core objective of the proposed system in replacing manual logbooks at the CSUCC library.

### Review of Related Systems (RRS)
Commercial biometric attendance systems, such as ZKTeco Time and Attendance terminals, provide robust hardware solutions for enterprise environments. However, these proprietary systems are often rigid, lacking customizable real-time dashboards for specific institutional needs, and require expensive licensing for multi-node setups [6]. 
*Takeaway:* The SMART ENTRY system improves upon this by offering a flexible, software-based web dashboard that can be run on any existing PC hardware with standard USB webcams.

Open-source facial recognition attendance projects built on Python often focus solely on the act of logging attendance, completely ignoring the security surveillance aspect [7]. 
*Takeaway:* SMART ENTRY adapts the open-source OpenCV foundation but significantly expands it by introducing a continuous background surveillance loop that actively flags and captures snapshots of unrecognized individuals.

### Synthesis of the Review
A critical analysis of the gathered literature and existing systems reveals a distinct research gap: while commercial solutions are prohibitively expensive and rigid, open-source academic projects rarely bridge the gap between attendance tracking and active security surveillance. Existing systems treat attendance (identifying known users) and security (flagging unknown users) as separate domains. The proposed SMART ENTRY system fills this gap by utilizing a unified LBPH recognition loop to simultaneously log enrolled users and trigger snapshot alerts for strangers, all operating within a localized, cost-effective hardware environment.

### Theoretical and Conceptual Framework
**Theoretical Framework:**  
This project is anchored on the **Technology Acceptance Model (TAM)**, developed by Fred Davis. TAM posits that user adoption of a new information system is determined by two primary factors: Perceived Usefulness (PU) and Perceived Ease of Use (PEOU) [8]. By utilizing frictionless facial recognition, the system maximizes PEOU, while the automated generation of attendance reports and security alerts maximizes PU for the administrators.

**Conceptual Framework (IPO):**
- **Input:** Live video stream from USB webcams; User enrollment data (Names, IDs, Programs); ISO 25010 Evaluation Questionnaires.
- **Process:** Face detection via Haar Cascades; Feature extraction and matching via LBPH algorithm; Database querying (SQLite3); Data aggregation for the dashboard.
- **Output:** SMART ENTRY web application; Real-time Attendance Logs; Security Alert Snapshots; ISO 25010 Evaluation Results.

### Technical Background
The system is built on a modern, lightweight Python stack. **Flask** serves as the backend web framework, handling routing, API requests, and WebSocket-like continuous video streaming (MJPEG). The database layer is handled by **SQLite3**, offering a serverless, zero-configuration database ideal for local deployments. The core biometric engine relies on **OpenCV**, utilizing the `haarcascade_frontalface_default.xml` for rapid, frame-by-frame face detection, and the `cv2.face.LBPHFaceRecognizer_create()` module for generating histograms of facial textures for identification. The front-end leverages HTML5, Vanilla CSS, and JavaScript for dynamic state management across the kiosk interfaces.

---

## Chapter 3: Methodology

### Research Design
This study employs a **Descriptive-Developmental** research design, which is highly suited for BSIT projects. The developmental phase encompasses the actual engineering, coding, and integration of the SMART ENTRY software and hardware components. The descriptive phase involves gathering quantitative data from end-users and administrators through structured questionnaires to evaluate the system's performance and acceptability based on software quality standards.

### Technical Description / Design / Architecture
**Hardware and Software Requirements:**
- *Hardware:* A central processing PC (Minimum Core i3, 8GB RAM), two standard 1080p USB Webcams (designated for Entry and Exit).
- *Software:* Windows 10/11 OS, Python 3.8+, OpenCV-Contrib-Python, Flask, SQLite3, and a modern web browser (Google Chrome/Edge).

**System Architecture:**
The system operates on a localized Client-Server architecture. The backend server (app.py) runs on the host PC and manages the SQLite database (`smart_entry.db`). The two USB webcams feed directly into the backend's OpenCV processing loop. The client interfaces (Admin Dashboard, Kiosk IN, Kiosk OUT) are rendered via the browser over `localhost`. When a face is detected by the Kiosk IN camera, the backend processes the frame against the `lbph_model.yml` file. If a match is found, data flows to the SQLite database to execute `log_time_in()`.

### Functional and Non-Functional Requirements
**Functional Requirements:**
- The system must allow administrators to enroll new users by capturing at least 20 facial training images.
- The system must accurately distinguish between the Entry and Exit camera streams to log `time_in` and `time_out` respectively.
- The system must capture and save a snapshot when an unrecognized face is detected for more than the designated cooldown period.

**Non-Functional Requirements:**
- The facial recognition matching process must execute in under 2 seconds per frame to ensure a seamless kiosk experience.
- The SQLite database queries must be optimized to prevent locking during simultaneous IN and OUT kiosk access.
- The Admin Dashboard user interface must be responsive and visually accessible.

### Statistical Treatment of Data
To evaluate the success and acceptability of the proposed system, the researchers will utilize the **ISO/IEC 25010 Software Quality Model**. A structured survey questionnaire will be distributed to IT experts and library personnel, focusing on three key characteristics: Functional Suitability, Usability, and Reliability.

The respondents will rate the system using a 5-point Likert Scale:
- 5: Strongly Agree (Excellent)
- 4: Agree (Very Good)
- 3: Neutral (Good)
- 2: Disagree (Fair)
- 1: Strongly Disagree (Poor)

The primary statistical tool utilized will be the **Weighted Mean**, calculated using the formula:
`WM = (Σ f*x) / N`
Where `f` is the frequency of responses, `x` is the weight of the response, and `N` is the total number of respondents. The resulting weighted means will be interpreted using a standard descriptive equivalent scale to determine the system's overall acceptability.

### Project/Research Development Phases
The development of the system strictly followed the **Agile Software Development Life Cycle (SDLC)**, divided into the following iterative phases:
1. **Planning and Requirements Analysis:** Gathering specific operational requirements from the CSUCC Library regarding their attendance tracking and security pain points.
2. **Design Prototyping:** Designing the UI wireframes for the Admin Dashboard and the dual-state Kiosk displays (Idle, Scanning, Success, Error).
3. **Development (Sprint 1 - Biometrics):** Implementing the Python OpenCV core, establishing Haar Cascade detection, and integrating the LBPH training module.
4. **Development (Sprint 2 - Backend Integration):** Linking the facial recognition engine with Flask routes and the SQLite database to track state and handle cooldowns.
5. **Testing and Refinement:** Conducting Alpha testing to calibrate the LBPH confidence thresholds and implement anti-spam cooldowns for the stranger alert snapshots.
6. **Deployment and Evaluation:** Deploying the system on the target hardware for ISO 25010 evaluation by the end-users.

---

## References

[1] M. A. Hossain, M. S. Islam, and M. A. Rahman, "A review on biometric attendance systems: Challenges and future directions," *Journal of Information Security and Applications*, vol. 58, p. 102713, 2021.

[2] J. Chen, X. Ran, and L. Wang, "Edge computing-based facial recognition for smart campus security," *IEEE Access*, vol. 9, pp. 45210-45218, 2021.

[3] S. R. K. V. S. Raju, P. S. S. Prasad, and K. V. S. N. Raju, "An efficient approach for face recognition using LBPH algorithm on edge devices," *International Journal of Cognitive Computing in Engineering*, vol. 2, pp. 134-142, 2021.

[4] D. T. Nguyen, "Comparative analysis of LBPH and CNN for real-time face recognition on resource-constrained hardware," *IEEE Transactions on Biometrics, Behavior, and Identity Science*, vol. 4, no. 2, pp. 210-221, 2022.

[5] A. Kumar and S. Singh, "Automated attendance management system using face recognition: A case study in higher education," *Education and Information Technologies*, vol. 27, no. 3, pp. 3123-3145, 2022.

[6] T. M. Alam *et al.*, "A review of commercial and open-source biometric systems for organizational security," *Computers & Security*, vol. 112, p. 102526, 2022.

[7] P. Sharma, "OpenCV-based real-time face recognition for attendance monitoring," *Journal of Visual Communication and Image Representation*, vol. 82, p. 103399, 2022.

[8] Y. Lee and J. Kim, "Evaluating the adoption of biometric security systems using the Technology Acceptance Model," *International Journal of Human-Computer Interaction*, vol. 38, no. 5, pp. 415-428, 2022.

[9] R. A. Calix, "Integrating ISO 25010 in the evaluation of academic software projects," *IEEE Software*, vol. 39, no. 1, pp. 55-62, 2022.

[10] S. Gupta and A. Sharma, "Anti-spoofing techniques in LBPH-based facial recognition systems," *Pattern Recognition Letters*, vol. 154, pp. 112-118, 2022.
