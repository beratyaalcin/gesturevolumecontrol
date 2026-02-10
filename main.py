import cv2
import mediapipe as mp
import numpy as np
import math
from pycaw.pycaw import AudioUtilities

# --- KALİBRASYON AYARLARI ---
# Parmakların birbirine en yakın (Mute) ve en uzak (Max Ses) olduğu piksel mesafeleri.
# Eğer ses hala hızlı değişiyorsa MAX_DIST değerini 350 veya 400 yapabilirsin.
MIN_DIST = 50  
MAX_DIST = 300 

# --- RENK PALETİ ---
CYAN = (255, 255, 0)
NEON_GREEN = (50, 255, 50)
RED = (50, 50, 255)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)

# --- BAŞLANGIÇ ---
devices = AudioUtilities.GetSpeakers()
volume = devices.EndpointVolume

mp_hands = mp.solutions.hands
hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

while cap.isOpened():
    success, img = cap.read()
    if not success: break
    img = cv2.flip(img, 1)
    imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    results = hands.process(imgRGB)

    volPer = 0
    volBar = 400

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
                cx_mid, cy_mid = (x1 + x2) // 2, (y1 + y2) // 2

                length = math.hypot(x2 - x1, y2 - y1)
                
                # --- DOĞRUSAL (LINEAR) MAPPING ---
                # 1. Ses seviyesi (0.0 - 1.0 arası scalar değer)
                volScalar = np.interp(length, [MIN_DIST, MAX_DIST], [0.0, 1.0])
                # 2. Görsel Bar (400'den 150'ye yükselen bar)
                volBar = np.interp(length, [MIN_DIST, MAX_DIST], [400, 150])
                # 3. Yüzde değeri (0 - 100)
                volPer = np.interp(length, [MIN_DIST, MAX_DIST], [0, 100])

                try:
                    # Scalar metodu sesi barla %100 uyumlu hale getirir
                    volume.SetMasterVolumeLevelScalar(volScalar, None)
                except: pass

                # --- GÖRSELLEŞTİRME ---
                line_color = NEON_GREEN if volPer < 85 else RED
                cv2.line(img, (x1, y1), (x2, y2), line_color, 3)
                cv2.circle(img, (x1, y1), 12, CYAN, cv2.FILLED)
                cv2.circle(img, (x2, y2), 12, CYAN, cv2.FILLED)

                # Parlama efekti
                glow_radius = int(np.interp(length, [MIN_DIST, MAX_DIST], [25, 5]))
                overlay = img.copy()
                cv2.circle(overlay, (cx_mid, cy_mid), glow_radius + 10, line_color, cv2.FILLED)
                img = cv2.addWeighted(overlay, 0.4, img, 0.6, 0)
                cv2.circle(img, (cx_mid, cy_mid), glow_radius, WHITE, cv2.FILLED)

            mp_draw.draw_landmarks(img, handLms, mp_hands.HAND_CONNECTIONS,
                                   mp_draw.DrawingSpec(color=GRAY, thickness=1),
                                   mp_draw.DrawingSpec(color=WHITE, thickness=1))

    # --- UI ÇİZİMİ ---
    cv2.rectangle(img, (50, 150), (85, 400), GRAY, 3)
    bar_color = NEON_GREEN if volPer < 85 else RED
    cv2.rectangle(img, (50, int(volBar)), (85, 400), bar_color, cv2.FILLED)
    cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX, 1, WHITE, 2)
    cv2.putText(img, 'ELLE SES KONTROL ARAYÜZÜ', (50, 50), cv2.FONT_HERSHEY_PLAIN, 2, CYAN, 2)
    cv2.putText(img, '0.3v', (50, 80), cv2.FONT_HERSHEY_PLAIN, 2, CYAN, 2)

    cv2.imshow("Elle Ses Kontrol", img)
    if cv2.waitKey(1) & 0xFF == ord('q'): break

cap.release()
cv2.destroyAllWindows()