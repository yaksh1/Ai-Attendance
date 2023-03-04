import cv2
import os
import face_recognition
import pickle
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

# importing students images
imageFolderPath = 'Images'
imgPathList = os.listdir(imageFolderPath)
# for storing student images
imgList = []
# for storing student IDs
studentIDs = []  # we will get it from image names (Id.png)

# --------------------------------------------
# storing student IDs and student images
# --------------------------------------------
for path in imgPathList:
    imgList.append(cv2.imread(os.path.join(imageFolderPath,path)))
    # print(path)
    # --- splitting the path and storing ids in the list ---
    studentIDs.append(os.path.splitext(path)[0])
    
    # sending images to firebase database
    fileName = f'{imageFolderPath}/{path}'
    bucket = storage.bucket()
    blob = bucket.blob(fileName)
    blob.upload_from_filename(fileName )

# finding encodings
def findEncodes(imagesList):
    encodeList = []
    for img in imagesList:
        img = cv2.cvtColor(img,cv2.cv2.COLOR_BGR2RGB)
        encode = face_recognition.face_encodings(img)[0]
        encodeList.append(encode)
    return encodeList

# storings encodings with student IDs
print('encoding started..')
encodings = findEncodes(imgList)
encodingsWithIDs = [encodings,studentIDs]
print('encodings completed')

# dumping the file using pickle
file = open('encodeFile.p','wb')
pickle.dump(encodingsWithIDs,file)
file.close()
print("file saved..")