import cv2
import numpy as np
import serial
import time
import tensorflow as tf

# Connect to Arduino
arduino = serial.Serial("COM5", 9600)
time.sleep(2)

# Load TensorFlow Lite model
interpreter = tf.lite.Interpreter(model_path="model_unquant.tflite")
interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Load labels
with open("labels.txt", "r") as f:
    class_names = f.readlines()

# Start webcam
camera = cv2.VideoCapture(0)

last_command = ""

while True:
    ret, frame = camera.read()

    if not ret:
        print("Could not read camera.")
        break

    # Prepare image for Teachable Machine
    image = cv2.resize(frame, (224, 224))
    image = np.asarray(image, dtype=np.float32)
    image = (image / 127.5) - 1
    image = np.expand_dims(image, axis=0)

    # Run AI model
    interpreter.set_tensor(input_details[0]["index"], image)
    interpreter.invoke()

    prediction = interpreter.get_tensor(output_details[0]["index"])[0]

    index = np.argmax(prediction)
    confidence = prediction[index]

    class_name = class_names[index].strip()
    label = class_name.split(" ", 1)[-1]

    # Show prediction on camera
    cv2.putText(
        frame,
        f"{label}: {confidence * 100:.1f}%",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 0),
        2
    )

    # Control servo when confidence is above 90%
    if confidence > 0.90:

        if label.lower() == "open hand":
            if last_command != "O":
                arduino.write(b'O')
                print("OPEN HAND -> UNLOCKED")
                last_command = "O"

        elif label.lower() == "closed hand":
            if last_command != "C":
                arduino.write(b'C')
                print("CLOSED HAND -> LOCKED")
                last_command = "C"

        elif label.lower() == "nothing":
            last_command = ""

    cv2.imshow("AI Servo Lock", frame)

    # Press Q to quit
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

camera.release()
arduino.close()
cv2.destroyAllWindows()