import json
import time
import math


class GestureRecognition:
    def __init__(self, configuration):
        self.thresholds = {
            "thumbThreshold": 0,
            "fingerThreshold": 0
        }

        self.statusHistory = []

        self.configOpts = configuration

        with open('mapping.json', 'r') as f:
            self.mapping = json.load(f)
            
        for n, _ in enumerate(self.mapping):
            self.mapping[n]['lastTriggered'] = 0

    def setThresholds(self, thresholds) -> None:
        self.thresholds['thumbThreshold'] = (thresholds['thumbBent']+thresholds['thumbStraight'])/2
        self.thresholds['fingerThreshold'] = (thresholds['fingerBent'] + thresholds['fingerStraight']) / 2

    def formatLandmarks(self, landmarks) -> list:
        landmarks = str(landmarks)
        splitLMs = landmarks.split('landmark')[1:]
        strippedLMs = [s.replace('\n', '') for s in splitLMs]

        formattedLandmarks = []

        for landmark in strippedLMs:
            landmark = landmark.replace(' x:', '\"x\":')
            landmark = landmark.replace(' y:', ', \"y\":')
            landmark = landmark.replace(' z:', ', \"z\":')
            formattedLandmarks.append(json.loads(landmark))

        return formattedLandmarks

    def getHandStatus(self, landmarks):
        handStatus = {
            "thumbStatus": self.getThumbStatus(landmarks),
            "thumbPosition": landmarks[3],
            "indexFingerStatus": self.getIndexStatus(landmarks),
            "indexFingerPosition": landmarks[8],
            "middleFingerStatus": self.getMiddleStatus(landmarks),
            "middleFingerPosition": landmarks[12],
            "ringFingerStatus": self.getRingStatus(landmarks),
            "ringFingerPosition": landmarks[16],
            "littleFingerStatus": self.getLittleStatus(landmarks),
            "littleFingerPosition": landmarks[20],
            "wristPosition": landmarks[0]
        }

        self.statusHistory.append(handStatus)

        if len(self.statusHistory) > 3:
            self.statusHistory.pop(0)

    def getThumbStatus(self, landmarks, returnValue=False):
        curveValue = self.lineCurve3d(
            landmarks[2],
            landmarks[3],
            landmarks[4]
        )

        status = self.determineStatusFromCurve(curveValue)

        if not returnValue:
            return status
        else:
            return [curveValue, status]

    def getIndexStatus(self, landmarks, returnValue=False):
        curveValue = self.lineCurve3d(
            landmarks[5],
            landmarks[6],
            landmarks[8]
        )

        status = self.determineStatusFromCurve(curveValue)

        if not returnValue:
            return status
        else:
            return [curveValue, status]

    def getMiddleStatus(self, landmarks):
        curveValue = self.lineCurve3d(
            landmarks[9],
            landmarks[10],
            landmarks[12]
        )

        return self.determineStatusFromCurve(curveValue)

    def getRingStatus(self, landmarks):
        curveValue = self.lineCurve3d(
            landmarks[13],
            landmarks[14],
            landmarks[16]
        )

        return self.determineStatusFromCurve(curveValue)

    def getLittleStatus(self, landmarks):
        curveValue = self.lineCurve3d(
            landmarks[17],
            landmarks[18],
            landmarks[20]
        )

        return self.determineStatusFromCurve(curveValue)

    def lineCurve(self, point1: dict, point2: dict, point3: dict) -> float:
        # https://stackoverflow.com/a/11908158/12671042
        dxc = point2['x'] - point1['x']
        dyc = point2['y'] - point1['y']

        dxl = point3['x'] - point1['x']
        dyl = point3['y'] - point1['y']

        cross = dxc * dyl - dyc * dxl  # The closer to 0, the more straight it is

        return cross

    def lineCurve3d(self, point1: dict, point2: dict, point3: dict) -> float:
        # http://www.ambrsoft.com/TrigoCalc/Line3D/LineColinear.htm
        x1, y1, z1 = point1.values()
        x2, y2, z2 = point2.values()
        x3, y3, z3 = point3.values()

        n1 = ((y2-y1)*(z3-z1))-((y3-y1)*(z2-z1))
        n2 = ((x3-x1)*(z2-z1))-((x2-x1)*(z3-z1))
        n3 = ((x2-x1)*(y3-y1))-((x3-x1)*(y2-y1))

        colinearity = abs(n1)+abs(n2)+abs(n3)  # The closer to 0, the more straight it is

        return colinearity

    def determineStatusFromCurve(self, curveValue: float, isThumb=False) -> str:
        # Lower = straighter
        if isThumb:
            if curveValue <= self.thresholds['thumbThreshold']:
                return 'straight'
            else:
                return 'bent'
        else:
            if curveValue <= self.thresholds['fingerThreshold']:
                return 'straight'
            else:
                return 'bent'

    def getAction(self) -> str:
        if len(self.statusHistory) < 3:
            return ''

        currentTimestamp = time.time()

        for action in self.mapping:
            if currentTimestamp - action['lastTriggered'] < action['maxFrequency']:
                continue

            doAction = True
            
            for triggerPoint in action['points']:
                if not doAction:
                    break

                if 'Status' in triggerPoint:
                    if not (
                        ((self.statusHistory[0][triggerPoint] == action['points'][triggerPoint][0]) or action['points'][triggerPoint][0] == '*') and
                        ((self.statusHistory[1][triggerPoint] == action['points'][triggerPoint][1]) or action['points'][triggerPoint][1] == '*') and
                        ((self.statusHistory[2][triggerPoint] == action['points'][triggerPoint][2]) or action['points'][triggerPoint][2] == '*')
                    ):
                        doAction = False
                elif 'Position' in triggerPoint:
                    distMoved = self.getDist(
                        [self.statusHistory[0][triggerPoint]['x'], self.statusHistory[0][triggerPoint]['y']],
                        [self.statusHistory[2][triggerPoint]['x'], self.statusHistory[2][triggerPoint]['y']]
                    )

                    if distMoved < self.configOpts['movementThreshold']:
                        continue

                    if action['points'][triggerPoint] == 'left':
                        if not (self.statusHistory[0][triggerPoint]['x'] > self.statusHistory[2][triggerPoint]['x']):
                            doAction = False
                    elif action['points'][triggerPoint] == 'right':
                        if not (self.statusHistory[0][triggerPoint]['x'] < self.statusHistory[2][triggerPoint]['x']):
                            doAction = False
                    elif action['points'][triggerPoint] == 'up':
                        if not (self.statusHistory[0][triggerPoint]['y'] < self.statusHistory[2][triggerPoint]['y']):
                            doAction = False
                    elif action['points'][triggerPoint] == 'down':
                        if not (self.statusHistory[0][triggerPoint]['y'] > self.statusHistory[2][triggerPoint]['y']):
                            doAction = False

            if not doAction:
                continue

            action['lastTriggered'] = currentTimestamp
            return action['command']

        return ''

    @staticmethod
    def getDist(point1: list, point2: list, negatives=False):
        if not negatives:
            return math.sqrt((abs(point1[0]-point2[0])**2)+(abs(point1[1]-point2[1])**2))
        else:
            return math.sqrt(((point1[0]-point2[0])**2)+((point1[1]-point2[1])**2))
