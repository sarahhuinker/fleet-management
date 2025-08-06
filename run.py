# run.py
# Entrypoint: create the Flask app and run the development server.

from app import create_app  # import the factory function

app = create_app()  # create the Flask application

if __name__ == '__main__':
    # Run with debug=True during development so you get auto-reload and the interactive debugger
    app.run(debug=True)


