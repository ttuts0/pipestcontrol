import cv2
import os
from picamera2 import Picamera2
import time
   
# find user and stores name in users list
users  = []
users.append(os.getlogin())

#reads the "coco.names" file consisting objects that the coco model can detect and stores names into classNames list
classNames = []
classFile = "/home/" + users[0] + "/Desktop/pipestcontrol/Object_Detection_Files/coco.names" 
with open(classFile,"rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

#defines paths to create detection model: modelPath: binary file containing trained weights(increase or decrease a specific amount of information to detect an object) and configPath:   
configPath = "/home/"+ users[0] + "/Desktop/pipestcontrol/Object_Detection_Files/ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
modelPath = "/home/"+ users[0] + "/Desktop/pipestcontrol/Object_Detection_Files/frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(modelPath,configPath) #sets up object detection model with paths provided
net.setInputSize(320,320) #resizes input image 320x320 pixels
net.setInputScale(1.0/ 127.5) #
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True) #swaps red and blue as OpenCV uses BGR by default

def getObjects(img, thres, nms, draw=True, objects=[]):
    """
    Set up what the drawn box size/colour is and the font/size/colour of the name tag and confidence label
    
    Parameters:
    img: the input image
    thres(float): threshold used to filter boxes by confidence(if detection model is not above this float, the detection will not show)
    nms(float): threshold used in non maximum suppression(eliminates duplicate detections)
    draw: draws rectangles default to True
    objects(list): optional,can filter the model to only detect objects in this list; empty by default
    
    Returns:
    - img: image with bounding boxes and na  me and confidence labels
    - objectInfo: list containing  coordinates of the bounding box and className which is the name of the detected object 
    """
    #'classId' is the ID of the detected object's class
    #'confidence' is the confidence score of the detection
    #'box' is the bounding box of the detected object
    classIds, confidences, bbox = net.detect(img,confThreshold=thres,nmsThreshold=nms)
    
    #Below has been commented out, if you want to print each sighting of an object to the console you can uncomment below     
    #print(classIds,bbox)
    if len(objects) == 0: objects = classNames # If the 'objects' list is empty, set it to 'classNames', which contains all the class names

    objectInfo =[]
    if len(classIds) != 0:
        for classId, confidence,box in zip(classIds.flatten(),confidences.flatten(),bbox):
            #get the class name of the detected object by indexing into 'classNames' with 'classId - 1'
            #class IDs are 1-based, so subtract 1 to get the correct index
            className = classNames[classId - 1]
            #if the class name of the detected object is in the 'objects' list (i.e., we are interested in this object)
            if className in objects:
                #append the bounding box and class name of the detected object to the 'objectInfo' list
                objectInfo.append([box,className])
                #if 'draw' is True, draw the bounding box and label on the image
                if (draw):
                    #draws a green box around detected object
                    cv2.rectangle(img,box,color=(0,255,0),thickness=2)
                    #overlays the class name in uppercase at the top-left corner of the bounding box using a green color, a font scale of 1, and a thickness of 2
                    cv2.putText(img,classNames[classId-1].upper(),(box[0]+10,box[1]+30), cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
                    #overlays confidence percent in green font 
                    cv2.putText(img,str(round(confidence*100,2)),(box[0]+200,box[1]+30),cv2.FONT_HERSHEY_COMPLEX,1,(0,255,0),2)
    
    return img,objectInfo

if __name__ == "__main__":
    # Initializes and starts the Raspberry Pi camera with a preview configuration. It sets the main format to 'XRGB8888' and the size to (640, 480)
    picam2 = Picamera2()
    picam2.configure(picam2.create_preview_configuration(main={"format": 'XRGB8888', "size": (640, 480)}))
    picam2.start()
       
    #Below is the never ending loop that determines what will happen when an object is identified.    
    while True:
     img = picam2.capture_array("main") #captures an image in the format specified by the main configuration of the camera(XRGB8888) with the camera and saves it under varible img
     img = cv2.cvtColor(img, cv2.COLOR_BGRA2BGR) #converts the color format of the captured image from BGRA (Blue, Green, Red, Alpha) to BGR (Blue, Green, Red)
     result, objectInfo = getObjects(img,0.45,0.2)#calls the getObjects function with a confidence threshold of 0.45 and a non-max suppression threshold of 0.2.
     cv2.imshow("Output",img) #displays the image in a window named "Output"
       

        
     k = cv2.waitKey(200)
     if k == 27:    # Esc key to stop
        # EXIT
         picam2.stop()
         cv2.destroyAllWindows()
         break
