import os
import cv2
import face_recognition
import numpy as np
import datetime
import pytz
import time
import csv

class FaceRecognitionAttendance:
    def __init__(self, dataset_path, log_file="attendance_log.csv"):
        self.dataset_path = dataset_path
        self.known_face_encodings, self.known_user_ids = self.load_face_encodings()
        self.log_file = log_file  # CSV log file

        # Initialize CSV log
        with open(self.log_file, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(["UserID", "Timestamp", "Accuracy"])

    def load_face_encodings(self):
        known_face_encodings = []
        known_user_ids = []
        for user_id in os.listdir(self.dataset_path):
            user_folder = os.path.join(self.dataset_path, user_id)
            if os.path.isdir(user_folder):
                for filename in os.listdir(user_folder):
                    if filename.endswith(".jpg") or filename.endswith(".png"):
                        img_path = os.path.join(user_folder, filename)
                        img = cv2.imread(img_path)
                        rgb_img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        img_encodings = face_recognition.face_encodings(rgb_img)
                        if img_encodings:
                            img_encoding = img_encodings[0]
                            known_face_encodings.append(img_encoding)
                            known_user_ids.append(user_id)
        return known_face_encodings, known_user_ids

    def process_video_file(self, video_file):
        video_capture = cv2.VideoCapture(video_file)

        while video_capture.isOpened():
            ret, frame = video_capture.read()
            if not ret:
                print("End of video file or failed to capture video frame.")
                break

            # Resize frame for faster face detection
            small_frame = cv2.resize(frame, (0, 0), fx=0.5, fy=0.5)
            rgb_frame = cv2.cvtColor(small_frame, cv2.COLOR_BGR2RGB)

            face_locations = face_recognition.face_locations(rgb_frame)
            face_encodings = face_recognition.face_encodings(rgb_frame, face_locations)

            current_time = time.time()
            for (top, right, bottom, left), face_encoding in zip(face_locations, face_encodings):
                face_distances = face_recognition.face_distance(self.known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                user_id = "Unknown"
                confidence = 0.0
                if face_distances[best_match_index] < 0.6:
                    user_id = self.known_user_ids[best_match_index]
                    confidence = 1 - face_distances[best_match_index]
                accuracy = confidence * 100  # Convert to percentage

                # Scale back face location since we resized the frame
                top *= 2
                right *= 2
                bottom *= 2
                left *= 2

                cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0) if user_id != "Unknown" else (0, 0, 255), 2)
                cv2.putText(frame, f"{user_id} ({accuracy:.2f}%)",
                            (left, top - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0) if user_id != "Unknown" else (0, 0, 255), 2)

                # Log attendance if recognized
                if user_id != "Unknown":
                    self.log_attendance(user_id, accuracy)

            cv2.imshow('Video', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        video_capture.release()
        cv2.destroyAllWindows()

    def log_attendance(self, user_id, accuracy):
        timestamp = datetime.datetime.now(pytz.UTC)  # Use UTC timezone for consistency
        print(f"Attendance logged for {user_id} at {timestamp} with accuracy {accuracy:.2f}%")

        # Log to CSV
        with open(self.log_file, mode='a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([user_id, timestamp, f"{accuracy:.2f}%"])


# test light setting
face_recognition_attendance = FaceRecognitionAttendance(dataset_path="originalData/dataset_faces")
face_recognition_attendance.process_video_file("dark_setting.mov")
