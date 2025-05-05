# main.py (excerpt)
from analytics import log_detection
from logger import log_message
import alarm, motion_detector, emotion_detector, notifications


for (x,y,w,h) in faces:
    face_gray = gray[y:y+h, x:x+w]
    name, conf = recognizer.predict(face_gray)
    emotion = emotion_detector.detect_emotion(face_gray)
    # Log & alert
    event = f"{name} ({emotion}) recognized with {int(conf)}"
    log_message(event)
    log_detection(event)
    notifications.send_alert(event)
    alarm.play_alarm()
    # draw on frame:
    cv2.putText(frame, f"{name},{emotion}", (x, y-10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0,255,0), 2)
