from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "<h1>Developer Focus: Success!</h1><p>Flask is running in the Execution Environment.</p>"

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8000)

