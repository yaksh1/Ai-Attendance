# importing libraries
import cv2
import os
import pickle
import numpy as np
import cvzone
import face_recognition
import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import db
from firebase_admin import storage

# firebase creds
cred = credentials.Certificate("key.json")
firebase_admin.initialize_app(cred,{
  "databaseURL":'https://classcapture-1362b-default-rtdb.firebaseio.com/',
  "storageBucket":'classcapture-1362b.appspot.com'
})

bucket = storage.bucket()

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

#  variables
modeType = 0
frameCounter = 0
imgStudent =[]
# process
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
    bgImg[44:44+633,808:808+414] = modesList[modeType]

    # if face in frame
    if faceCurrFrame:
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
                # get id
                id = studentIDs[matchIndex]
                if frameCounter == 0:
                    frameCounter = 1
                    modeType=1
            
            if frameCounter!=0:
                if frameCounter==1:
                    # get students data
                    studentInfo = db.reference(f'Students/{id}').get()
                    print(studentInfo)
                    
                    # get image from storage
                    blob = bucket.get_blob(f'Images/{id}.png')
                    array = np.frombuffer(blob.download_as_string(),np.uint8)
                    imgStudent = cv2.imdecode(array,cv2.COLOR_BGRA2BGR)
                    
                    # update student attendance
                    dateTimeObj = datetime.strptime(studentInfo['last_attendance_time'],"%Y-%m-%d %H:%M:%S")
                    secondsElapsed = (datetime.now() - dateTimeObj).total_seconds()
                    print(secondsElapsed)
                    
                    if secondsElapsed>30: # change 30 secs to whichever hours you want the student attendance to update
                        ref =db.reference(f'Students/{id}')
                        studentInfo['total_attendance']+=1
                        ref.child('total_attendance').set(studentInfo['total_attendance'])
                        ref.child('last_attendance_time').set(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
                    else:
                        modeType=3
                        counter =0
                        bgImg[44:44+633,808:808+414] = modesList[modeType]

                
                
                # only do when mode type != 3
                if modeType!=3:
                    # marked frame image
                    if 10<frameCounter<20:
                        modeType=2
                        bgImg[44:44+633,808:808+414] = modesList[modeType]
                    
                    # student data image
                    if frameCounter<=10:
                        # add total attendance on bg image
                        cv2.putText(bgImg,str(studentInfo['total_attendance']),(861,125),cv2.FONT_HERSHEY_COMPLEX,1,(255,255,255),1)
                        # add program on bg image
                        cv2.putText(bgImg,str(studentInfo['program']),(1006,550),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                        # add id on bg image
                        cv2.putText(bgImg,str(id),(1006,493),cv2.FONT_HERSHEY_COMPLEX,0.5,(255,255,255),1)
                        # add year on bg image
                        cv2.putText(bgImg,str(studentInfo['year']),(1025,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                        # add starting_year on bg image
                        cv2.putText(bgImg,str(studentInfo['starting_year']),(1125,625),cv2.FONT_HERSHEY_COMPLEX,0.6,(100,100,100),1)
                        
                        # adjusting name to be centered
                        (w,h),_ = cv2.getTextSize(studentInfo['name'],cv2.FONT_HERSHEY_COMPLEX,1,1)
                        offset = (414 - w)//2
                        # add name on bg image
                        cv2.putText(bgImg,str(studentInfo['name']),(808+offset,445),cv2.FONT_HERSHEY_COMPLEX,1,(50,50,50),1)
                        # add image on bg image
                        bgImg[175:175:212,909:909+216]=imgStudent
                    
                    frameCounter+=1
                    
                    # to reset the counter and mode
                    if frameCounter>=20:
                        frameCounter=0
                        modeType=0
                        studentInfo=[]
                        imgStudent =[]
                        bgImg[44:44+633,808:808+414] = modesList[modeType]
                
    else:
        modeType=0
        counter =0
            
            
    # webcam layout
    # cv2.imshow("Webcam", img)

    # background layout
    cv2.imshow("Backgroung image", bgImg)
    cv2.waitKey(1)
