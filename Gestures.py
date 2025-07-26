import cv2
import mediapipe as mp
import time
import subprocess
from datetime import datetime
import numpy as np
from collections import deque

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
hands_detector = mp_hands.Hands(max_num_hands=2, min_detection_confidence=0.7)
cap = cv2.VideoCapture(0)

cooldowns = {
    "spotify": 0,
    "photo": 0,
    "volume": 0,
    "brightness": 0,
    "pauseplay": 0,
}
COOLDOWN_DURATION = 3
COMMANDS = [
    ("Volume Down", "Left",   1, "🔉 Decrease Volume"),
    ("Volume Up",   "Right",  1, "🔊 Increase Volume"),
    ("Brightness Down", "Left", 2, "🔅 Decrease Brightness"),
    ("Brightness Up", "Right", 2, "🔆 Increase Brightness"),
    ("Open Spotify",  "Either", 3, "🎵 Launch Spotify App"),
    ("Play/Pause",  "Either", 4, "⏯️ Toggle Play/Pause"),
    ("Click Photo", "Either", 5, "📸 Take Photo (3-2-1)")
]

def fingers_up(hand_landmarks, handedness_label):
    tips = [4, 8, 12, 16, 20]
    fingers = []

    if handedness_label == "Left":
        # Thumb: left hand — tip x > IP x when up (facing palm to cam)
        fingers.append(1 if hand_landmarks.landmark[tips[0]].x > hand_landmarks.landmark[tips[0] - 1].x else 0)
    else:
        # Thumb: right hand — tip x < IP x when up
        fingers.append(1 if hand_landmarks.landmark[tips[0]].x < hand_landmarks.landmark[tips[0] - 1].x else 0)
    # Other fingers (shared logic)
    for tip in tips[1:]:
        fingers.append(1 if hand_landmarks.landmark[tip].y < hand_landmarks.landmark[tip-2].y else 0)
    return fingers

def capture_photo(frame):
    filename = f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
    cv2.imwrite(filename, frame)
    print(f"✅ Photo saved: {filename}")

def open_spotify():
    subprocess.call(['osascript', '-e', 'tell application "Spotify" to activate'])

def play_pause_spotify():
    subprocess.call(['osascript', '-e', 'tell application "Spotify" to playpause'])

def increase_volume():
    subprocess.call(['osascript', '-e', 'set volume output volume ((output volume of (get volume settings)) + 5)'])

def decrease_volume():
    subprocess.call(['osascript', '-e', 'set volume output volume ((output volume of (get volume settings)) - 5)'])

def increase_brightness():
    subprocess.call(['osascript', '-e', 'tell application "System Events" to key code 144'])

def decrease_brightness():
    subprocess.call(['osascript', '-e', 'tell application "System Events" to key code 145'])

def draw_ui_panel(frame, left_count, right_count, active_command, highlight, calibration_progress=1.0):
    height, width, _ = frame.shape
    panel_width = 430
    panel = np.zeros((height, panel_width, 3), dtype=np.uint8)
    panel[:] = (20, 20, 20)
    y = 35
    cv2.putText(panel, "Gesture Control", (15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.92, (255, 255, 255), 2)
    y += 35
    cv2.putText(panel, f"Left Hand  Fingers: {left_count if left_count is not None else '-'}", (15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (180, 210, 255), 2)
    y += 30
    cv2.putText(panel, f"Right Hand Fingers: {right_count if right_count is not None else '-'}", (15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.72, (255, 180, 180), 2)
    y += 30
    cv2.putText(panel, "Active Command:", (15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.77, (255, 255, 120), 2)
    y += 30
    if active_command:
        col = (80, 240, 100) if highlight else (170, 200, 200)
        cv2.putText(panel, active_command, (39, y), cv2.FONT_HERSHEY_SIMPLEX, 0.80, col, 2)
    else:
        cv2.putText(panel, "None", (39, y), cv2.FONT_HERSHEY_SIMPLEX, 0.80, (200, 200, 210), 2)
    y += 45
    cv2.putText(panel, "Commands:", (15, y), cv2.FONT_HERSHEY_SIMPLEX, 0.70, (255, 220, 140), 2)
    y += 25
    for gesture, hand, fingers, label in COMMANDS:
        display = f"{label}: {hand} | Fingers {fingers}"
        color = (240, 255, 180) if active_command and gesture in active_command else (210, 210, 210)
        cv2.putText(panel, display, (18, y), cv2.FONT_HERSHEY_SIMPLEX, 0.54, color, 1)
        y += 20
    if calibration_progress < 1.0:
        bar_x, bar_y, bar_w, bar_h = 20, height-60, panel_width-40, 22
        cv2.rectangle(panel, (bar_x, bar_y), (bar_x+bar_w, bar_y+bar_h), (90,170,240), 2)
        fill_w = int(bar_w * calibration_progress)
        cv2.rectangle(panel, (bar_x, bar_y), (bar_x+fill_w, bar_y+bar_h), (180,220,255), -1)
        cv2.putText(panel, f"Calibration: {int(calibration_progress*100)}%", (bar_x+5, bar_y+17), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,38,76), 2)
    full_img = np.zeros((height, width + panel_width, 3), dtype=np.uint8)
    full_img[:,:width] = frame
    full_img[:,width:] = panel
    return full_img

calibration_needed_frames = 30
calibration_counter = 0
calibration_positions = []

active_command = None
active_command_timestamp = 0
command_display_duration = 2.5  # seconds

while True:
    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands_detector.process(rgb)

    hand_data = []
    hand_positions = []
    handedness_labels = []
    now = time.time()
    left_count = right_count = None

    if results.multi_hand_landmarks:
        for idx, hand_landmarks in enumerate(results.multi_hand_landmarks):
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            label = results.multi_handedness[idx].classification[0].label  # "Left" or "Right"
            hand_data.append((fingers_up(hand_landmarks, label), hand_landmarks.landmark[0].x, label))

    # Calibration logic
    if calibration_counter < calibration_needed_frames:
        if len(hand_data) == 2:
            calibration_counter += 1
            calibration_positions.append((hand_data[0][1], hand_data[1][1]))
        else:
            calibration_counter = 0
            calibration_positions = []
        prog = float(calibration_counter) / calibration_needed_frames
        ui = draw_ui_panel(frame, None, None, "Calibrating...", False, calibration_progress=prog)
        cv2.putText(ui, "Show BOTH hands steadily...", (50, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
        cv2.imshow("Gesture Control", ui)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        continue

    # Hand assignment by MediaPipe handedness
    left_hand = None
    right_hand = None
    for f, x, label in hand_data:
        if label == "Left":
            left_hand = f
            left_count = sum(f)
        elif label == "Right":
            right_hand = f
            right_count = sum(f)

    new_command = None

    try:
        if left_hand and sum(left_hand) == 1 and now - cooldowns["volume"] > 1:
            decrease_volume()
            new_command = "Volume Down"
            cooldowns["volume"] = now
        elif right_hand and sum(right_hand) == 1 and now - cooldowns["volume"] > 1:
            increase_volume()
            new_command = "Volume Up"
            cooldowns["volume"] = now
        elif left_hand and sum(left_hand) == 2 and now - cooldowns["brightness"] > 1:
            decrease_brightness()
            new_command = "Brightness Down"
            cooldowns["brightness"] = now
        elif right_hand and sum(right_hand) == 2 and now - cooldowns["brightness"] > 1:
            increase_brightness()
            new_command = "Brightness Up"
            cooldowns["brightness"] = now
        elif ((left_hand and sum(left_hand) == 3) or (right_hand and sum(right_hand) == 3)) and now - cooldowns["spotify"] > COOLDOWN_DURATION:
            open_spotify()
            new_command = "Open Spotify"
            cooldowns["spotify"] = now
        elif ((left_hand and sum(left_hand) == 4) or (right_hand and sum(right_hand) == 4)) and now - cooldowns["pauseplay"] > COOLDOWN_DURATION:
            play_pause_spotify()
            new_command = "Play/Pause"
            cooldowns["pauseplay"] = now
        elif ((left_hand and sum(left_hand) == 5) or (right_hand and sum(right_hand) == 5)) and now - cooldowns["photo"] > COOLDOWN_DURATION:
            for i in range(3, 0, -1):
                countdown = frame.copy()
                cv2.putText(countdown, f"📸 Photo in {i}", (60, 130), cv2.FONT_HERSHEY_SIMPLEX,
                            2.1, (0, 0, 255), 7)
                ui = draw_ui_panel(countdown, left_count, right_count, "Click Photo (Countdown)", True, 1.0)
                cv2.imshow("Gesture Control", ui)
                cv2.waitKey(1000)
            capture_photo(frame)
            new_command = "Click Photo"
            cooldowns["photo"] = now
    except Exception as e:
        new_command = f"[HANDLING ERROR] {e}"

    if new_command:
        active_command = new_command
        active_command_timestamp = now
        highlight = True
    elif active_command and now - active_command_timestamp < command_display_duration:
        highlight = True
    else:
        highlight = False
        if now - active_command_timestamp >= command_display_duration:
            active_command = None

    ui = draw_ui_panel(frame, left_count, right_count, active_command, highlight, 1.0)
    cv2.imshow("Gesture Control", ui)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
