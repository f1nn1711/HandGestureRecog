#pip install -r requirements.txt
#or
#pip3 install -r requirements.txt
import cv2
import mediapipe
import json

#WIP
def recogniseGesture(landmarkPoints: str) -> str:
    splitLMs = landmarkPoints.split('landmark')[1:]
    formattedLMs = [dict(s.strip()) for s in splitLMs]
    pass

with open('config.txt', 'r') as f:
    configOpts = json.load(f)

capture = cv2.VideoCapture(0)

handsDetection = mediapipe.solutions.hands.Hands()
mediapipeDraw = mediapipe.solutions.drawing_utils

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
            recogniseGesture(str(landmarks))
            mediapipeDraw.draw_landmarks(img, landmarks, mediapipe.solutions.hands.HAND_CONNECTIONS)

    cv2.imshow('window', img)

    if cv2.waitKey(1) == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
