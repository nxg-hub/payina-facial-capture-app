from flask import Flask, request, jsonify, render_template
import cv2
import cloudinary
from cloudinary.uploader import upload
from cloudinary.utils import cloudinary_url
import numpy as np

app = Flask(__name__)

# Load the cascade
cascPath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascPath)

# Cloudinary configuration
cloudinary.config(
    cloud_name='dildznazt',
    api_key='236923818157321',
    api_secret='-Nc3-tS4BZQcdDPvqGJjHS-4G5E'
)


# def capture_image():
#     video_capture = cv2.VideoCapture(0)
#     ret, frame = video_capture.read()
#     video_capture.release()
#     return frame
def capture_image():
    """Captures an image from the primary camera.

    Searches for available cameras and attempts to capture an image from the first
    one found. If no camera is found, a RuntimeError is raised.

    Returns:
        numpy.ndarray: The captured image frame.

    Raises:
        RuntimeError: If no camera is found.
    """

    # Enumerate available cameras
    available_cameras = [i for i in range(100)]  # Check up to 10 cameras
    for camera_index in available_cameras:
        video_capture = cv2.VideoCapture(camera_index)
        if video_capture.isOpened():
            ret, frame = video_capture.read()
            video_capture.release()
            if ret:
                return frame

    raise RuntimeError("No camera found!")


@app.route('/detect_faces', methods=['POST'])
def detect_faces():
    try:
        # Capture image from the camera
        frame = capture_image()

        # Convert the image to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Detect faces in the image
        faces = faceCascade.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(30, 30)
        )

        # Convert frame to bytes
        _, img_encoded = cv2.imencode('.jpg', frame)
        img_bytes = img_encoded.tobytes()

        # Upload the captured image to Cloudinary
        response = upload(img_bytes, folder="captured_images")

        # Get the URL of the uploaded image
        image_url = response['secure_url']

        # Extract face coordinates
        face_coordinates = []
        for (x, y, w, h) in faces:
            face_coordinates.append({"x": x, "y": y, "width": w, "height": h})

        # Return the detected face coordinates and image URL
        return jsonify({"faces": face_coordinates, "image_url": image_url}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
