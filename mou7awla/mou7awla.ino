#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Initialize the LCD with the I2C address 0x27 (change if needed)
LiquidCrystal_I2C lcd(0x27, 16, 2);  // 16 columns and 2 rows

int sensor1 = 7;  // Pin for sensor 1
bool detected = false;  // Flag to indicate if an object has been detected
unsigned long detectionTime = 0;  // Timestamp for detection
const unsigned long resetDelay = 5000;  // Time in milliseconds to reset detection
char receivedData[100];
int dataIndex = 0;
void setup() {
  pinMode(sensor1, INPUT);  // Set sensor 1 pin as input
  Serial.begin(9600);  // Start serial communication at 9600 baud
  lcd.init();  // Initialize the LCD
  lcd.setBacklight(1);  // Turn on the backlight
  lcd.setCursor(0, 0);  // Set cursor to the first column of the first row
  lcd.print("LCD Initialized");  // Print test message on LCD
  
  delay(2000);  // Wait for 2 seconds to see the test message on LCD
  lcd.clear();   // Clear the LCD after the test message
}
void loop() {
  int state1 = digitalRead(sensor1);  // Read the state of sensor 1

  if (!detected) {
    if (state1 == LOW) {  // Object detected
      detected = true;
      detectionTime = millis();
      Serial.println("START");  // Send the "START" signal
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Object detected!");
      lcd.setCursor(0, 1);
      lcd.print("Waiting for PC");
    }
  } else {
    if (Serial.available() > 0) {
      // Read the incoming data
      char incomingByte = Serial.read();
      
      // If a newline character is received, process the full message
      if (incomingByte == '\n') {
        receivedData[dataIndex] = '\0';  // Null-terminate the string
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Plate Number:");
        lcd.setCursor(0, 1);
        lcd.print(receivedData);  // Display the received data
        delay(10000);  // Keep the data displayed for 5 seconds

        // Reset the variables for the next detection
        dataIndex = 0;
        detected = false;
        lcd.clear();
        lcd.setCursor(0, 0);
        lcd.print("Ready for next");
        lcd.setCursor(0, 1);
        lcd.print("detection");
      } else {
        if (dataIndex < sizeof(receivedData) - 1) {
          receivedData[dataIndex] = incomingByte;
          dataIndex++;
        }
      }
    }

    // Timeout for resetting detection if no data received
    if (millis() - detectionTime >= resetDelay) {
      detected = false;
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("Ready for next");
      lcd.setCursor(0, 1);
      lcd.print("detection");
    }
  }
}

/*#include <Wire.h>
#include <LiquidCrystal_I2C.h>

// Set up the LCD. Address 0x27 is common for I2C LCDs.
LiquidCrystal_I2C lcd(0x27, 16, 2);

// Pin 7 is used for the sensor input
const int sensorPin = 7;

void setup() {
  // Start serial communication with the Python script
  Serial.begin(9600);
 lcd.init();  // Initialize the LCD
  lcd.setBacklight(1);  // Turn on the backlight
  lcd.setCursor(0, 0);  // Set cursor to the first column of the first row
  lcd.print("LCD Initialized");  // Print test message on LCD
  
  delay(2000);  // Wait for 2 seconds to see the test message on LCD
  lcd.clear();   // Clear the LCD after the test message
  
  // Set sensorPin as input
  pinMode(sensorPin, INPUT);
}

void loop() {
  // Read the sensor value (assuming it's a digital sensor)
  int sensorValue = digitalRead(sensorPin);

  if (sensorValue == LOW) {
    // If the sensor is triggered, send the "START" signal
    Serial.println("START");
    
    // Display a message on the LCD to indicate waiting for data
    lcd.clear();
    lcd.setCursor(0, 0);
    lcd.print("Waiting for data...");
    
    // Wait for data from Python (e.g., the license plate number)
    if (Serial.available() > 0) {
      // Read the license plate number sent from Python
      String licensePlate = Serial.readString();
      
      // Clear LCD and display the license plate number
      lcd.clear();
      lcd.setCursor(0, 0);
      lcd.print("License Plate:");
      lcd.setCursor(0, 1);
      lcd.print(licensePlate); // Display the license plate number
      
      // Wait for a while before checking the sensor again
      delay(5000); // Display the license plate for 5 seconds
    }
  }
  
  // Delay to avoid excessive sensor polling
  delay(100);
}
*/
