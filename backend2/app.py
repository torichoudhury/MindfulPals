import base64
import io
import cv2
from flask import Flask, request
from flask_cors import CORS
import numpy as np
from keras.models import load_model
from emotion import predict_emotion 
from pyngrok import ngrok
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Retrieve Ngrok authentication token from environment variable
ngrok_auth_token = os.getenv("NGROK_AUTH_TOKEN")
if ngrok_auth_token is None:
    raise ValueError("Ngrok authentication token not found in environment variables.")

port_no=5000
public_url = ngrok.connect(port_no).public_url
print(public_url)


app = Flask(__name__)
CORS(app)

face_classifier = cv2.CascadeClassifier(r'haarcascade_frontalface_default.xml')
emotion_classifier = load_model(r'model.h5')

@app.route('/api/send_frame', methods=['POST'])
def send_frame():
    data = request.get_json()
    frame_data = data.get('frame')

    # Convert the base64-encoded image to OpenCV format
    image_data = base64.b64decode(frame_data.split(',')[1])
    image_np = cv2.imdecode(np.frombuffer(image_data, np.uint8), cv2.IMREAD_COLOR)

    # Perform face detection
    gray = cv2.cvtColor(image_np, cv2.COLOR_BGR2GRAY)
    faces = face_classifier.detectMultiScale(gray)

    emotion_label = None  # Initialize emotion_label before the loop

    for (x, y, w, h) in faces:
        roi_gray = gray[y:y+h, x:x+w]
        roi_gray = cv2.resize(roi_gray, (48, 48), interpolation=cv2.INTER_AREA)

        # Predict emotion
        emotion_label = predict_emotion(emotion_classifier, roi_gray)

        # Draw rectangle and label on the frame
        cv2.rectangle(image_np, (x, y), (x+w, y+h), (0, 255, 255), 2)
        label_position = (x, y)
        cv2.putText(image_np, emotion_label, label_position, cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    # No need to display the frame using cv2.imshow

    print("Emotion:", emotion_label)

    return {'status': 'success', 'emotion': emotion_label}

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=port_no)