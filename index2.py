{% extends "base.html" %}
{% block content %}

    <style>

        .image-container {
        display: flex;
        justify-content: center;
    }

    @media (min-width: 768px) {
        .image {
            margin: 200px;
        }
    }

        h1 {
            padding-top: 150px;
            text-align: center;
        }

        .log-container {
            display: flex;
            justify-content: space-around;
        }

        .log {
            text-align: center;
        }
    </style>
      
    <div class="log-container">
        <div class="log">
            <h1>Pest Log</h1>
            <ul>
                {% for line in motion_lines %}
                    {% if line.startswith('pest') %}
                        <li>{{ line.strip() }}</li>
                    {% endif %}
                {% endfor %}
            </ul>
            <a href="full_log"> show more </a>
        </div>
        <div class="log">
            <h1>Friend Log</h1>
            <ul>
                {% for line in motion_lines %}
                    {% if line.startswith('friend') %}
                        <li>{{ line.strip() }}</li>
                    {% endif %}
                {% endfor %}
            </ul>
            <a href="full_log"> show more </a>
        </div>
    </div>
        <a href="full_log"> show more </a>
        <div class="image-container">
            <div class="image">
                <h2>Latest Pest Image:</h2>
                {% for filename in pest_image_filenames %}
        <img src="{{ url_for('get_pest_image', filename=filename) }}" alt="Pest Image">
        {% endfor %}
            </div>
        
        <div class="image">
            <h2>Latest Friend Image:</h2>
            <img src="{{ url_for('get_friend_image', filename='friend1.jpg') }}" alt="Latest Friend Image">
        </div>
        
        </div>

{% endblock %}
