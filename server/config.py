import os

basedir = os.path.abspath(os.path.dirname(__file__))

class Config:
    # database URI (Uniform Resource Identifier) is a string that uniquely identifies a database connection
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'app.db')
    UPLOAD_FOLDER = os.path.join(basedir, 'detected_pics')
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_default_secret_key'
    
    # Email settings
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_USERNAME = 'fixme@email.com'   # Use your actual Gmail address
    MAIL_PASSWORD = 'password123'

    # Session settings
    SESSION_TYPE = 'filesystem'  # Use filesystem to store session data
    SESSION_FILE_DIR = os.path.join(basedir, 'flask_session')  # Directory to store session files
    SESSION_PERMANENT = False
    SESSION_USE_SIGNER = True  # Use a secure cookie for sessions
    SESSION_KEY_PREFIX = 'session:'  # Prefix for session keys

    # Ensure the upload folder exists and has the correct permissions
    @staticmethod
    def init_app(app):
        if not os.path.exists(Config.UPLOAD_FOLDER):
            os.makedirs(Config.UPLOAD_FOLDER)
            print(f"Created upload folder at: {Config.UPLOAD_FOLDER}")
        else:
            print(f"Upload folder already exists at: {Config.UPLOAD_FOLDER}")

        #set permissions
        os.chmod(Config.UPLOAD_FOLDER, 0o755)
        print(f"Set permissions for upload folder at: {Config.UPLOAD_FOLDER}")

