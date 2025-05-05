# notifications.py
from logger import log_message

def send_alert(message):
    
    log_message(f"[ALERT] {message}")
    


