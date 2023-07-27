# subscriber.py
import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe, which need to put into on_connect
    # If reconnect after losing the connection with the broker, it will continue to subscribe to the raspberry/topic topic

# The callback function, it will be triggered when receiving messages
def on_message(client, userdata, msg):
    print(f"{msg.payload}")

def create_client():
    client.on_message = on_message

    # Set the will message, when the Raspberry Pi is powered off, or the network is interrupted abnormally, it will send the will message to other clients
    #clienttwo.will_set('raspberry/status', b'{"status": "Off"}')

    # Create connection, the three parameters are broker address, broker port number, and keep-alive time respectively

    return client 