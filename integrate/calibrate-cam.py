import cv2

# Initialize the video capture
cap = cv2.VideoCapture(0)

# Check if the video capture is opened successfully
if not cap.isOpened():
    print("Error: Could not open video capture.")
    exit()

# Loop over frames from the video capture
while True:
    # Read a frame from the video capture
    ret, frame = cap.read()

    # If the frame was not read correctly, break from the loop
    if not ret:
        break

    # Display the frame
    cv2.imshow("Video Stream", frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture and close all OpenCV windows
cap.release()
cv2.destroyAllWindows()