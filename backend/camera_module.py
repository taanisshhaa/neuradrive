# # import cv2
# # import time
# # import mediapipe as mp
# # import numpy as np
# # import requests

# # # Backend endpoint
# # BACKEND_URL = "http://127.0.0.1:8000/predict"

# # # Initialize Mediapipe
# # mp_face_mesh = mp.solutions.face_mesh
# # face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# # # Define EAR calculation
# # def eye_aspect_ratio(landmarks, eye_indices):
# #     p1 = np.array([landmarks[eye_indices[0]].x, landmarks[eye_indices[0]].y])
# #     p2 = np.array([landmarks[eye_indices[1]].x, landmarks[eye_indices[1]].y])
# #     p3 = np.array([landmarks[eye_indices[2]].x, landmarks[eye_indices[2]].y])
# #     p4 = np.array([landmarks[eye_indices[3]].x, landmarks[eye_indices[3]].y])
# #     p5 = np.array([landmarks[eye_indices[4]].x, landmarks[eye_indices[4]].y])
# #     p6 = np.array([landmarks[eye_indices[5]].x, landmarks[eye_indices[5]].y])

# #     # compute EAR
# #     A = np.linalg.norm(p2 - p6)
# #     B = np.linalg.norm(p3 - p5)
# #     C = np.linalg.norm(p1 - p4)
# #     ear = (A + B) / (2.0 * C)
# #     return ear

# # # Indices for left and right eyes (Mediapipe FaceMesh)
# # LEFT_EYE = [33, 160, 158, 133, 153, 144]
# # RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# # # Capture from webcam
# # cap = cv2.VideoCapture(0)

# # blink_count = 0
# # blink_start = False
# # frame_count = 0
# # send_interval = 3  # seconds

# # last_send_time = time.time()

# # print("🎥 Starting camera... Press 'q' to quit.")

# # while cap.isOpened():
# #     success, frame = cap.read()
# #     if not success:
# #         break

# #     # Flip and convert color
# #     frame = cv2.flip(frame, 1)
# #     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
# #     results = face_mesh.process(rgb_frame)

# #     if results.multi_face_landmarks:
# #         landmarks = results.multi_face_landmarks[0].landmark

# #         left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
# #         right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
# #         ear = (left_ear + right_ear) / 2.0

# #         # Detect blinks
# #         if ear < 0.22 and not blink_start:
# #             blink_start = True
# #         if ear >= 0.25 and blink_start:
# #             blink_count += 1
# #             blink_start = False

# #         # Rough head tilt estimate (using eyes horizontal alignment)
# #         left_eye = np.array([landmarks[33].x, landmarks[33].y])
# #         right_eye = np.array([landmarks[263].x, landmarks[263].y])
# #         dx, dy = right_eye - left_eye
# #         head_tilt = np.degrees(np.arctan2(dy, dx))

# #         # Display EAR and blink info
# #         cv2.putText(frame, f"EAR: {ear:.2f}", (30, 50),
# #                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
# #         cv2.putText(frame, f"Blinks: {blink_count}", (30, 80),
# #                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
# #         cv2.putText(frame, f"Tilt: {head_tilt:.1f}", (30, 110),
# #                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

# #         # Send data to backend every 3 seconds
# #         if time.time() - last_send_time > send_interval:
# #             payload = {
# #                 "eye_ratio": float(ear),
# #                 "blink_count": blink_count,
# #                 "head_tilt": float(head_tilt)
# #             }
# #             try:
# #                 r = requests.post(BACKEND_URL, json=payload, timeout=2)
# #                 if r.ok:
# #                     response = r.json()
# #                     print("🧠 Fatigue:", response)
# #             except Exception as e:
# #                 print("⚠️ Could not send to backend:", e)
# #             last_send_time = time.time()
# #             blink_count = 0  # reset blink counter per window

# #     cv2.imshow("NeuroDrive Camera", frame)
# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break

# # cap.release()
# # cv2.destroyAllWindows()
# import cv2
# import time
# import mediapipe as mp
# import numpy as np
# import requests

# # Backend endpoint
# BACKEND_URL = "http://127.0.0.1:8000/predict"

# # Initialize Mediapipe
# mp_face_mesh = mp.solutions.face_mesh
# face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# # Define EAR calculation
# def eye_aspect_ratio(landmarks, eye_indices):
#     p1 = np.array([landmarks[eye_indices[0]].x, landmarks[eye_indices[0]].y])
#     p2 = np.array([landmarks[eye_indices[1]].x, landmarks[eye_indices[1]].y])
#     p3 = np.array([landmarks[eye_indices[2]].x, landmarks[eye_indices[2]].y])
#     p4 = np.array([landmarks[eye_indices[3]].x, landmarks[eye_indices[3]].y])
#     p5 = np.array([landmarks[eye_indices[4]].x, landmarks[eye_indices[4]].y])
#     p6 = np.array([landmarks[eye_indices[5]].x, landmarks[eye_indices[5]].y])
#     A = np.linalg.norm(p2 - p6)
#     B = np.linalg.norm(p3 - p5)
#     C = np.linalg.norm(p1 - p4)
#     return (A + B) / (2.0 * C)

# # Indices for left and right eyes
# LEFT_EYE = [33, 160, 158, 133, 153, 144]
# RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# # Capture from webcam
# cap = cv2.VideoCapture(0)

# # Blink and timing variables
# blink_count = 0
# blink_start = False
# send_interval = 3  # seconds
# last_send_time = time.time()

# # ---------------- AUTO CALIBRATION ----------------
# print("⚙️ Starting auto calibration...")
# open_ear_values = []
# closed_ear_values = []

# # Step 1: Eyes open
# print("\n➡️ Look straight with eyes OPEN for 5 seconds...")
# start = time.time()
# while time.time() - start < 5:
#     success, frame = cap.read()
#     if not success:
#         continue
#     frame = cv2.flip(frame, 1)
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = face_mesh.process(rgb_frame)
#     if results.multi_face_landmarks:
#         landmarks = results.multi_face_landmarks[0].landmark
#         left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
#         right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
#         ear = (left_ear + right_ear) / 2.0
#         open_ear_values.append(ear)
#         cv2.putText(frame, f"Calibrating (eyes open)...", (30, 50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
#     cv2.imshow("Calibration", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# # Step 2: Eyes closed
# print("\n➡️ Now CLOSE your eyes for 5 seconds...")
# start = time.time()
# while time.time() - start < 5:
#     success, frame = cap.read()
#     if not success:
#         continue
#     frame = cv2.flip(frame, 1)
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = face_mesh.process(rgb_frame)
#     if results.multi_face_landmarks:
#         landmarks = results.multi_face_landmarks[0].landmark
#         left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
#         right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
#         ear = (left_ear + right_ear) / 2.0
#         closed_ear_values.append(ear)
#         cv2.putText(frame, f"Calibrating (eyes closed)...", (30, 50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
#     cv2.imshow("Calibration", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cv2.destroyWindow("Calibration")

# # Compute calibration thresholds
# open_avg = np.mean(open_ear_values) if open_ear_values else 0.3
# closed_avg = np.mean(closed_ear_values) if closed_ear_values else 0.2
# blink_thresh_low = closed_avg + 0.1 * (open_avg - closed_avg)
# blink_thresh_high = open_avg - 0.1 * (open_avg - closed_avg)

# print(f"\n✅ Calibration complete:")
# print(f"   Open EAR:   {open_avg:.3f}")
# print(f"   Closed EAR: {closed_avg:.3f}")
# print(f"   Blink LOW:  {blink_thresh_low:.3f}")
# print(f"   Blink HIGH: {blink_thresh_high:.3f}")

# print("\n🎥 Starting real-time detection... Press 'q' to quit.")

# # ---------------- LIVE DETECTION ----------------
# while cap.isOpened():
#     success, frame = cap.read()
#     if not success:
#         break

#     frame = cv2.flip(frame, 1)
#     rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
#     results = face_mesh.process(rgb_frame)

#     if results.multi_face_landmarks:
#         landmarks = results.multi_face_landmarks[0].landmark

#         left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
#         right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
#         ear = (left_ear + right_ear) / 2.0

#         # Blink detection using calibrated thresholds
#         if ear < blink_thresh_low and not blink_start:
#             blink_start = True
#         if ear >= blink_thresh_high and blink_start:
#             blink_count += 1
#             blink_start = False

#         # Rough head tilt
#         left_eye = np.array([landmarks[33].x, landmarks[33].y])
#         right_eye = np.array([landmarks[263].x, landmarks[263].y])
#         dx, dy = right_eye - left_eye
#         head_tilt = np.degrees(np.arctan2(dy, dx))

#         # Display info
#         cv2.putText(frame, f"EAR: {ear:.2f}", (30, 50),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
#         cv2.putText(frame, f"Blinks: {blink_count}", (30, 80),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
#         cv2.putText(frame, f"Tilt: {head_tilt:.1f}", (30, 110),
#                     cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

#         # Send to backend every few seconds
#         if time.time() - last_send_time > send_interval:
#             payload = {
#                 "eye_ratio": float(ear),
#                 "blink_count": blink_count,
#                 "head_tilt": float(head_tilt)
#             }
#             try:
#                 r = requests.post(BACKEND_URL, json=payload, timeout=2)
#                 if r.ok:
#                     response = r.json()
#                     print("🧠 Fatigue:", response)

#                     # Draw backend status
#                     status = response.get("status", "")
#                     color = (0, 0, 255) if status == "alert" else (0, 255, 0)
#                     cv2.putText(frame, f"STATUS: {status.upper()}",
#                                 (30, 150), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)
#             except Exception as e:
#                 print("⚠️ Could not send to backend:", e)

#             last_send_time = time.time()
#             blink_count = 0

#     cv2.imshow("NeuroDrive Camera", frame)
#     if cv2.waitKey(1) & 0xFF == ord('q'):
#         break

# cap.release()
# cv2.destroyAllWindows()
import cv2
import time
import mediapipe as mp
import numpy as np
import requests
import platform

# Backend endpoint
BACKEND_URL = "http://127.0.0.1:8000/predict"

# Initialize Mediapipe
mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(refine_landmarks=True)

# Define EAR (Eye Aspect Ratio)
def eye_aspect_ratio(landmarks, eye_indices):
    p1 = np.array([landmarks[eye_indices[0]].x, landmarks[eye_indices[0]].y])
    p2 = np.array([landmarks[eye_indices[1]].x, landmarks[eye_indices[1]].y])
    p3 = np.array([landmarks[eye_indices[2]].x, landmarks[eye_indices[2]].y])
    p4 = np.array([landmarks[eye_indices[3]].x, landmarks[eye_indices[3]].y])
    p5 = np.array([landmarks[eye_indices[4]].x, landmarks[eye_indices[4]].y])
    p6 = np.array([landmarks[eye_indices[5]].x, landmarks[eye_indices[5]].y])
    A = np.linalg.norm(p2 - p6)
    B = np.linalg.norm(p3 - p5)
    C = np.linalg.norm(p1 - p4)
    return (A + B) / (2.0 * C)

# Define mouth opening ratio (for yawning)
def mouth_opening_ratio(landmarks):
    top_lip = np.array([landmarks[13].x, landmarks[13].y])
    bottom_lip = np.array([landmarks[14].x, landmarks[14].y])
    left_lip = np.array([landmarks[61].x, landmarks[61].y])
    right_lip = np.array([landmarks[291].x, landmarks[291].y])
    vertical = np.linalg.norm(top_lip - bottom_lip)
    horizontal = np.linalg.norm(left_lip - right_lip)
    return vertical / horizontal

# Eye landmark indices
LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]

# Camera
cap = cv2.VideoCapture(0)
blink_count = 0
blink_start = False
send_interval = 3  # seconds
last_send_time = time.time()
last_alert_time = 0

# ---------- SOUND FUNCTION ----------
def play_alert_sound():
    """Plays a short beep or alert sound depending on OS."""
    try:
        if platform.system() == "Windows":
            import winsound
            winsound.Beep(1000, 600)  # frequency, duration
        else:
            from playsound import playsound
            playsound("alert.wav", block=False)
    except Exception as e:
        print("⚠️ Sound error:", e)

# ---------------- AUTO CALIBRATION ----------------
print("⚙️ Starting auto calibration...")
open_ear_values = []
closed_ear_values = []

# Step 1: Eyes open
print("\n➡️ Look straight with eyes OPEN for 5 seconds...")
start = time.time()
while time.time() - start < 5:
    success, frame = cap.read()
    if not success:
        continue
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
        right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
        ear = (left_ear + right_ear) / 2.0
        open_ear_values.append(ear)
        cv2.putText(frame, f"Calibrating (eyes open)...", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
    cv2.imshow("Calibration", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Step 2: Eyes closed
print("\n➡️ Now CLOSE your eyes for 5 seconds...")
start = time.time()
while time.time() - start < 5:
    success, frame = cap.read()
    if not success:
        continue
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)
    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark
        left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
        right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
        ear = (left_ear + right_ear) / 2.0
        closed_ear_values.append(ear)
        cv2.putText(frame, f"Calibrating (eyes closed)...", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
    cv2.imshow("Calibration", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyWindow("Calibration")

# Compute thresholds
open_avg = np.mean(open_ear_values) if open_ear_values else 0.3
closed_avg = np.mean(closed_ear_values) if closed_ear_values else 0.2
blink_thresh_low = closed_avg + 0.1 * (open_avg - closed_avg)
blink_thresh_high = open_avg - 0.1 * (open_avg - closed_avg)

print(f"\n✅ Calibration complete:")
print(f"   Open EAR:   {open_avg:.3f}")
print(f"   Closed EAR: {closed_avg:.3f}")
print(f"   Blink LOW:  {blink_thresh_low:.3f}")
print(f"   Blink HIGH: {blink_thresh_high:.3f}")
print("\n🎥 Starting real-time detection... Press 'q' to quit.")

# ---------------- LIVE DETECTION ----------------
while cap.isOpened():
    success, frame = cap.read()
    if not success:
        break

    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = face_mesh.process(rgb_frame)

    if results.multi_face_landmarks:
        landmarks = results.multi_face_landmarks[0].landmark

        left_ear = eye_aspect_ratio(landmarks, LEFT_EYE)
        right_ear = eye_aspect_ratio(landmarks, RIGHT_EYE)
        ear = (left_ear + right_ear) / 2.0

        # Blink detection
        if ear < blink_thresh_low and not blink_start:
            blink_start = True
        if ear >= blink_thresh_high and blink_start:
            blink_count += 1
            blink_start = False

        # Head tilt
        left_eye = np.array([landmarks[33].x, landmarks[33].y])
        right_eye = np.array([landmarks[263].x, landmarks[263].y])
        dx, dy = right_eye - left_eye
        head_tilt = np.degrees(np.arctan2(dy, dx))

        # Yawn detection
        mouth_ratio = mouth_opening_ratio(landmarks)
        yawn_detected = mouth_ratio > 0.6

        if yawn_detected:
            cv2.putText(frame, "YAWN DETECTED!", (30, 170),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2)
            # play sound once per yawn
            if time.time() - last_alert_time > 2:
                play_alert_sound()
                last_alert_time = time.time()

        # Display info
        cv2.putText(frame, f"EAR: {ear:.2f}", (30, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Blinks: {blink_count}", (30, 80),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Tilt: {head_tilt:.1f}", (30, 110),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        cv2.putText(frame, f"Mouth: {mouth_ratio:.2f}", (30, 140),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        # Send data to backend
        if time.time() - last_send_time > send_interval:
            payload = {
                "eye_ratio": float(ear),
                "blink_count": blink_count,
                "head_tilt": float(head_tilt),
                "yawn_ratio": float(mouth_ratio)
            }
            try:
                r = requests.post(BACKEND_URL, json=payload, timeout=2)
                if r.ok:
                    response = r.json()
                    print("🧠 Fatigue:", response)

                    # Show backend status
                    status = response.get("status", "")
                    color = (0, 0, 255) if status == "alert" else (0, 255, 0)
                    cv2.putText(frame, f"STATUS: {status.upper()}",
                                (30, 200), cv2.FONT_HERSHEY_SIMPLEX, 0.8, color, 2)

                    # Beep when fatigue = alert
                    if status == "alert" and time.time() - last_alert_time > 2:
                        play_alert_sound()
                        last_alert_time = time.time()

            except Exception as e:
                print("⚠️ Could not send to backend:", e)

            last_send_time = time.time()
            blink_count = 0  # reset

    cv2.imshow("NeuroDrive Camera", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
