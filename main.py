import cv2
import time
import datetime
import threading
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from notifications import send_alert  # email notification function
import winsound  # For alarm sound
import os

# Initialize video capture  
cap = cv2.VideoCapture(0)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
body_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_fullbody.xml")

detection_active = False
detection_stopped_time = None
timer_started = False
SECONDS_TO_RECORD_AFTER_DETECTION = 5
frame_size = (int(cap.get(3)), int(cap.get(4)))
fourcc = cv2.VideoWriter_fourcc(*"mp4v")
out = None
recording_duration = 0
sensitivity = 5  # Default sensitivity
save_directory = os.getcwd()
motion_count = 0  # Track motion detection occurrences

###
class ObjectDetection:
    def detect_objects(self, frame):
        return []  

detection_model = ObjectDetection()

# GUI 
root = tk.Tk()
root.title("Motion Detection Camera")
root.geometry("1000x700")
root.configure(bg="#0F0F0F") 


frame_top = tk.Frame(root, bg="#1C1C1C", bd=2, relief="groove", padx=15, pady=15)
frame_top.pack(fill=tk.X, padx=10, pady=10)

title_label = tk.Label(frame_top, text="Motion Detector", bg="#1C1C1C", fg="white",
                       font=("Helvetica", 28, "bold"))
title_label.pack(pady=(0,15))

# Button 
button_frame = tk.Frame(frame_top, bg="#1C1C1C", bd=2, relief="groove", padx=10, pady=10)
button_frame.pack()

start_button = tk.Button(button_frame, text="Start Detection",
                         command=lambda: threading.Thread(target=start_detection).start(),
                         bg="#154360", fg="white", font=("Helvetica", 12, "bold"),
                         relief="flat", activebackground="#1A5276", padx=10, pady=5)
start_button.grid(row=0, column=0, padx=10)

stop_button = tk.Button(button_frame, text="Stop Detection",
                        command=lambda: threading.Thread(target=stop_detection).start(),
                        bg="#78281F", fg="white", font=("Helvetica", 12, "bold"),
                        relief="flat", activebackground="#943126", padx=10, pady=5)
stop_button.grid(row=0, column=1, padx=10)

save_button = tk.Button(button_frame, text="Set Save Directory",
                        command=lambda: threading.Thread(target=set_save_directory).start(),
                        bg="#7D6608", fg="white", font=("Helvetica", 12, "bold"),
                        relief="flat", activebackground="#B7950B", padx=10, pady=5)
save_button.grid(row=0, column=2, padx=10)

sensitivity_slider = tk.Scale(frame_top, from_=1, to=10, orient=tk.HORIZONTAL,
                              label="Sensitivity", bg="#1C1C1C", fg="white", font=("Helvetica", 10),
                              highlightbackground="#1C1C1C", troughcolor="#424949")
sensitivity_slider.set(sensitivity)
sensitivity_slider.pack(pady=10)

# video display and logs 
frame_bottom = tk.Frame(root, bg="#1C1C1C", bd=2, relief="groove", padx=10, pady=10)
frame_bottom.pack(fill=tk.BOTH, expand=True, padx=10, pady=(0,10))

video_label = tk.Label(frame_bottom, bg="#1C1C1C", bd=2, relief="sunken")
video_label.pack(pady=10)

log_text = tk.Text(frame_bottom, height=10, width=70, bg="#262626", fg="white",
                   font=("Helvetica", 10), relief="flat", bd=2, highlightthickness=1, 
                   highlightbackground="#424949")
log_text.pack(pady=(0,10), padx=10)

scrollbar = tk.Scrollbar(frame_bottom, command=log_text.yview)
scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
log_text.config(yscrollcommand=scrollbar.set)

def update_log(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)

def save_snapshot(frame):
    timestamp = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
    filename = os.path.join(save_directory, f"snapshot_{timestamp}.png")
    cv2.imwrite(filename, frame)
    update_log(f"Snapshot saved: {filename}")

def play_alarm():
    winsound.Beep(1000, 500)  # Beep sound

def set_save_directory():
    global save_directory
    save_directory = filedialog.askdirectory()
    update_log(f"Save directory set to: {save_directory}")

def detect_motion():
    global detection_active, detection_stopped_time, timer_started, out, recording_duration, sensitivity, motion_count
    sensitivity = sensitivity_slider.get()
    
    ret, frame = cap.read()
    if not ret:
        root.after(10, detect_motion)
        return

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = face_cascade.detectMultiScale(gray, 1.3, sensitivity)
    bodies = body_cascade.detectMultiScale(gray, 1.3, sensitivity)
    objects = detection_model.detect_objects(frame)  # Always empty

    if len(faces) + len(bodies) > 0:
        motion_count += 1
        update_log(f"Motion detected! Count: {motion_count}")
        if not detection_active:
            detection_active = True
            timer_started = False
            current_time = datetime.datetime.now().strftime("%d-%m-%Y-%H-%M-%S")
            out = cv2.VideoWriter(os.path.join(save_directory, f"video_{current_time}.mp4"),
                                  fourcc, 20, frame_size)
            update_log("Started recording! (Motion detected)")
            
            save_snapshot(frame)
            threading.Thread(target=play_alarm).start()
            threading.Thread(target=send_alert, args=("Motion detected!",)).start()
            update_log("Email alert sent!")
    elif detection_active:
        if timer_started:
            if time.time() - detection_stopped_time >= SECONDS_TO_RECORD_AFTER_DETECTION:
                detection_active = False
                timer_started = False
                if out is not None:
                    out.release()
                    out = None
                update_log("Stopped recording! (No motion detected)")
        else:
            timer_started = True
            detection_stopped_time = time.time()

    if detection_active and out is not None:
        out.write(frame)
        recording_duration += 1 / 20

    for (x, y, width, height) in faces:
        cv2.rectangle(frame, (x, y), (x + width, y + height), (255, 0, 0), 3)
    for (x, y, width, height) in bodies:
        cv2.rectangle(frame, (x, y), (x + width, y + height), (0, 255, 0), 3)

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    img = ImageTk.PhotoImage(img)
    video_label.config(image=img)
    video_label.image = img

    root.after(10, detect_motion)

def start_detection():
    detect_motion()

def stop_detection():
    cap.release()
    cv2.destroyAllWindows()
    root.quit()

root.mainloop()
