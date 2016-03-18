"""Detects faces from webcam."""
import cv2
import sys
from collections import Counter
from requests import put
import json

# Get user supplied values
cascPath = sys.argv[1]
numFrames = int(sys.argv[2])
cameraIdx = int(sys.argv[3])

countFrames = 0
numObjsCount = []

cap = cv2.VideoCapture(cameraIdx)
url = "http://198.199.119.166/settransit/Z1/"
p1 = (660, 600)
p2 = (220, 220)

# Create the haar cascade
objCascade = cv2.CascadeClassifier(cascPath)


def ccw(A, B, C):
    """intersect helper."""
    return (C[1]-A[1]) * (B[0]-A[0]) > (B[1]-A[1]) * (C[0]-A[0])


# Return true if line segments AB and CD intersect
def intersect(A,B,C,D):
    """"Returns if two lines intersects."""
    return ccw(A,C,D) != ccw(B,C,D) and ccw(A,B,C) != ccw(A,B,D)


def rectIntersectLine(linePoints, rectPoints):
    """Returns if a line intersects a rectangle."""
    diagonal1 = rectPoints
    return intersect(linePoints[0], linePoints[1], rectPoints[0][0], rectPoints[0][1]) or intersect(linePoints[0], linePoints[1], rectPoints[1][0], rectPoints[1][1])

while True:
    countFrames += 1
    ret, frame = cap.read()

    # Read the image
    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Detect faces in the image
    objects = objCascade.detectMultiScale(frame, 1.1, 2)
    # Draw a rectangle around the objects

    validObjects = 0  # The number of objects that intersects the line
    for (x, y, w, h) in objects:
        cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        if rectIntersectLine([p1, p2], [((x,y), (x+w, y+h)), ((x+w,y), (x, y+h))]):
            validObjects += 1

    numObjsCount.append(validObjects)

    cv2.line(frame, p1, p2, 123)
    cv2.imshow("Frame", frame)

    if countFrames >= 10:
        counter = Counter(numObjsCount)
        numObjs = counter.most_common(1)[0][0]
        print(numObjs)
        countFrames = 0
        numObjsCount = []
        put(url + str(numObjs))
        del counter

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()
