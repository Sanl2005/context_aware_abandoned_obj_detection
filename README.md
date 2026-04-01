# Context-Aware Abandoned Object Intelligence System

🚨 **SentinelEye** - Real-time video monitoring with AI-powered object detection and abandonment alerts.

This system monitors video feeds to detect unattended objects and gradually estimates risk based on time, interaction, and context. It uses YOLOv8 for detection, Flask for processing, Ruby on Rails for API and persistence, and React for the dashboard.

---

## 🛠 Prerequisites

Before starting, ensure you have the following installed on your system (Windows, macOS, or Linux):

1.  **Python 3.9 - 3.11+**: Required for the ML Service.
2.  **Node.js (v16+)**: Required for the React Frontend.
3.  **Ruby (3.x)** and **Rails (7.x)**: Required for the backend API.
4.  **PostgreSQL**: Database for storing alerts and events.
5.  **Redis**: Required by Rails ActionCable for WebSockets (Live data).
6.  *(Optional but recommended)* **NVIDIA GPU** with CUDA support for real-time video processing.

---

## 💻 Setup Instructions (For Any System)

Follow these steps to configure and run the project locally.

### 1. Database & Services Setup
Make sure your PostgreSQL and Redis servers are running. Create the databases for Rails:
```bash
cd rails_backend
bundle install
rails db:create db:migrate
```

### 2. ML Service Setup (Python)
The ML service runs the YOLO model and processes the video frame by frame.
```bash
cd ml_service

# Create a virtual environment
python -m venv venv

# Activate it
# On Windows:
venv\Scripts\activate
# On Linux / macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Frontend Dashboard Setup (React)
The frontend is built with React.
```bash
cd frontend_dashboard
npm install
```

---

## 🚀 Running the Application

You need to run all three components simultaneously for the system to fully function.

### Method A: Quick Start (Windows Only)
On Windows, you can simply run the provided batch script which launches Redis, Rails, the ML Service, and the Frontend in separate windows:
```cmd
start_all.bat
```

### Method B: Manual Start (Mac / Linux / Windows)
Open three separate terminal windows/tabs:

**Terminal 1: Start Rails Backend**
```bash
cd rails_backend
rails server -p 3001
```

**Terminal 2: Start ML Service**
```bash
cd ml_service
# Make sure your virtual environment is active!
python app.py
```

**Terminal 3: Start Node Frontend**
```bash
cd frontend_dashboard
npm start
```

Once everything is running, open your web browser and go to `http://localhost:3000`.

---

## 🔐 Dashboard Authentication

The dashboard is protected. You must log in to view the live feed and archives.

**Demo Credentials:**
- **Username**: `admin`
- **Password**: `admin123`

---

## ✨ System Architecture

- **ML Service (Python/Flask)**: Handles real-time object detection using Ultralytics YOLOv8. Tracks object abandonment, captures images of alerts, and handles SOS notifications (Email/SMS).
- **Rails Backend (Ruby on Rails)**: Serves as the central API, manages persistent storage using ActiveStorage (for images) and PostgreSQL, and handles real-time broadcasting via ActionCable.
- **Frontend Dashboard (React)**: Provides a cyber-security surveillance styled UI for viewing live feeds, archived alerts, and managing historical data.

---

## 📚 Documentation

For more in-depth technical details, check out:
- [PROJECT_DOCUMENTATION.md](PROJECT_DOCUMENTATION.md) - System overview and architecture details
- [AUTHENTICATION_GUIDE.md](AUTHENTICATION_GUIDE.md) - Authentication system details
- [ARCHITECTURE.md](ARCHITECTURE.md) - Detailed component relationships

---

## 📝 License

This project is for educational and surveillance demonstration purposes.
