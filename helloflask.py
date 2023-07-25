from flask import Flask
from datetime import datetime

app = Flask(__name__)

@app.route('/')
def hello():
    return """<html><body>
        <h1>Hello, world!</h1>
        The time is """ + str(datetime.now()) + """.
        </body></html>"""

if __name__ == "__main__":
    # Launch the Flask dev server
    app.run(host="localhost", debug=True)