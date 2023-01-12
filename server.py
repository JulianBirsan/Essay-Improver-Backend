from flask import Flask, jsonify, request
from flask_cors import CORS
from main import main

app = Flask(__name__)
CORS(app)

@app.route("/result", methods =['POST'])
def result():
    return main([request.json['essay']])

if __name__ == "__main__":
    app.run(debug=True)