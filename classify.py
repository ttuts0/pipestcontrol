
from tflite_runtime.interpreter import Interpreter
import numpy as np#array operations
from PIL import Image#mkae inputted image compatible w ML
import time
import random

def search_for_pest():
    model_path = "model_files/mobilenet_v1_1.0_224_quant.tflite" #img classification model
    label_path = "model_files/labels.txt"#labels of imgs in classified model

    interpreter = Interpreter(model_path=model_path)

    with open(label_path, 'r') as f:
        labels = list(map(str.strip, f.readlines()))
        
    #print(labels)
    #print('n Printing value of label at index 126:',labels[126])

    #information about model
    #print("n--------Input Details of Model-------------------n")
    input_details = interpreter.get_input_details()
    #print(input_details)

    #print("n--------Output Details of Model-------------------n")
    output_details = interpreter.get_output_details()
    #print(output_details)

    input_shape = input_details[0]['shape']

    #print("shape of input: ",input_shape)
    size = input_shape[1:3]
    #print("size of image: ", size) 

    # Fetch image & preprocess it to match the input requirements of the model
    # file_path = "sample_pictures/10.jpg"
    #file_path = "sample_pictures/11.jpg"
    number = random.randint(9,20)
    file_path =f'sample_pictures/{number}.jpg'
    #random.choice(["sample_pictures/12.jpg", "sample_pictures/9.jpg"])
    print(file_path)

    img = Image.open(file_path).convert('RGB') #read the image and convert it to RGB format
    img = img.resize(size) #resize the image to 224x224
    img = np.array(img) # convert the image in an array

    #print(img)
    #print('value of pixel 145x223: ',img[145][223])

    processed_image = np.expand_dims(img, axis=0)# Add a batch dimension
    #print('value of pixel 145x223 in processed_image:',processed_image[0][145][223])

    # Now allocate tensors so that we can use the set_tensor() method to feed the processed_image
    interpreter.allocate_tensors()
    #print(input_details[0]['index'])
    interpreter.set_tensor(input_details[0]['index'], processed_image)

    t1=time.time()
    interpreter.invoke()
    t2=time.time()
    time_taken=(t2-t1)*1000 #milliseconds
    #print("time taken for Inference: ",str(time_taken), "ms")

    # Obtain results 
    predictions = interpreter.get_tensor(output_details[0]['index'])[0]

    #print("length of array: ", len(predictions),"n")

    for i in range(len(predictions)):
        if(predictions[i]>0):
            print("predictions["+str(i)+"]: ",predictions[i])

    top_k = 5
    top_k_indices = np.argsort(predictions)[::-1][0:top_k]
    #print("Sorted array of top indices:",top_k_indices)

    for i in range(top_k):
        score=predictions[top_k_indices[i]]/255.0
        lbl=labels[top_k_indices[i]]
        print(lbl, "=", score)
        if lbl.lower() in ['tabby', 'egyptian cat','tiger cat', 'lynx', 'mexican hairless', 'siamese cat']:
            print('found cat')
            return True
    

    top_label = labels[top_k_indices[0]]
    index_max_score=top_k_indices[0]
    max_score=score=predictions[index_max_score]/255.0
    max_label=labels[index_max_score]

    print(max_label,": ",max_score)
    print("couldn't fibd cat")
    return False
search_for_pest()
    
    