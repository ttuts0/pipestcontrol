from app import app

if __name__ == "__main__":
    # Bind to all interfaces (0.0.0.0) to make the app accessible externally
    app.run(host="0.0.0.0", port=5000)
