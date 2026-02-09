# 🔧 Troubleshooting: Video Feed Not Showing

## Issue Description
The frontend dashboard displays the video feed container, but the video area is completely black and not showing the webcam feed.

## ✅ Quick Checklist

### 1. Is the ML Service Running?
**Check:** Look for a terminal window running `python app.py` from the `ml_service` directory.

**Fix:**
```bash
cd ml_service
python app.py
```

**Expected output:**
```
 * Serving Flask app 'app'
 * Debug mode: on
WARNING: This is a development server. Do not use it in a production deployment.
 * Running on http://127.0.0.1:5000
Press CTRL+C to quit
```

### 2. Test the Video Feed Endpoint

**Method 1: Open in Browser**
- Open your browser to: `http://127.0.0.1:5000/video_feed`
- You should see the webcam feed with bounding boxes

**Method 2: Use the Test Page**
- Open `test_video_feed.html` in your browser (from the project root)
- This page will automatically test:
  - ML Service connectivity
  - Video feed loading
  - Webcam permissions
  - Real-time error logs

**Method 3: Test Status Endpoint**
- Open in browser: `http://127.0.0.1:5000/status`
- You should see: `{"status":"ok","message":"Flask ML Service running"}`

### 3. Check Browser Console for Errors

**How to open console:**
- Press `F12` or right-click → Inspect → Console tab

**Common errors and solutions:**

#### Error: "Failed to load resource: net::ERR_CONNECTION_REFUSED"
**Cause:** ML Service is not running
**Fix:** Start the ML Service (see step 1)

#### Error: "CORS policy: No 'Access-Control-Allow-Origin' header"
**Cause:** flask-cors not installed or not configured
**Fix:**
```bash
cd ml_service
pip install flask-cors
```
Then restart the ML Service.

#### Error: "net::ERR_NETWORK_CHANGED"
**Cause:** Network configuration changed
**Fix:** Reload the page (F5)

#### No error, but video is black
**Possible causes:**
1. Webcam is being used by another application
2. Webcam permissions not granted
3. No webcam connected

### 4. Check Webcam Availability

**Test webcam manually:**
1. Open Camera app on Windows
2. If it works there, another app might be using it
3. Close Camera app and refresh browser

**Grant webcam permissions:**
1. Look for camera icon in browser address bar
2. Click it and select "Always allow"
3. Refresh the page

### 5. Verify Model File Exists

**Check if YOLO model is present:**
```bash
# Should exist in ml_service directory
ls ml_service/yolov8n.pt
```

**If missing:**
- The model will auto-download on first run
- Wait for download to complete (may take 1-2 minutes)
- Check Flask terminal for download progress

### 6. Check for Import Errors

**View Flask terminal for errors:**
Look for:
```
ModuleNotFoundError: No module named 'utils'
ModuleNotFoundError: No module named 'flask_cors'
```

**Fix import errors:**
```bash
cd ml_service
pip install -r requirements.txt
```

### 7. Frontend React App

**Ensure frontend is running:**
```bash
cd frontend_dashboard
npm start
```

**Check React console:**
- F12 → Console
- Look for errors loading the VideoFeed component

### 8. Port Conflicts

**Check if port 5000 is already in use:**
```bash
# Windows
netstat -ano | findstr :5000

# If a process is using port 5000, you can:
# 1. Kill that process
# 2. Or change the port in ml_service/app.py:
#    app.run(debug=True, port=5001)  # Use different port
#    Then update VideoFeed.js to use the new port
```

## 🎯 Step-by-Step Debugging

### Step 1: Test ML Service Directly
```bash
cd ml_service
python app.py
```

Wait for:
```
* Running on http://127.0.0.1:5000
```

### Step 2: Open Test Page
1. Open `test_video_feed.html` in your browser
2. Click "Test ML Service Status"
3. If it says "ML Service is running", proceed
4. If not, check Step 1

### Step 3: Check Video Feed in Test Page
- If video loads in test page → Frontend issue
- If video doesn't load → ML Service issue

### Step 4: Check Webcam Permissions
Click "Check Webcam Access" button in test page
- If granted → Good!
- If denied → Grant permission in browser settings

### Step 5: Refresh React Dashboard
1. Go to `http://localhost:3001`
2. Press `Ctrl+Shift+R` (hard refresh)
3. Video should now appear

## 🔍 Advanced Debugging

### Check Flask Logs

**Look in Flask terminal for:**
```python
127.0.0.1 - - [timestamp] "GET /video_feed HTTP/1.1" 200 -
```

**If you see errors like:**
```
ImportError: cannot import name 'ObjectTracker'
```

Check that `ml_service/utils/object_tracker.py` exists.

### Test Webcam with Python

Create a test script:
```python
import cv2

cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, frame = cap.read()
    if ret:
        print("✅ Webcam is working!")
        cv2.imwrite("test_frame.jpg", frame)
    else:
        print("❌ Failed to read frame")
else:
    print("❌ Failed to open webcam")
cap.release()
```

Run it:
```bash
cd ml_service
python test_webcam.py
```

### Check CORS Configuration

Verify in `ml_service/app.py`:
```python
from flask_cors import CORS
...
CORS(app)  # This must be present
```

### Verify Frontend URL

In `src/components/VideoFeed.js`, check:
```javascript
const VideoFeed = ({ streamUrl = 'http://127.0.0.1:5000/video_feed' }) => {
```

Make sure the port matches where Flask is running.

## 📝 Common Solutions Summary

| Symptom | Solution |
|---------|----------|
| Black video area | Start ML Service: `python ml_service/app.py` |
| Connection refused error | ML Service not running |
| CORS error | Install flask-cors: `pip install flask-cors` |
| Module not found error | Install requirements: `pip install -r requirements.txt` |
| Webcam denied | Grant browser permissions |
| Video works in test page only | Hard refresh React app (Ctrl+Shift+R) |
| Port already in use | Change port or kill conflicting process |

## ✅ Final Verification

### All systems working when:
1. ✅ Flask terminal shows: `Running on http://127.0.0.1:5000`
2. ✅ Test page at `test_video_feed.html` shows video
3. ✅ Status endpoint returns: `{"status":"ok"}`
4. ✅ React app shows video feed at top of dashboard
5. ✅ Bounding boxes appear around detected objects

## 🆘 Still Not Working?

1. Restart all services:
   - Stop Flask (Ctrl+C)
   - Stop React (Ctrl+C)
   - Close all browser tabs
   - Start Flask first, then React
   - Hard refresh browser (Ctrl+Shift+R)

2. Check system requirements:
   - Python 3.7+
   - Node.js 14+
   - Webcam connected
   - Windows/Linux/Mac with webcam drivers

3. Try a different browser:
   - Chrome (recommended)
   - Firefox
   - Edge

4. Check firewall/antivirus:
   - Temporarily disable to test
   - Add exception for localhost ports 5000, 3000, 3001

## 📞 Getting Help

If still not working, gather this information:
- Operating System
- Browser and version
- Error messages from browser console (F12)
- Error messages from Flask terminal
- Output of `test_video_feed.html`
- Screenshot of the issue

---

**Current Status:** ML Service should be running now. Please:
1. Open `test_video_feed.html` in your browser
2. Click "Test ML Service Status"
3. Check if video feed loads
4. Report back what you see!
