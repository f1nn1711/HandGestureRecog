#pip install -r requirements.txt
#or
#pip3 install -r requirements.txt
import cv2
import json

with open('config.txt', 'r') as f:
    configOpts = json.load(f)

capture = cv2.VideoCapture(0)

while capture.isOpened():
    ret, img = capture.read()

    if configOpts['greyscale']:
        img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    if configOpts['flip']:
        img = cv2.flip(img, 1)

    cv2.imshow('window', img)

    if cv2.waitKey(1) == ord('q'):
        break

capture.release()
cv2.destroyAllWindows()
