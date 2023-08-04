# subscriber.py
import paho.mqtt.client as mqtt


def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe, which need to put into on_connect
    client.subscribe("pestbusterai/motion")

def print_msg(client, userdata, msg):#function will be called when the MQTT client (client) receives a message on the subscribed topic.
    f=open("motion_log.txt", "a")
    message = msg.payload.decode('utf-8')
    f.write(message+'\n')
    f.close()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = print_msg
client.connect("broker.emqx.io", 1883, 60)
client.loop_forever()