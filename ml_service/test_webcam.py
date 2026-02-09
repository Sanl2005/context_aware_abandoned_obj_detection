import cv2
import sys

print("Testing webcam access...")
print("-" * 50)

# Try to open webcam
cap = cv2.VideoCapture(0)

if cap.isOpened():
    print("✅ Webcam opened successfully!")
    
    # Try to read a frame
    ret, frame = cap.read()
    
    if ret:
        print(f"✅ Frame captured successfully!")
        print(f"   Frame shape: {frame.shape}")
        print(f"   Resolution: {frame.shape[1]}x{frame.shape[0]}")
        
        # Save test frame
        cv2.imwrite("test_webcam_frame.jpg", frame)
        print(f"✅ Test frame saved as 'test_webcam_frame.jpg'")
        print("")
        print("🎉 WEBCAM IS WORKING!")
        print("   The ML service should be able to stream video.")
        
    else:
        print("❌ Failed to capture frame from webcam")
        print("   Webcam opened but can't read frames")
        print("   Check if another app is using the camera")
    
    cap.release()
else:
    print("❌ Failed to open webcam!")
    print("   Possible causes:")
    print("   1. No webcam connected")
    print("   2. Webcam is being used by another application")
    print("   3. Permission denied")
    print("   4. Webcam driver issues")

print("-" * 50)
print("Test complete.")
