import json
import os

with open('config.txt', 'r') as f:
    configOpts = json.load(f)

if configOpts['install_dependancies']:
    # If command isn't found, uses 'pip' instead of 'pip3'
    os.system('pip3 install -r requirements.txt')

import cv2
import mediapipe  # https://google.github.io/mediapipe/solutions/hands.html
import gestureRecog

capture = cv2.VideoCapture(0)

handsDetection = mediapipe.solutions.hands.Hands()
mediapipeDraw = mediapipe.solutions.drawing_utils
gesRecog = gestureRecog.GestureRecognition()

while capture.isOpened():
    ret, img = capture.read()

    if configOpts['greyscale']:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    elif configOpts['rgb']:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    if configOpts['flip']:
        img = cv2.flip(img, 1)

    detectionResults = handsDetection.process(img)

    if detectionResults.multi_hand_landmarks:
        for landmarks in detectionResults.multi_hand_landmarks:
            gesRecog.getHandStatus(gesRecog.formatLandmarks(landmarks))
            mediapipeDraw.draw_landmarks(img, landmarks, mediapipe.solutions.hands.HAND_CONNECTIONS)

    cv2.imshow('window', img)

    if cv2.waitKey(1) == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
