import serial
import time
import cv2
from matplotlib import pyplot as plt
import numpy as np
import imutils
import easyocr
import re

def capture_image_from_camera():
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Camera not accessible.")
        return None

    ret, frame = cap.read()
    cap.release()

    if ret:
        return frame
    else:
        print("Error: Failed to capture image.")
        return None

def process_image(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    bfilter = cv2.bilateralFilter(gray, 11, 17, 17)
    edged = cv2.Canny(bfilter, 30, 200)

    keypoints = cv2.findContours(edged.copy(), cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    contours = imutils.grab_contours(keypoints)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)[:10]

    location = None
    for contour in contours:
        approx = cv2.approxPolyDP(contour, 10, True)
        if len(approx) == 4:
            location = approx
            break

    if location is not None:
        mask = np.zeros(gray.shape, np.uint8)
        new_image = cv2.drawContours(mask, [location], 0, 255, -1)
        new_image = cv2.bitwise_and(image, image, mask=mask)

        (x, y) = np.where(mask == 255)
        (x1, y1) = (np.min(x), np.min(y))
        (x2, y2) = (np.max(x), np.max(y))
        cropped_image = gray[x1:x2+1, y1:y2+1]

        reader = easyocr.Reader(['en', 'ar'])
        result = reader.readtext(cropped_image)

        return result
    else:
        print("License plate not found.")
        return None

def run_image_processing(ser):  # Accept 'ser' as an argument
    image = capture_image_from_camera()
    if image is not None:
        result = process_image(image)
        if result:
            sorted_result = sorted(result, key=lambda detection: detection[0][0][0], reverse=True)
            license_plate_numbers = []
            for detection in sorted_result:
                text = detection[1]
                numbers = re.findall(r'\d+', text)
                license_plate_numbers.extend(numbers)
#------------------------naama-----------------------------------------
            if license_plate_numbers:
                output = "TUN".join(reversed(license_plate_numbers))
                print(output)  # Output only the numbers
                print(f"Sending data: {output}")
                ser.write((output + '\n').encode('utf-8'))
                  # Optional feedback
            else:
                print("No numbers found.")
#----------------------------------------------------------------------
def listen_for_start_signal():
    try:
        print("Connecting to serial port...")
        ser = serial.Serial('COM6', 9600, timeout=1)
        if ser.is_open:
            print("Serial port opened successfully!")
    except Exception as e:
        print(f"Error opening serial port: {e}")
        return

    print("Waiting for data from Arduino...")
    try:
        while True:
            if ser.in_waiting > 0:
                data = ser.readline().decode('utf-8').strip()
                print(f"Received data: {data}")
                if data == "START":
                    print("START signal received, running image processing...")
                    run_image_processing(ser)  # Pass 'ser' to the function
                    break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Reading interrupted by user.")
    finally:
        ser.close()
        print("Serial connection closed.")

if __name__ == "__main__":
    listen_for_start_signal()

"""
def run_image_processing():
    # Capture an image from the camera
    image = capture_image_from_camera()

    if image is not None:
        # Process the captured image
        result = process_image(image)
        if result:
            # Sort the results by the x-coordinate of the bounding box to maintain right-to-left order
            sorted_result = sorted(result, key=lambda detection: detection[0][0][0], reverse=True)  # Sort by x-coordinate in descending order

            # Extract the numbers and sort them by length (3-digit numbers first, then 4-digit numbers)
            sorted_numbers = []
            for detection in sorted_result:
                # Each detection is a list: [bounding box, recognized text, confidence score]
                text = detection[1]
                # Use regular expression to filter only numeric text (digits)
                numbers = re.findall(r'\d+', text)
                for number in numbers:
                    sorted_numbers.append(number)  # Add the number to the list

            # Now sort the numbers: first by length (3-digit numbers first, then 4-digit numbers)
            sorted_numbers.sort(key=lambda x: (len(x), x), reverse=True)

            # Extract t1 and t2 (first 3-digit and 4-digit number)
            t1 = None
            t2 = None
            for number in sorted_numbers:
                if len(number) == 3 and t1 is None:
                    t1 = number
                elif len(number) == 4 and t2 is None:
                    t2 = number

            # Print the extracted values of t1 and t2
            if t1 and t2:
                print(f"{t1} {t2}")
            else:
                print("Erreur: Valeurs non trouvées")
"""



