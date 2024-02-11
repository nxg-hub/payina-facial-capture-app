import os
import cv2
from flask import Flask, render_template, Response

from cloudinary import uploader
from flask_cors import CORS
import cloudinary

# Initialize Cloudinary with your credentials
cloudinary.config(
    cloud_name='dildznazt',
    api_key='236923818157321',
    api_secret='-Nc3-tS4BZQcdDPvqGJjHS-4G5E'
)

app = Flask(__name__)
cors = CORS(app, resources={r"/capture": {"origins": "http://localhost:1234"}})  # Enable CORS for all routes

# Load the pre-trained cascade classifier for detecting faces
cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascPath)

# Global variable to store the frame from the webcam
frame = None


# Function to capture images from the webcam
def capture_frame():
    global frame
    video_capture = cv2.VideoCapture(1)
    success, frame = video_capture.read()
    video_capture.release()  # Release the camera after capturing the frame

# Generator function to stream video frames
def gen_frames():
    global frame
    while True:
        if frame is not None:
            # Encode the frame into JPEG format
            ret, buffer = cv2.imencode('.jpg', frame)
            frame_bytes = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame_bytes + b'\r\n')

            # Use the PORT environment variable if available, otherwise default to 80
            port = int(os.environ.get("PORT", 80))
            app.run(host="0.0.0.0", port=port)

# Route for streaming the video feed
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


# Route for capturing and uploading the frame to Cloudinary
@app.route('/capture', methods=['POST'])
def capture_and_upload():
    global frame
    capture_frame()  # Capture a new frame
    if frame is not None:
        # Convert the frame to JPEG format
        ret, buffer = cv2.imencode('.jpg', frame)
        image_data = buffer.tobytes()

        # Upload the image to Cloudinary
        response = uploader.upload(image_data, folder="captured_images", use_filename=True)

        # Check if the upload was successful
        if 'secure_url' in response:
            return f'Image captured and saved to Cloudinary successfully! URL: {response["secure_url"]}'
        else:
            return 'Failed to upload image to Cloudinary.'
    else:
        return 'No frame available to capture.'


# Route for serving the HTML page
@app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.run(debug=True)
