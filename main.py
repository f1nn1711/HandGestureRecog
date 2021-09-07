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
import time

capture = cv2.VideoCapture(0)

handsDetection = mediapipe.solutions.hands.Hands()
mediapipeDraw = mediapipe.solutions.drawing_utils
gesRecog = gestureRecog.GestureRecognition()

hasCalibrated = False
calibrating = False
startTime = 0
endTime = 0
calibratingStage = 0
calibrationValues = []

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
            if not hasCalibrated and configOpts['calibrateThresholds'] == 'true':
                print('Starting validation')
                print(f'Hold {configOpts["digitThresholds"][calibratingStage]} for 5 seconds')
                calibrating = True
                startTime = time.time()

            if calibrating:
                if (time.time() - startTime) <= 5:
                    pass
                    #get the value from the class
                    #add it to the array
                
                #add else for when it has been more than 5 seconds
                #calculate avg of values, abs it, set it on the config
                #update the stage

            gesRecog.getHandStatus(gesRecog.formatLandmarks(landmarks))

            mediapipeDraw.draw_landmarks(img, landmarks, mediapipe.solutions.hands.HAND_CONNECTIONS)

    cv2.imshow('window', img)

    if cv2.waitKey(1) == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
