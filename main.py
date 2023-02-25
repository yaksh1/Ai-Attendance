# importing libraries
import cv2
import os
import pickle
import numpy as np
import cvzone

import face_recognition

# webcam settings
capture = cv2.VideoCapture(1)
capture.set(3, 640)
capture.set(4, 480)

# background image
bgImg = cv2.imread('Resources/background.png')

# creating modes list to switch between different modes
modesFolderPath = 'Resources/Modes'
modesPathList = os.listdir(modesFolderPath)
modesList = []
for path in modesPathList:
    modesList.append(cv2.imread(os.path.join(modesFolderPath,path)))

# --- load the encoding file --- #
print("loading the encode file...")
file = open('encodeFile.p','rb')
encodingsWithIDs = pickle.load(file)
file.close()
encodings,studentIDs = encodingsWithIDs
# print(studentIDs) to test if IDs are fetched
print("encode file loaded")

while True:
    success, img = capture.read()

    # --- scaling down the image to reduce the computation power required --- #
    imgSmall = cv2.resize(img,(0,0),None,0.25,0.25)
    imgSmall = cv2.cvtColor(imgSmall, cv2.cv2.COLOR_BGR2RGB)

    # finding out encodings in current frame
    faceCurrFrame = face_recognition.face_locations(imgSmall)
    encodeCurrFrame = face_recognition.face_encodings(imgSmall,faceCurrFrame)

    # UI layout
    bgImg[162:162+480,55:55+640] = img
    bgImg[44:44+633,808:808+414] = modesList[0]

    # matching the face with the encodings
    for encodeFace,faceLocation in zip(encodeCurrFrame,faceCurrFrame):
        matches = face_recognition.compare_faces(encodings,encodeFace)
        faceDistance = face_recognition.face_distance(encodings,encodeFace)
        # print('matches: ',matches)
        # print('face Distance: ',faceDistance)

        matchIndex = np.argmin(faceDistance)

        if matches[matchIndex]:
            # print("known face detected")
            # print("Id: ",studentIDs[matchIndex])
            # --- boundry box info --- #
            y1,x2,y2,x1 = faceLocation
            y1,x2,y2,x1= y1 * 4, x2 * 4, y2 * 4, x1 * 4
            bbox = 55+x1,162+y1,x2-x1,y2-y1
            bgImg = cvzone.cornerRect(bgImg,bbox,rt=0)

    # webcam layout
    # cv2.imshow("Webcam", img)

    # background layout
    cv2.imshow("Backgroung image", bgImg)
    cv2.waitKey(1)
