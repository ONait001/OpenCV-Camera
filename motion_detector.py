
def detect_motion(self, sensitivity=5):
    faces, bodies, frame = super().detect_motion(sensitivity)
    if faces or bodies:
        
        return faces, bodies, frame, True
    return faces, bodies, frame, False
