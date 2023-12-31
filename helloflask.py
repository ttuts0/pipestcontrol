from flask import Flask, request, Response, stream_with_context, render_template, send_from_directory
from datetime import datetime
import paho.mqtt.client as mqtt
import time
from collections import defaultdict  # Import defaultdict
import os
app = Flask(__name__)#creates a flask application instance and assinges it to variable app, name is to figure out the path 

# Function to read motion data from a file and organize it by hour
def get_motion_data_from_file(file_path):
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

# Function to get the last three lines from a file
def get_last_three_lines(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    formatted_lines = []
    for line in lines[-3:]:
        formatted_lines.append(str(line))
    return formatted_lines

# Function to get the lines before the last three from a file
def get_rest_of_lines(file_path):
    with open(file_path, 'r') as file:
        lines= file.readlines()
    formatted_lines = []
    for line in lines[:-3]:
        formatted_lines.append(str(line))
    return formatted_lines

# Route to display the last three lines from the motion log
@app.route('/')
def stream_file():
    file_path = 'motion_log.txt'
    last_three_lines = get_last_three_lines(file_path)
    return render_template('index.html', motion_lines=last_three_lines)

# Route to retrieve and display pest images
@app.route('/pest_images/<filename>')
def get_pest_image(filename):
    return send_from_directory('pest_images', filename)

# Route to retrieve and display friend images
@app.route('/friend_images/<filename>')
def get_friend_image(filename):
    return send_from_directory('friend_images', filename)

# Route to display the rest of the motion log entries
@app.route('/full_log')
def show_full_log():
    file_path = 'motion_log.txt'
    rest_of_lines = get_rest_of_lines(file_path)
    return render_template('show_more.html', lines=rest_of_lines)

# Route to display motion statistics
@app.route('/stats')
def stats():
    file_path = 'motion_log.txt'
    motion_data = get_motion_data_from_file(file_path)
    motion_data_copy = dict(motion_data) 
    return render_template('stats.html', motion_data=motion_data)

if __name__ == "__main__":
    # Launch the Flask dev server
    app.run(host="localhost", debug=True)
