from tflite_runtime.interpreter import Interpreter
import numpy as np#array operations
from PIL import Image#mkae inputted image compatible w ML
import time
import random
def get_file_path():
    number = random.randint(9,20)
    file_path ='sample_pictures/'+f'{number}.jpg'
    return file_path
def search_for_pest():
    model_path = "model_files/mobilenet_v1_1.0_224_quant.tflite" #img classification model
    label_path = "model_files/labels.txt"#labels of imgs in classified model
    pest_log = 'pests.txt'

    interpreter = Interpreter(model_path=model_path)

    with open(label_path, 'r') as f:
        labels = list(map(str.strip, f.readlines()))
        
    input_details = interpreter.get_input_details()

    output_details = interpreter.get_output_details()

    input_shape = input_details[0]['shape']

    size = input_shape[1:3]

    file_path = get_file_path()

    img = Image.open(file_path).convert('RGB') 
    img = img.resize(size) 
    img = np.array(img) 

    processed_image = np.expand_dims(img, axis=0)# Add a batch dimension
    #print('value of pixel 145x223 in processed_image:',processed_image[0][145][223])

    # Now allocate tensors so that we can use the set_tensor() method to feed the processed_image
    interpreter.allocate_tensors()
    interpreter.set_tensor(input_details[0]['index'], processed_image)

    t1=time.time()
    interpreter.invoke()
    t2=time.time()
    time_taken=(t2-t1)*1000 #milliseconds

    # Obtain results 
    predictions = interpreter.get_tensor(output_details[0]['index'])[0]

    top_k = 5
    top_k_indices = np.argsort(predictions)[::-1][0:top_k]
    
    pest_list=[]
    with open(pest_log,'r') as file:
        pest_list=[line.strip() for line in file.readlines()]

    for i in range(top_k):
        score=predictions[top_k_indices[i]]/255.0
        lbl=labels[top_k_indices[i]]
        for f in pest_list:
            if lbl.lower() in f.lower():
                return True, file_path

    top_label = labels[top_k_indices[0]]
    index_max_score=top_k_indices[0]
    max_score=score=predictions[index_max_score]/255.0
    max_label=labels[index_max_score]

    return False, file_path