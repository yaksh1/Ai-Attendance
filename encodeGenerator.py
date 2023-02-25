import cv2
import os
import face_recognition
import pickle

# importing students images
folderPath = 'Images'
imgPathList = os.listdir(folderPath)
# for storing student images
imgList = []
# for storing student IDs
studentIDs = []  # we will get it from image names (Id.png)

# --------------------------------------------
# storing student IDs and student images
# --------------------------------------------
for path in imgPathList:
    imgList.append(cv2.imread(os.path.join(folderPath,path)))
    # print(path)
    # --- splitting the path and storing ids in the list ---
    studentIDs.append(os.path.splitext(path)[0])

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
print("file saved  ")