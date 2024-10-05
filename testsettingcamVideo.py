import cv2
import time

def record_video(output_file="output.mov", duration=120, frame_rate=20):
    # Open the default webcam (usually index 0)
    cap = cv2.VideoCapture(0)

    # Get the width and height of the frame
    frame_width = int(cap.get(3))
    frame_height = int(cap.get(4))

    # Define the codec and create VideoWriter object to save as a .mov file
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')  # Using 'mp4v' codec for .mov
    out = cv2.VideoWriter(output_file, fourcc, frame_rate, (frame_width, frame_height))

    # Record start time
    start_time = time.time()

    while True:
        ret, frame = cap.read()
        if ret:
            # Write the frame into the file
            out.write(frame)

            # Display the frame
            cv2.imshow('Recording Video', frame)

            # Break if the 'q' key is pressed
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

            # Stop recording after the specified duration (in seconds)
            if time.time() - start_time >= duration:
                break
        else:
            print("Failed to capture video.")
            break

    # Release the capture and writer objects and close the display window
    cap.release()
    out.release()
    cv2.destroyAllWindows()

# Example usage: record a 5 sec video and save it as output.mov
record_video(output_file="output.mov", duration=50, frame_rate=20)
