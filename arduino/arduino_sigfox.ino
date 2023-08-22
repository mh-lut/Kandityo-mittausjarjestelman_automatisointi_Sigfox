// ------------------------------
// Program name: arduino_sigfox.ino
// Description: Message sending program
// Date: 10.8.2023
// Notes: This is part of the automated measurement system (sigfox)
// Sources: https://docs.arduino.cc/tutorials/mkr-fox-1200/sigfox-first-configuration
// Device: Arduino MKRFOX 1200
// ------------------------------


#include <SigFox.h>

void setup() {
  Serial.begin(115200);
}

void loop() {
  while (!Serial.available()); // Wait serial

  String message;
  char inchar;
  bool start = false;
  bool endchar = false;

  while (Serial.available() && !start) { // Check start

    inchar = (char)Serial.read();
    
    if (inchar == ':') {
      start = true;
    }
  }

  while (Serial.available() && !endchar) { // Collecting the message until the stop char "x"

    inchar = (char)Serial.read(); // Read char

    if (inchar == 'x') {
      endchar = true;
    } else {
      message += inchar; // Add char to message
    }
  }

  message.trim();

  if (start && endchar) {
    sendString(message);
  }
}

// https://docs.arduino.cc/tutorials/mkr-fox-1200/sigfox-first-configuration
void sendString(String str) {

  SigFox.begin();

  delay(100); // Wait at least 30mS after first configuration (100mS before)

  //Clears all pending interrupts

  SigFox.status();

  delay(1);

  SigFox.beginPacket(); // Start packet

  SigFox.print(str); // Add the mesasge string

  int ret = SigFox.endPacket(); // Send buffer to SIGFOX network

  Serial.println(ret); // Send transmission status number

  SigFox.end();
}