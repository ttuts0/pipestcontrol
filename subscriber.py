# subscriber.py
import paho.mqtt.client as mqtt
import base64 

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe, which need to put into on_connect
    client.subscribe("pestbusterai/motion")
    client.subscribe("pestbusterai/pest_image")
    client.subscribe("pestbusterai/friend_image")

def print_msg(client, userdata, msg):#function will be called when the MQTT client (client) receives a message on the subscribed topic.
    f=open("motion_log.txt", "a")
    message = msg.payload.decode('utf-8')
    f.write(message+'\n')
    f.close()

def get_pest_image(client, userdata, msg):
    print('saving image')
    message2 = str(msg.payload.decode('utf-8'))
    img =message2.encode('ascii')
    final_msg=base64.b64decode(img)
    open('pest_images/receive_img.jpg','wb').write(final_msg)

def get_friend_image(client, userdata, msg):
    print('saving image')
    message2 = str(msg.payload.decode('utf-8'))
    img =message2.encode('ascii')
    final_msg=base64.b64decode(img)
    open('friend_images/receive_img.jpg','wb').write(final_msg)

client = mqtt.Client()
client.on_connect = on_connect
#client.on_message = print_msg
#client.on_message=print_msg2
client.message_callback_add("pestbusterai/motion", print_msg)
client.message_callback_add("pestbusterai/pest_image", get_pest_image)
client.message_callback_add("pestbusterai/friend_image", get_friend_image)
client.connect("broker.emqx.io", 1883, 60)
client.loop_forever()