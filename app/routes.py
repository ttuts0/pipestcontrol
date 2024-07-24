from flask import render_template, send_from_directory, request, jsonify, session,flash
from app import app, db
from app.models import Detection, Critter
from sqlalchemy import desc
from collections import defaultdict
from datetime import datetime,timedelta
from werkzeug.utils import secure_filename
import os
import smtplib
from flask_mail import Mail, Message
from email.mime.text import MIMEText
import requests
from flask_session import Session

mail = Mail(app)
sess = Session(app)


#only files with these extensions will be accepted
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    """
    Checks if file is in set allowed_extensions 

    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def send_alert_email(detected_object, threshold):
    """
    Sends an alert email about heightened pest activity.
    """
    sender_email = app.config['MAIL_USERNAME']
    recipient_email = 'tammymathews03@gmail.com'  
    subject = 'Pest Detection Alert'
    body = f"Alert: The pest '{detected_object}' has been detected more than {threshold} times in the last hour."

    msg = Message(subject=subject, sender=sender_email, recipients=[recipient_email])
    msg.body = body

    try:
        mail.send(msg)
        print("Alert email sent successfully.")
    except Exception as e:
        print(f"Failed to send alert email: {e}")

# Function to check and send alert email if needed
def send_alert_email_if_needed(critter_name):
    current_threshold = session.get('alert_threshold', 15)  # Ensure to use the same default value as in the form
    print(f"Checking for pest '{critter_name}' with threshold {current_threshold}")  # Debugging print
    one_hour_ago = datetime.now() - timedelta(hours=1)
    recent_detections = Detection.query.join(Critter).filter(
        Critter.name == critter_name,
        Critter.is_pest == True,
        Detection.detection_time >= one_hour_ago
    ).count()
    
    print(f"Recent detections count: {recent_detections}")  # Debugging print

    if recent_detections > current_threshold:
        send_alert_email(critter_name, current_threshold)

def get_last_three_entries():
    """
    
    Retrieve and format the last three motion detection entries for pests and friends respectively

    Returns:
    List[str]: A list of formatted strings; Each string contains the critter's name, type, and detection time.

    """
    last_three_entries = Detection.query.join(Critter).order_by(desc(Detection.detection_time)).limit(6).all()
    
    formatted_lines = []
    for entry in reversed(last_three_entries):  # Reverse to show most recent first
        pest_type = "Pest" if entry.critter.is_pest else "Friend"
        formatted_lines.append(f"{entry.critter.name},{pest_type},{entry.detection_time.strftime('%Y-%m-%d %H:%M:%S')}")

    return formatted_lines

#route handles POST requests to /upload_image for uploading images.   
@app.route('/upload_image', methods=['POST'])
def upload_image():
    """
    Handles the upload of an image file, saves it to the server, and records
    the associated metadata in the database.

    Returns:
    JSON response with a success message and status code 200 if the file is successfully uploaded,
    or an error message and status code 400 for various errors.
    """
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)

        critter_name = request.form.get('critter_name')
        critter_type = request.form.get('critter_type', '').lower()
        detection_time_str = request.form.get('detection_time')

        # Validate form data
        if not critter_name or not critter_type or not detection_time_str:
            return jsonify({'error': 'Missing required form data'}), 400

        try:
            detection_time = datetime.strptime(detection_time_str, '%Y/%m/%d %H:%M:%S')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY/MM/DD HH:MM:SS'}), 400

        is_pest = True if critter_type == 'pest' else False

        with app.app_context():
            critter = Critter.query.filter_by(name=critter_name, is_pest=is_pest).first()
            
            if not critter:
                return jsonify({'error': f"Critter '{critter_name}' not found in database"}), 400

            # Save the detection entry with image filename
            new_detection = Detection(
                critter_id=critter.id,
                detection_time=detection_time,
                image_filename=filename  # Store the filename in the database
            )
            db.session.add(new_detection)
            db.session.commit()

            if is_pest:
                send_alert_email_if_needed(critter_name)

        return jsonify({'message': 'File successfully uploaded'}), 200

    return jsonify({'error': 'Invalid file type'}), 400

@app.route('/', methods=['GET', 'POST'])
def stream_file():
    """
    Renders the main page with the three latest motion detection entries and recent detection images for pests and friends respectively.
    Allows updating the alert threshold value and cooldown times for detecting different pests.
    
    Returns:
    Rendered HTML template 'index.html' with context variables:
    motion_lines: A list of the last three motion detection entries.
    recent_pest_images: A list of filenames of the three most recent pest detection images.
    recent_friend_images: A list of filenames of the three most recent friend detection images.
    current_threshold: The current alert threshold value.
    cooldown_times: The current cooldown times for each pest type.
    """
    current_threshold = session.get('alert_threshold', 15)
    cooldown_times = session.get('cooldown_times', {
        'grasshopper': 60,
        'snail': 60,
        'rabbit': 60,
        'ladybug': 60,
        'butterfly': 60,
        'bee': 60
    })

    if request.method == 'POST':
        current_threshold = request.form.get('threshold')
        if current_threshold:
            try:
                threshold = int(current_threshold)
                session['alert_threshold'] = threshold
                flash('Threshold updated successfully!', 'success')
                current_threshold = threshold
            except ValueError:
                flash('Invalid threshold value. Please enter a valid number.', 'error')

        cooldown_times = {
            'grasshopper': int(request.form.get('cooldown_grasshopper')),
            'snail': int(request.form.get('cooldown_snail')),
            'rabbit': int(request.form.get('cooldown_rabbit')),
            'ladybug': int(request.form.get('cooldown_ladybug')),
            'butterfly': int(request.form.get('cooldown_butterfly')),
            'bee': int(request.form.get('cooldown_bee'))
        }
        session['cooldown_times'] = cooldown_times

        #Send cooldown times to Raspberry Pi
        raspberry_pi_ip = '172.18.12.50'
        raspberry_pi_url = f'http://{raspberry_pi_ip}:5001/update_cooldown_times'
        try:
            response = requests.post(raspberry_pi_url, json=cooldown_times)
            if response.status_code == 200:
                flash('Cooldown times updated successfully on Raspberry Pi!', 'success')
            else:
                flash('Failed to update cooldown times on Raspberry Pi.', 'error')
        except requests.exceptions.RequestException as e:
            flash(f'Error communicating with Raspberry Pi: {e}', 'error')

    last_three_lines = get_last_three_entries()
    recent_detections = Detection.query.order_by(desc(Detection.detection_time)).limit(6).all()
    recent_pest_images = []
    recent_friend_images = []

    for detection in recent_detections:
        if detection.critter.is_pest and len(recent_pest_images) < 3:
            recent_pest_images.append(detection.image_filename)
        elif not detection.critter.is_pest and len(recent_friend_images) < 3:
            recent_friend_images.append(detection.image_filename)

    return render_template('index.html', motion_lines=last_three_lines,
                           recent_pest_images=recent_pest_images,
                           recent_friend_images=recent_friend_images,
                           current_threshold=current_threshold,
                           cooldown_times=cooldown_times)


@app.route('/get_config', methods=['GET'])
def get_config():
    """
    Endpoint to provide the current configurations to the Raspberry Pi.
    
    Returns:
    JSON response containing the alert threshold and cooldown times.
    """
    config = {
        'cooldown_times': session.get('cooldown_times', {
            'grasshopper': 60,
            'snail': 60,
            'rabbit': 60,
            'ladybug': 60,
            'butterfly': 60,
            'bee': 60
        })
    }
    return jsonify(config)

# Route to display the rest of the motion log entries
@app.route('/full_log', methods=['GET', 'POST'])
def show_full_log():
    """
    Displays the full log of motion detection entries with optional search and date filters.

    Returns:
    str: Rendered HTML template 'show_more.html' displaying grouped motion detection entries and the search query if provided.
    """
    search_query = request.form.get('search_query', '')
    
    query = Detection.query.join(Critter).order_by(Detection.detection_time.desc())
    
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

# Route to display motion statistics
@app.route('/stats')
def stats():
    file_path = 'motion_log.txt'
    motion_data = get_motion_data_from_file(file_path)
    motion_data_copy = dict(motion_data) 
    return render_template('stats.html', motion_data=motion_data)

@app.route('/recommendations')
def pest_control_recommendations():
    """
    Renders a page with pest control recommendations

    Returns:
    Rendered HTML template 'recommendations.html' that displays pest control recommendations
    
    """
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
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    """
    Sends image from detected_pics dir

    Returns:
    The file from the detected_pics directory
    
    """
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)