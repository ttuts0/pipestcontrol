
from tflite_runtime.interpreter import Interpreter
import numpy as np#array operations
from PIL import Image#mkae inputted image compatible w ML
import time
import random

model_path = "model_files/mobilenet_v1_1.0_224_quant.tflite" #img classification model
label_path = "model_files/labels.txt"#labels of imgs in classified model

interpreter = Interpreter(model_path=model_path)

with open(label_path, 'r') as f:
    labels = list(map(str.strip, f.readlines()))

#print(labels)
print('n Printing value of label at index 126:',labels[126])

#information about model
print("n--------Input Details of Model-------------------n")
input_details = interpreter.get_input_details()
print(input_details)

print("n--------Output Details of Model-------------------n")
output_details = interpreter.get_output_details()
print(output_details)

input_shape = input_details[0]['shape']

print("shape of input: ",input_shape)
size = input_shape[1:3]
print("size of image: ", size) 

# Fetch image & preprocess it to match the input requirements of the model
file_path = "sample_pictures/1.jpg"
img = Image.open(file_path).convert('RGB') #read the image and convert it to RGB format
img = img.resize(size) #resize the image to 224x224
img = np.array(img) # convert the image in an array

#print(img)
print('value of pixel 145x223: ',img[145][223])

processed_image = np.expand_dims(img, axis=0)# Add a batch dimension
print('value of pixel 145x223 in processed_image:',processed_image[0][145][223])

def search_for_pest():
    return random.choice([True, False])
    
