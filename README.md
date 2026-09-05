# Swimming Pool Safety AI (Proof of Concept)

A real-time, web-based computer vision prototype for monitoring swimming pool occupancy, depth boundary crossings, and safety risk assessment. The system leverages YOLOv8 person detection on the backend and projects detected swimmers onto horizontal pool safety zones (Shallow, Medium, and Deep).

---

## 🏗️ Project Architecture

The workspace is organized into a clean client-server architecture:

```text
swimmingpool/
│
├── frontend/           # Vite + React 2-Page Surveillance Dashboard
│   ├── src/
│   │   ├── context/    # Shared AnalysisContext state
│   │   ├── layouts/    # Simplified MainLayout navigation frame
│   │   ├── pages/      # Monitoring and TestUpload pages
│   │   └── services/   # Axios API client config
│   
├── backend/            # Express Node.js REST API Server
│   ├── config/         # MongoDB initialization config (graceful offline fallback)
│   ├── routes/         # Health routes
│   ├── services/       # Python YOLO script wrapper
│   └── uploads/        # Storage for uploaded and processed media files
│
├── requirements.txt    # Python library requirements
└── README.md           # Setup and Run Guide
```

---

## 💻 Tech Stack Summary

### Frontend (`frontend/`)
* **Framework:** React + Vite (JS)
* **Styling:** Tailwind CSS (surveillance control-room theme)
* **Routing:** React Router v6
* **HTTP requests:** Axios Central API Config
* **Visual Icons:** Lucide React
* **Warnings/Toasts:** React Hot Toast

### Backend (`backend/`)
* **Runtime:** Node.js + Express
* **Database Driver:** Mongoose (MongoDB Connection with graceful offline fallbacks)
* **Image/Video Upload:** Multer
* **AI Analysis:** Python Child-Process execution (OpenCV + Ultralytics YOLOv8)
* **Dev Reloading:** Nodemon

---

## ⚠️ Proof of Concept Features

This release is a **2-page proof of concept** focusing on YOLOv8 verification and zone classification:
1. **Can YOLO detect people in swimming pool CCTV footage?** (Tested using static images and short video clips).
2. **Can we determine which zone each person is in?** (Categorizes location horizontally based on the swimmer's **bottom-center point**).

### Page 1 — MONITORING (`/monitoring`)
* **Mode A — CCTV / Analysed Video**: Plays the processed MP4 video or displays the analysed image returned by the backend. All YOLO bounding boxes, confidence, ID tags, and zone dividers are pre-rendered directly on the media using OpenCV to ensure smooth, high-fidelity playback.
* **Mode B — Pool Visualization**: Shows a CSS-drawn pool diagram with 3 vertical zones (Zone 1: Shallow, Zone 2: Medium, Zone 3: Deep) as a fallback when no active analysis is loaded.
* **Sidebar telemetry**: Displays the count of occupants detected, individual zone occupancy counts, and the overall status representing the highest-risk occupied zone (SAFE for Zone 1, WARNING for Zone 2, CRITICAL for Zone 3).

### Page 2 — UPLOAD & TEST (`/test`)
* **Video Testing**: Select a video (`.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`) up to 5 GB. The backend processes the video in the background, drawing the overlay results on sampled frames, saving a time-lapse summary, and reporting real-time progress to the UI.
* **Image Testing**: Select an image (`.jpg`, `.jpeg`, `.png`, `.webp`) and perform a single YOLOv8 person scan. Returns the annotated image and stats instantly.

---

## 🚀 How to Run the Applications

Ensure you have **Node.js** (v18+), **npm**, and **Python 3.10+** (with `ultralytics`, `opencv-python`, and `numpy` installed) on your workstation.

### Step 1: Run the Backend Server
Open a terminal in the project root:
```bash
cd backend
npm install
npm run dev
```
The server starts on [http://localhost:5000](http://localhost:5000). 
* Health check: [http://localhost:5000/api/health](http://localhost:5000/api/health)

> [!NOTE]
> On the very first image/video analysis run, YOLOv8 will download the lightweight `yolov8n.pt` model weights (~6.2 MB) automatically. Make sure you are online.

### Step 2: Run the Frontend Client
Open a second terminal window/tab:
```bash
cd frontend
npm install
npm run dev
```
The Vite development server starts on [http://localhost:5173](http://localhost:5173). Open this link in your browser to view the application.

---

## ⚙️ Large CCTV Video Uploads & Processing Configuration

This prototype is built to handle large CCTV recordings (e.g. 277 MB, 1.8 GB, up to 5 GB) and long durations (e.g., 30 minutes, 1 hour, 2 hours+).

### Capabilities
* **Maximum Upload Size:** 5 GB (configurable via environment variables)
* **Supported Video Formats:** `.mp4`, `.mov`, `.avi`, `.mkv`, `.webm`
* **Upload Method:** Disk-based multipart upload (saves files to disk instead of memory to prevent crash loops)
* **AI Processing:** Background analysis running frame-by-frame with a configurable sampling stride
* **Telemetry:** Displays real-time upload percentage, frames processed, people detected, and overall analysis progress

### Configuration Environment Variables

#### Backend Configuration (`backend/.env`)
* `MAX_UPLOAD_SIZE_GB`: Sets the maximum allowed file upload size. Defaults to `5`.
* `PROCESS_EVERY_N_FRAMES`: Configures frame sampling. E.g., `30` will process 1 frame out of every 30 frames (ideal for long CCTV videos, as it reduces processing time and disk space).
* `PROCESS_FPS`: Alternately configure sampling rate (e.g., 1 frame per second).

#### Frontend Configuration (`frontend/.env`)
* `VITE_MAX_UPLOAD_SIZE_GB`: Sets the client-side validation threshold. Defaults to `5`.

### 🌐 Nginx / Reverse Proxy Support

If deploying this application behind Nginx or another reverse proxy, you must adjust the maximum allowed request body size to handle large files. Add the following rule to your Nginx site configuration block:

```nginx
client_max_body_size 5G;
```

