import json
import os

with open('config.json', 'r') as f:
    configOpts = json.load(f)

if configOpts['installDependencies']:
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
calibrationTime = configOpts['calibrationTime']
calibratingStage = 0
calibrationValues = []
calibrationPointsKeys = list(configOpts['digitThresholds'].keys())


def updateConfigFile(configOpts):
    with open('config.json', 'w') as f:
        jsonConfigData = json.dumps(configOpts, indent=4)
        f.write(jsonConfigData)
        f.close()


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
            formattedLandmarks = gesRecog.formatLandmarks(landmarks)

            if not hasCalibrated and configOpts['calibrateThresholds'] and not calibrating:
                print('Starting calibration')
                print(f'Hold {calibrationPointsKeys[calibratingStage]} for {calibrationTime} second(s)')
                calibrating = True
                startTime = time.time()
            elif not configOpts['calibrateThresholds'] and not hasCalibrated:
                hasCalibrated = True
                gesRecog.setThresholds(configOpts['digitThresholds'])

            if calibrating:
                if (time.time() - startTime) <= calibrationTime:
                    if calibratingStage <= 1:
                        calibrationValues.append(gesRecog.getIndexStatus(formattedLandmarks, True)[0])
                    elif calibratingStage <= 3:
                        calibrationValues.append(gesRecog.getThumbStatus(formattedLandmarks, True)[0])
                else:
                    print('finished calibrating digit')

                    configOpts['digitThresholds'][calibrationPointsKeys[calibratingStage]] = sum(
                        calibrationValues) / len(calibrationValues)
                    calibrating = False

                    calibratingStage += 1

                    if calibratingStage == 4:
                        configOpts['calibrateThresholds'] = False
                        updateConfigFile(configOpts)
                        print('----------------------CALIBRATION DONE----------------------')
                        hasCalibrated = True
                        gesRecog.setThresholds(configOpts['digitThresholds'])

            gesRecog.getHandStatus(formattedLandmarks)

            mediapipeDraw.draw_landmarks(img, landmarks, mediapipe.solutions.hands.HAND_CONNECTIONS)

    cv2.imshow('window', img)

    if cv2.waitKey(1) == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
