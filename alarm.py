# emotion_detector.py
import cv2
import numpy as np
from tensorflow.keras.models import load_model


EMOTION_MODEL = load_model("models/emotion_model.h5")
EMOTIONS = ["Angry","Disgust","Fear","Happy","Sad","Surprise","Neutral"]

def detect_emotion(face_img_gray):
    # resize & normalize
    roi = cv2.resize(face_img_gray, (48, 48)) / 255.0
    roi = np.expand_dims(np.expand_dims(roi, -1), 0)
    preds = EMOTION_MODEL.predict(roi)[0]
    return EMOTIONS[np.argmax(preds)]

