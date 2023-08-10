from flask import Flask, request, Response, stream_with_context, render_template, send_from_directory
from datetime import datetime
import paho.mqtt.client as mqtt
import time
from collections import defaultdict  # Import defaultdict
import os
app = Flask(__name__)#creates a flask application instance and assinges it to variable app, name is to figure out the path 

def get_motion_data_from_file(file_path):
    #motion_data =   defaultdict(lambda: {"pest": 0, "friend": 0})
    motion_data={}
    for i in range(24):
        motion_data[i] = {"pest": 0, "friend": 0}
    with open(file_path, 'r') as file:
        for line in file: 
            parts = line.strip().split(',')
            if len(parts) == 2:
                print(parts[0])
                event = parts[0].strip()
                timestamp = parts[1].strip()
                hour = int(timestamp.split(' ')[-1].split(':')[0])
                if event == 'pest':
                    motion_data[hour]['pest'] += 1
                elif event == 'friend':
                    motion_data[hour]['friend'] += 1

    return motion_data


def get_last_three_image_titles(directory, n):
    image_titles = []
    for filename in os.listdir(directory):
        if filename.endswith('.jpg'):
            image_titles.append(os.path.splitext(filename)[0])
    return image_titles[-3:] 

def get_image_filenames(directory, titles):
    filenames = []
    for title in titles:
        filenames.append(title + '.jpg')
    return filenames

def get_rest_of_lines(file_path):
    with open(file_path, 'r') as file:
        lines= file.readlines()
    formatted_lines = []
    for line in lines[:-3]:
        formatted_lines.append(str(line))
    return formatted_lines

@app.route('/')
def stream_file():
    pest_images = 'pest_images'
    friend_images = 'friend_images'
    num=3

    pest_image_titles = get_last_three_image_titles(pest_images, num)
    friend_image_titles = get_last_three_image_titles(friend_images, num)
    combined_image_titles = pest_image_titles + friend_image_titles

    return render_template('index.html', motion_lines=combined_image_titles)


@app.route('/pest_images/<filename>')
def get_pest_image(filename):
    pest_images = 'pest_images'
    pest_image_titles = get_last_three_image_titles(pest_images, 3)
    pest_image_filenames = get_image_filenames(pest_images, pest_image_titles)
    return send_from_directory('pest_images.html', pest_image_filenames=pest_image_filenames)

@app.route('/friend_images/<filename>')
def get_friend_image(filename):
    return send_from_directory('friend_images', filename)

@app.route('/full_log')
def show_full_log():
    file_path = 'motion_log.txt'
    rest_of_lines = get_rest_of_lines(file_path)
    #formatted_lines = format_lines(rest_of_lines)
    return render_template('show_more.html', lines=rest_of_lines)

@app.route('/stats')
def stats():
    file_path = 'motion_log.txt'
    motion_data = get_motion_data_from_file(file_path)
    motion_data_copy = dict(motion_data) 
    return render_template('stats.html', motion_data=motion_data)

#HELLO_HTML = """
 #   <html><body>
  #      <h1>{0}</h1>
   #     The time is {1}.
    #</body></html>"""

if __name__ == "__main__":
    # Launch the Flask dev server
    app.run(host="localhost", debug=True)
