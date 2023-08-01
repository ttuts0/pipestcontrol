from flask import Flask, request, Response, stream_with_context, render_template
from datetime import datetime
import paho.mqtt.client as mqtt
import time

app = Flask(__name__)#creates a flask application instance and assinges it to variable app, name is to figure out the path 

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    # Subscribe, which need to put into on_connect
    client.subscribe("pestbusterai/motion")

def print_msg(client, userdata, msg):#function will be called when the MQTT client (client) receives a message on the subscribed topic.
    f=open("motion_log.txt", "a")
    f.write(f"{msg.payload}\n")
    f.close()

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = print_msg
client.connect("broker.emqx.io", 1883, 60)

def get_last_three_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines[-3:]

def get_rest_of_lines(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    return lines[:-3]

@app.route('/')
def stream_file():
    file_path = 'motion_log.txt'
    last_three_lines = get_last_three_lines(file_path)
    #formatted_lines = format_lines(last_three_lines)
    return render_template('index.html', lines=last_three_lines)

@app.route('/full_log')
def show_full_log():
    file_path = 'motion_log.txt'
    rest_of_lines = get_rest_of_lines(file_path)
    #formatted_lines = format_lines(rest_of_lines)
    return render_template('show_more.html', lines=rest_of_lines)
#HELLO_HTML = """
 #   <html><body>
  #      <h1>{0}</h1>
   #     The time is {1}.
    #</body></html>"""

if __name__ == "__main__":
    # Launch the Flask dev server
    client.loop_start()
    app.run(host="localhost", debug=True)
