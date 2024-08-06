from flask import render_template, send_from_directory, request, jsonify, session,flash
from app import app, db
from app.models import Detection, Critter, Configure
from sqlalchemy import desc
from collections import defaultdict
from datetime import datetime,timedelta
from werkzeug.utils import secure_filename
import os
import smtplib
from flask_mail import Mail, Message
from email.mime.text import MIMEText
import requests

mail = Mail(app)

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
            print(critter_name)
            db.session.add(new_detection)
            db.session.commit()

            if is_pest:
                send_alert_email_if_needed(critter_name)

        return jsonify({'message': 'File successfully uploaded'}), 200

    return jsonify({'error': 'Invalid file type'}), 400


@app.route('/settings', methods=['GET', 'POST'])
def settings():
    default_threshold = 15
    current_threshold = default_threshold
    cooldown_times = {}

    if request.method == 'POST':
        # Handle threshold update
        threshold_input = request.form.get('threshold')
        if threshold_input:
            try:
                current_threshold = int(threshold_input)
                flash('Threshold updated successfully!', 'success')
            except ValueError:
                flash('Invalid threshold value. Please enter a valid number.', 'error')

        # Handle cooldown times update
        critters = ['grasshopper', 'snail', 'rabbits', 'ladybug', 'butterfly', 'bee']
        for critter in critters:
            # Get the cooldown time from the form
            cooldown_time_str = request.form.get(f'cooldown_{critter}')
            if cooldown_time_str:
                try:
                    cooldown_time = int(cooldown_time_str)
                except ValueError:
                    continue  
                
                # Update or add entry in the database
                config_entry = Configure.query.filter_by(critter_name=critter).first()
                if config_entry:
                    config_entry.cooldown_time = cooldown_time
                else:
                    config_entry = Configure(critter_name=critter, cooldown_time=cooldown_time)
                    db.session.add(config_entry)
                cooldown_times[critter] = cooldown_time  # Save to the dictionary
            else:
                # If no cooldown time provided, keep the existing or default
                config_entry = Configure.query.filter_by(critter_name=critter).first()
                if config_entry:
                    cooldown_times[critter] = config_entry.cooldown_time
                else:
                    cooldown_times[critter] = 60  # Default value

        db.session.commit()

        # Print the updated Configure table contents
        print("Current Configure table contents:")
        for entry in Configure.query.all():
            print(f"Critter: {entry.critter_name}, Cooldown Time: {entry.cooldown_time}")

        flash('Settings updated successfully!', 'success')
    
    else:
        # For GET request, load current cooldown times from the database
        critters = ['grasshopper', 'snail', 'rabbits', 'ladybug', 'butterfly', 'bee']
        for critter in critters:
            config_entry = Configure.query.filter_by(critter_name=critter).first()
            if config_entry:
                cooldown_times[critter] = config_entry.cooldown_time
            else:
                cooldown_times[critter] = 60  # Default cooldown time

    return render_template('settings.html', current_threshold=current_threshold, cooldown_times=cooldown_times)


@app.route('/get_cooldown_times', methods=['GET'])
def get_cooldown_times():
    cooldown_times = {entry.critter_name: entry.cooldown_time for entry in Configure.query.all()}
    return jsonify(cooldown_times)

@app.route('/', methods=['GET'])
def index():
    today = datetime.combine(datetime.now(), datetime.min.time())
    tomorrow = today + timedelta(days=1)
    yesterday = today - timedelta(days=1)

    # Fetch daily data
    detections_today = Detection.query.filter(
        Detection.detection_time >= today,
        Detection.detection_time < tomorrow
    ).all()

    num_pests = len([d for d in detections_today if d.critter.is_pest])
    num_friends = len([d for d in detections_today if not d.critter.is_pest])

    # Determine activity level for pests
    if num_pests < 5:
        pest_activity_level = 'low'
    elif num_pests < 15:
        pest_activity_level = 'moderate'
    else:
        pest_activity_level = 'high'

    # Determine activity level for friends
    if num_friends < 5:
        friend_activity_level = 'low'
    elif num_friends < 15:
        friend_activity_level = 'moderate'
    else:
        friend_activity_level = 'high'

    friend_counts = {}
    pest_counts = {}

    for detection in detections_today:
        critter_type = detection.critter.name
        if detection.critter.is_pest:
            if critter_type in pest_counts:
                pest_counts[critter_type] += 1
            else:
                pest_counts[critter_type] = 1
        else:
            if critter_type in friend_counts:
                friend_counts[critter_type] += 1
            else:
                friend_counts[critter_type] = 1

    num_pest_types = len(pest_counts)
    num_friend_types = len(friend_counts)

    return render_template('index.html', today=today, num_pests=num_pests,
                           num_friends=num_friends, pest_activity_level=pest_activity_level,
                           friend_activity_level=friend_activity_level,
                           friend_counts=friend_counts, pest_counts=pest_counts,
                           num_pest_types=num_pest_types, num_friend_types=num_friend_types,
                           previous_day=yesterday.strftime('%Y-%m-%d'))
@app.route('/trends')
def trends():
    today = datetime.now().date()
    start_date = today - timedelta(days=6)
    end_date = today

    critters_of_interest = {'rabbits', 'Ladybug', 'Bee', 'grasshopper', 'butterfly', 'snail'}

    data = Detection.query.join(Critter).filter(
        Detection.detection_time >= start_date,
        Detection.detection_time <= end_date,
        Critter.name.in_(critters_of_interest)
    ).all()

    date_critter_data = {date.strftime('%Y-%m-%d'): {critter: [] for critter in critters_of_interest} for date in (start_date + timedelta(n) for n in range(7))}
    
    for entry in data:
        date_str = entry.detection_time.date().strftime('%Y-%m-%d')
        if date_str in date_critter_data:
            critter_name = entry.critter.name
            if critter_name in date_critter_data[date_str]:
                date_critter_data[date_str][critter_name].append({'time': entry.detection_time.strftime('%Y-%m-%dT%H:%M:%S'), 'count': 1})

    # Filter out today's date if it has no data
    critters = list(critters_of_interest)
    dates = sorted([date for date in date_critter_data.keys() if date != today.strftime('%Y-%m-%d') or any(date_critter_data[date][critter] for critter in critters_of_interest)])

    return render_template('trends.html',
                           date_critter_data=date_critter_data,
                           critters=critters,
                           dates=dates)







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


@app.route('/daily_report/')
@app.route('/daily_report/<date>')
def daily_report(date=None):
    if date is None:
        date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    report_date = datetime.strptime(date, '%Y-%m-%d')
    start_date = datetime.combine(report_date, datetime.min.time())
    end_date = datetime.combine(report_date, datetime.max.time())
    
    # Example data fetching and calculations (Replace with your actual data fetching logic)
    data = Detection.query.join(Critter).filter(Detection.detection_time >= start_date, Detection.detection_time <= end_date).all()
    total_detections = len(data)
    num_pests = sum(1 for entry in data if entry.critter.is_pest)
    num_friends = total_detections - num_pests
    
    # Calculate the next and previous dates
    previous_date = (report_date - timedelta(days=1)).strftime('%Y-%m-%d')
    next_date = (report_date + timedelta(days=1)).strftime('%Y-%m-%d')
    
    # Check if the next_date is in the future
    current_date = datetime.now().date()
    next_date_obj = datetime.strptime(next_date, '%Y-%m-%d').date()
    show_next_day_link = next_date_obj <= current_date
    
    # Count detections for each type of friend
    friend_counts = {}
    for entry in data:
        if not entry.critter.is_pest:
            friend_counts[entry.critter.name] = friend_counts.get(entry.critter.name, 0) + 1

    return render_template(
        'dailyreport.html', 
        date=report_date, 
        total_detections=total_detections, 
        num_pests=num_pests, 
        num_friends=num_friends, 
        friend_counts=friend_counts, 
        previous_date=previous_date, 
        show_next_day_link=show_next_day_link, 
        next_date=next_date
    )
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

IMAGES_FOLDER = os.path.join(app.root_path, 'images')

@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory(IMAGES_FOLDER, filename)