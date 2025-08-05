# Import the Flask class from the flask library
from flask import Flask

# Create an instance of the Flask app
app = Flask(__name__)

# Define the route for the homepage ('/')
@app.route('/')
def home():
    # What gets shown when someone goes to http://localhost:5000
    return "Hello, Sarah! Your Flask app is running 💥"

# Run the app only if this file is executed directly
if __name__ == '__main__':
    # Start the development server with debugging enabled
    app.run(debug=True)
