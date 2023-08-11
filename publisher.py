import paho.mqtt.client as mqtt
import time
import base64
from classify2 import get_file_path
from datetime import datetime

# Create MQTT client and connect to broker
def create_client():#add parameter to change broker
    client = mqtt.Client()
    client.connect("broker.emqx.io", 1883, 60)
    return client

# Encode and send an image over MQTT in string format, covert image to base64 and publish it
def send_pic(file_path, client, is_pest):
    with open(file_path,"rb") as image:
        img = image.read()
    message2=img
    base64_bytes=base64.b64encode(message2)
    base64_message=base64_bytes.decode('ascii')+" "+str(datetime.now())
    if is_pest:
        client.publish('pestbusterai/pest_image', payload = base64_message, qos=0, retain=False)
    else:
        client.publish('pestbusterai/friend_image', payload = base64_message, qos=0, retain=False)