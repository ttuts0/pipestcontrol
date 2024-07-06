import paho.mqtt.client as mqtt
import base64 
import csv
from datetime import datetime
from app import app, db
from app.models import Detection, Critter

global friend_image_count
friend_image_count = 1

global pest_image_count
pest_image_count = 1

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("pestbusterai/motion")
    client.subscribe("pestbusterai/pest_image")
    client.subscribe("pestbusterai/friend_image")

def print_msg(client, userdata, msg):
    f = open("motion_log.txt", "a")
    message = msg.payload.decode('utf-8')
    f.write(message + '\n')
    f.close()

    parts = message.split(',')
    critter_name = parts[0].strip()  # Extract critter name
    critter_type = parts[1].strip().lower()
    detection_time_str = parts[2].strip()
    detection_time = datetime.strptime(detection_time_str, '%Y/%m/%d %H:%M:%S')

    is_pest = True if critter_type == 'pest' else False

    # Create or get the Critter record and add Detection record to the database
    with app.app_context():
        critter = Critter.query.filter_by(name=critter_name, is_pest=is_pest).first()
        if not critter:
            critter = Critter(name=critter_name, is_pest=is_pest)
            db.session.add(critter)
            db.session.commit()

        new_detection = Detection(
            critter_id=critter.id,
            detection_time=detection_time
        )
        db.session.add(new_detection)
        db.session.commit()

def get_pest_image(client, userdata, msg):
    global pest_image_count
    print('saving pest image')
    message2 = str(msg.payload.decode('utf-8'))
    img = message2.encode('ascii')
    final_msg = base64.b64decode(img)
    filename = f'pest_images/pest{pest_image_count}.jpg'
    with open(filename, 'wb') as f:
        f.write(final_msg)

def get_friend_image(client, userdata, msg):
    global friend_image_count
    print('saving friend image')
    message2 = str(msg.payload.decode('utf-8'))
    img = message2.encode('ascii')
    final_msg = base64.b64decode(img)
    filename = f'friend_images/friend{friend_image_count}.jpg'
    with open(filename, 'wb') as f:
        f.write(final_msg)

client = mqtt.Client()
client.on_connect = on_connect
client.message_callback_add("pestbusterai/motion", print_msg)
client.message_callback_add("pestbusterai/pest_image", get_pest_image)
client.message_callback_add("pestbusterai/friend_image", get_friend_image)
client.connect("broker.emqx.io", 1883, 60)
client.loop_forever()
