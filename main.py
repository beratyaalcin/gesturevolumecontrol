import cv2
import mediapipe as mp
import numpy as np
import math
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# --- 1. GLOBAL DEĞİŞKENLER ---
minVol, maxVol = -65.25, 0.0
audio_active = False
volume = None

# --- 2. SES MOTORU BAŞLATMA (Triple-Check) ---
print("Ses motoruna bağlanılıyor...")
try:
    devices = AudioUtilities.GetSpeakers()
    # Yol A: Standart Aktivasyon
    try:
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
    except:
        # Yol B: Eğer 'devices' bir listeyse ilk elemanı dene
        try:
            interface = devices[0].Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        except:
            # Yol C: 'device' özniteliği üzerinden dene
            interface = devices.device.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
            
    volume = cast(interface, POINTER(IAudioEndpointVolume))
    volRange = volume.GetVolumeRange()
    minVol, maxVol = volRange[0], volRange[1]
    audio_active = True
    print("✅ Ses motoru BAŞARIYLA bağlandı!")
except Exception as e:
    print(f"❌ SES HATASI: {e}")
    print("Program görsel modda çalışıyor...")

# --- 3. MEDIAPIPE ---
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

while cap.isOpened():
    success, img = cap.read()
    if not success: break
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    if results.multi_hand_landmarks:
        for handLms in results.multi_hand_landmarks:
            lmList = []
            for id, lm in enumerate(handLms.landmark):
                h, w, _ = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append([id, cx, cy])

            if len(lmList) >= 9:
                x1, y1 = lmList[4][1], lmList[4][2]
                x2, y2 = lmList[8][1], lmList[8][2]
                length = math.hypot(x2 - x1, y2 - y1)
                
                if audio_active and volume:
                    try:
                        vol = np.interp(length, [30, 200], [minVol, maxVol])
                        volume.SetMasterVolumeLevel(vol, None)
                    except: pass

                cv2.line(img, (x1, y1), (x2, y2), (0, 255, 0), 3)
                cv2.circle(img, (x1, y1), 10, (255, 0, 0), cv2.FILLED)
                cv2.circle(img, (x2, y2), 10, (255, 0, 0), cv2.FILLED)

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS)

    cv2.imshow("BAIBU Gesture Control - Final Fix", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()