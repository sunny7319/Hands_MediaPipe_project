# app.py
from flask import Flask, request, render_template, jsonify
from main import predict_image
from PIL import Image
import base64
from io import BytesIO
import os

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/capture', methods=['POST'])
def capture_image():
    data = request.get_json()
    img_data = data['image']
    img_data = img_data.split(",")[1]
    img = Image.open(BytesIO(base64.b64decode(img_data)))
    predicted_class, predicted_prob = predict_image(img)
    return jsonify({'class': predicted_class, 'probability': predicted_prob})

if __name__ == "__main__":
    app.run(debug=True)

