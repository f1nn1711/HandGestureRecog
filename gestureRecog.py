import json

class GestureRecognition():
    def __init__(self):
        pass

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
            "thumbPosition": {},
            "indexFingerStatus": self.getIndexStatus(landmarks),
            "indexFingerPosition": {},
            "middleFingerStatus": self.getMiddleStatus(landmarks),
            "middleFingerPosition": {},
            "ringFingerStatus": self.getRingStatus(landmarks),
            "ringFingerPosition": {},
            "littleFingerStatus": self.getLittleStatus(landmarks),
            "littleFingerPosition": {},
            "wristPosition": {}
        }

    def getThumbStatus(self, landmarks, returnValue=False):
        curveValue = self.lineCurve(
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
        curveValue = self.lineCurve(
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
        curveValue = self.lineCurve(
            landmarks[9],
            landmarks[10],
            landmarks[12]
        )

        return self.determineStatusFromCurve(curveValue)

    def getRingStatus(self, landmarks):
        curveValue = self.lineCurve(
            landmarks[13],
            landmarks[14],
            landmarks[16]
        )

        return self.determineStatusFromCurve(curveValue)

    def getLittleStatus(self, landmarks):
        curveValue = self.lineCurve(
            landmarks[17],
            landmarks[18],
            landmarks[20]
        )

        return self.determineStatusFromCurve(curveValue)

    def lineCurve(self, point1: dict, point2: dict, point3: dict) -> float:
        #https://stackoverflow.com/a/11908158/12671042
        dxc = point2['x'] - point1['x']
        dyc = point2['y'] - point1['y']

        dxl = point3['x'] - point1['x']
        dyl = point3['y'] - point1['y']

        cross = dxc * dyl - dyc * dxl  # The closer to 0, the more straight it is

        return cross

    def determineStatusFromCurve(self, curveValue: float) -> str:
        if abs(curveValue) <= 0.0006:
            return 'straight'
        elif abs(curveValue) > 0.008:
            return 'bent'

        '''
        very bent is 0.001
        straight is  0.0003
        '''
