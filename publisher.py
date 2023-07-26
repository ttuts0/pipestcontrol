import paho.mqtt.client as mqtt
import time
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
