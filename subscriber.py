import paho.mqtt.client as mqtt
import base64 

global friend_image_count
friend_image_count = 1

global pest_image_count
pest_image_count = 1

#when a connection is identified client subscribes to topics motion, pest_image and friend_image
def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe, which need to put into on_connect
    client.subscribe("pestbusterai/motion")
    client.subscribe("pestbusterai/pest_image")
    client.subscribe("pestbusterai/friend_image")

#function will be called when the MQTT client (client) receives a message on the subscribed topic.
def print_msg(client, userdata, msg):
    f=open("motion_log.txt", "a")
    message = msg.payload.decode('utf-8')
    f.write(message+'\n')
    f.close()

#gets the pest image in a string format and sends at what date and time detected and adds it to the pest_images folder
def get_pest_image(client, userdata, msg):
    global pest_image_count
    print('saving pest image')
    message2 = str(msg.payload.decode('utf-8'))
    img =message2.encode('ascii')
    final_msg=base64.b64decode(img)
    filename = f'pest_images/pest{pest_image_count}.jpg'
    with open(filename, 'wb') as f:
        f.write(final_msg)

#gets the friend image in a string format and sends at what date and time detected and adds it to the friend_images folder
def get_friend_image(client, userdata, msg):
    global friend_image_count
    print('saving friend image')
    message2 = str(msg.payload.decode('utf-8'))
    img =message2.encode('ascii')
    final_msg=base64.b64decode(img)
    filename = f'friend_images/friend{friend_image_count}.jpg'
    with open(filename, 'wb') as f:
        f.write(final_msg)

#creates new MQTT Client, connects to broker, subscribes to topic and delops respective function
client = mqtt.Client()
client.on_connect = on_connect
client.message_callback_add("pestbusterai/motion", print_msg)
client.message_callback_add("pestbusterai/pest_image", get_pest_image)
client.message_callback_add("pestbusterai/friend_image", get_friend_image)
client.connect("broker.emqx.io", 1883, 60)
client.loop_forever()