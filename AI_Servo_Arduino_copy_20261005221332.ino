#include <Servo.h>

Servo myServo;

void setup() {
  Serial.begin(9600);
  myServo.attach(9);
  myServo.write(0);
}

void loop() {
  if (Serial.available() > 0) {
    char command = Serial.read();

    if (command == 'O') {
      myServo.write(90);
    }

    if (command == 'C') {
      myServo.write(0);
    }
  }
}