from flask import Flask, render_template, Response
import cv2
from cloudinary import uploader
import cloudinary

# Initialize Cloudinary with your credentials
cloudinary.config(
    cloud_name='dildznazt',
    api_key='236923818157321',
    api_secret='-Nc3-tS4BZQcdDPvqGJjHS-4G5E'
)

app = Flask(__name__)

# Load the pre-trained cascade classifier for detecting faces
cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cv2.data.haarcascades + cascPath)

# Global variable to store the frame from the webcam
frame = None

# Function to capture images from the webcam
def capture_frame():
    global frame
    video_capture = cv2.VideoCapture(0)
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



# from flask import Flask, request, jsonify, render_template
# import cv2
# import cloudinary
# from cloudinary.uploader import upload
# from cloudinary.utils import cloudinary_url
# import numpy as np
#
# app = Flask(__name__)
#
# # Load the cascade
# cascPath = "haarcascade_frontalface_default.xml"
# faceCascade = cv2.CascadeClassifier(cascPath)
#
# # Cloudinary configuration
# cloudinary.config(
#     cloud_name='dildznazt',
#     api_key='236923818157321',
#     api_secret='-Nc3-tS4BZQcdDPvqGJjHS-4G5E'
# )
#
#
# def capture_image():
#     video_capture = cv2.VideoCapture(0)
#     ret, frame = video_capture.read()
#     video_capture.release()
#     return frame
#
#
# @app.route('/detect_faces', methods=['POST'])
# def detect_faces():
#     try:
#         # Capture image from the camera
#         frame = capture_image()
#
#         # Convert the image to grayscale
#         gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
#
#         # Detect faces in the image
#         faces = faceCascade.detectMultiScale(
#             gray,
#             scaleFactor=1.1,
#             minNeighbors=5,
#             minSize=(30, 30)
#         )
#
#         # Convert frame to bytes
#         _, img_encoded = cv2.imencode('.jpg', frame)
#         img_bytes = img_encoded.tobytes()
#
#         # Upload the captured image to Cloudinary
#         response = upload(img_bytes, folder="captured_images")
#
#         # Get the URL of the uploaded image
#         image_url = response['secure_url']
#
#         # Extract face coordinates
#         face_coordinates = []
#         for (x, y, w, h) in faces:
#             face_coordinates.append({"x": x, "y": y, "width": w, "height": h})
#
#         # Return the detected face coordinates and image URL
#         return jsonify({"faces": face_coordinates, "image_url": image_url}), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500
#
#
#
# if __name__ == '__main__':
#     app.run(debug=True)
