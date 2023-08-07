import paho.mqtt.client as mqtt
import time
import base64
from classify2 import get_file_path
#import TimeDetection

# def on_connect(client, userdata, flags, rc):
#     print(f"Connected with result code {rc}")
#     message = "connected"
#     # Send a message to the raspberry/topic every 1 second, 5 times in a row
#     # The four parameters are topic, sending content, QoS and whether retaining the message respectively
#     client.publish('pestbusterai/general', payload=message, qos=2, retain=False)
#     print(f"send '{message}' to raspberry/topic")

def create_client():#parameter to change broker
    client = mqtt.Client()
    #client.on_connect = on_connect
    client.connect("broker.emqx.io", 1883, 60)

    return client

#client= create_client()
#client.susbcribe('pestbusterai/image')
def send_pic(file_path, client):
    with open(file_path,"rb") as image:
        img = image.read()
    message2=img
    base64_bytes=base64.b64encode(message2)
    base64_message=base64_bytes.decode('ascii')
    client.publish('pestbusterai/image', payload = base64_message, qos=0, retain=False)
