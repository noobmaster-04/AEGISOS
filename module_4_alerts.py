import cv2
import time
import platform
import threading

# Global variable to prevent spamming the sound
last_alert_time = 0
ALERT_COOLDOWN = 5  # Seconds between sound alerts

def play_alert_sound():
    """
    Plays a non-blocking sound.
    Works on Windows (winsound) and Mac/Linux (os.system).
    """
    system_os = platform.system()
    
    try:
        if system_os == "Windows":
            import winsound
            # SND_ASYNC makes it non-blocking (doesn't freeze the video)
            winsound.PlaySound("SystemHand", winsound.SND_ALIAS | winsound.SND_ASYNC)
        elif system_os == "Darwin": # Mac
            import os
            os.system('afplay /System/Library/Sounds/Sosumi.aiff &')
        else: # Linux
            print("\a") # Simple beep
    except Exception as e:
        print(f"Audio Error: {e}")

def process_alerts(frame, emergency_confirmed, confidence_score, posture_state):
    """
    Module 4: Alert Execution & System Feedback
    
    Args:
        frame: The current video frame from Module 1.
        emergency_confirmed (bool): From Module 3.
        confidence_score (float): From Module 3 (0.0 to 1.0).
        posture_state (str): From Module 2 (e.g., "Fall", "Sitting").
        
    Returns:
        frame: The frame with the overlay drawn on it.
    """
    global last_alert_time
    
    # --- 1. VISUAL FEEDBACK (Overlay) ---
    # Define colors (B, G, R)
    COLOR_NORMAL = (0, 255, 0)   # Green
    COLOR_WARN = (0, 255, 255)   # Yellow
    COLOR_ALERT = (0, 0, 255)    # Red
    
    # Determine Status Color & Text
    if emergency_confirmed:
        status_color = COLOR_ALERT
        status_text = "EMERGENCY: COLLAPSE DETECTED"
    elif confidence_score > 0.5:
        status_color = COLOR_WARN
        status_text = "WARNING: UNUSUAL ACTIVITY"
    else:
        status_color = COLOR_NORMAL
        status_text = "SYSTEM NORMAL"

    # Draw Background Box for Text (Top Left)
    cv2.rectangle(frame, (5, 5), (350, 100), (0, 0, 0), -1) # Black box filled
    
    # Text 1: System Status
    cv2.putText(frame, status_text, (15, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, status_color, 2)
    
    # Text 2: Posture State
    cv2.putText(frame, f"Posture: {posture_state}", (15, 60), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)

    # Text 3: Confidence Score
    cv2.putText(frame, f"Confidence: {confidence_score:.2f}", (15, 85), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    # --- 2. AUDIO ALERT (SOS Trigger) ---
    if emergency_confirmed:
        current_time = time.time()
        # Draw a thick red border around the whole screen
        h, w, _ = frame.shape
        cv2.rectangle(frame, (0, 0), (w, h), COLOR_ALERT, 10)
        
        # Play sound if cooldown has passed
        if current_time - last_alert_time > ALERT_COOLDOWN:
            # Run sound in a separate thread so it doesn't lag the video
            threading.Thread(target=play_alert_sound).start()
            last_alert_time = current_time

    return frame