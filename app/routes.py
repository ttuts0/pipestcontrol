from flask import render_template, send_from_directory, request
from app import app
from app.models import Detection, Critter
from sqlalchemy import desc
from collections import defaultdict
from datetime import datetime,timedelta




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
# def get_last_three_lines(file_path):
#     with open(file_path, 'r', encoding='utf-8') as file:
#         lines = file.readlines()
#     formatted_lines = []
#     for line in lines[-3:]:
#         formatted_lines.append(str(line))
#     return formatted_lines

# def get_last_three_entries():
#     # Query for the last three entries ordered by timestamp descending
#     last_three_entries = User.query.order_by(desc(User.detection_time)).limit(3).all()
    
#     formatted_lines = []
#     for entry in reversed(last_three_entries):  # Reverse to show most recent first
#         pest_type = "Pest" if entry.is_pest else "Friend"
#         formatted_lines.append(f"{entry.pest_identification},{pest_type},{entry.detection_time.strftime('%Y-%m-%d %H:%M:%S')}")

#     return formatted_lines

def get_last_three_entries():
    # Query for the last three entries ordered by timestamp descending
    last_three_entries = Detection.query.join(Critter).order_by(desc(Detection.detection_time)).limit(3).all()
    
    formatted_lines = []
    for entry in reversed(last_three_entries):  # Reverse to show most recent first
        pest_type = "Pest" if entry.critter.is_pest else "Friend"
        formatted_lines.append(f"{entry.critter.name},{pest_type},{entry.detection_time.strftime('%Y-%m-%d %H:%M:%S')}")

    return formatted_lines


@app.route('/')
def stream_file():
    #file_path = 'motion_log.txt'
    last_three_lines = get_last_three_entries()
    print(last_three_lines)  # Debug print statement
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
# 
@app.route('/full_log', methods=['GET', 'POST'])
def show_full_log():
    search_query = request.form.get('search_query', '')
    date_filter = request.args.get('date')
    
    query = Detection.query.join(Critter).order_by(Detection.detection_time.desc())
    
    if date_filter:
        start_date = datetime.strptime(date_filter, '%Y-%m-%d')
        end_date = start_date + timedelta(days=1)
        query = query.filter(Detection.detection_time >= start_date, Detection.detection_time < end_date)
    
    all_entries = query.all()

    if search_query:
        search_query = search_query.lower()
        all_entries = [
            entry for entry in all_entries 
            if search_query in ('pest' if entry.critter.is_pest else 'friend').lower() or 
               search_query in entry.critter.name.lower() or
               search_query in entry.detection_time.strftime('%Y-%m-%d')
        ]

    grouped_entries = defaultdict(list)
    for entry in all_entries:
        date_str = entry.detection_time.strftime('%Y-%m-%d')
        grouped_entries[date_str].append(entry)
    print(grouped_entries) 
    return render_template('show_more.html', grouped_entries=grouped_entries, search_query=search_query)

@app.route('/daily_report/<date>')
def daily_report(date):
    report_date = datetime.strptime(date, '%Y-%m-%d')
    start_date = datetime.combine(report_date, datetime.min.time())
    end_date = datetime.combine(report_date, datetime.max.time())
    
    data = Detection.query.join(Critter).filter(Detection.detection_time >= start_date, Detection.detection_time <= end_date).all()
    total_detections = len(data)
    num_pests = sum(1 for entry in data if entry.critter.is_pest)
    num_friends = total_detections - num_pests
    
    # Count detections for each type of friend
    friend_counts = {}
    for entry in data:
        if not entry.critter.is_pest:
            friend_counts[entry.critter.name] = friend_counts.get(entry.critter.name, 0) + 1
    
    return render_template('dailyreport.html', date=report_date, total_detections=total_detections, num_pests=num_pests, num_friends=num_friends, friend_counts=friend_counts)


# Route to display motion statistics
@app.route('/stats')
def stats():
    file_path = 'motion_log.txt'
    motion_data = get_motion_data_from_file(file_path)
    motion_data_copy = dict(motion_data) 
    return render_template('stats.html', motion_data=motion_data)

@app.route('/recommendations')
def pest_control_recommendations():
    recommendations = [
        {"title": "Maintain Plant Health", "details": [
            "Nutrient Management: Use appropriate fertilizers to maintain soil health and plant vigor.",
            "Pruning: Regularly prune dead or diseased plant parts to prevent pest harborage."
        ]},
        {"title": "Cultural Practices", "details": [
            "Intercropping: Plant a mix of crops to confuse and deter pests.",
            "Mulching: Use mulch to retain soil moisture, suppress weeds, and prevent soil-borne pests from reaching plants."
        ]},
        {"title": "Physical Barriers", "details": [
            "Netting and Row Covers: Use netting or row covers to protect plants from insects and birds.",
            "Fences: Erect fences to keep larger pests like rabbits and deer away from the garden."
        ]},
        {"title": "Biological Controls", "details": [
            "Beneficial Insects: Introduce or encourage beneficial insects like ladybugs, predatory beetles, and parasitic wasps to control pest populations.",
            "Companion Planting: Grow companion plants that repel pests or attract beneficial insects. For example, plant marigolds to deter nematodes or basil to repel flies and mosquitoes.",
            "Sticky Traps: Place sticky traps around the garden to monitor and reduce pest populations."
        ]},
        {"title": "Sanitation", "details": [
            "Remove Debris: Clear plant debris and fallen leaves that can harbor pests.",
            "Proper Disposal: Dispose of infested plant material properly to prevent reinfestation."
        ]}
    ]
    return render_template('recommendations.html', recommendations=recommendations)
