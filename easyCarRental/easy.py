"""Flask web application"""
from app import app  


if __name__ == "__main__":  # checks if the script runs directly
    app.run(port=3000, debug=True)