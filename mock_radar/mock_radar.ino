// Mock device generating serial output with timestamp and fluctuating distances

unsigned long previousMillis = 0;
const unsigned long interval = 100; // Time interval between updates in milliseconds

int movingDistance = 50; // Initial moving object distance (in cm)
int stationaryDistance = 40; // Initial stationary object distance (in cm)

void setup() {
  Serial.begin(256000); // Set the baud rate
}

void loop() {
  unsigned long currentMillis = millis();

  // Check if it's time to send new data
  if (currentMillis - previousMillis >= interval) {
    previousMillis = currentMillis;

    // Generate timestamp
    String timestamp = getTimestamp();

    // Update distances with slight fluctuations
    movingDistance = updateDistance(movingDistance);
    stationaryDistance = updateDistance(stationaryDistance);

    // Print mock output
    Serial.println(timestamp + " -> OUT pin status: HIGH (Presence detected)");
    Serial.println(timestamp + " -> Motion detected via UART!");
    Serial.println(timestamp + " -> Moving object at distance: " + String(movingDistance) + " cm");
    Serial.println(timestamp + " -> Stationary object at distance: " + String(stationaryDistance) + " cm");
    Serial.println(timestamp + " -> --------------------");
  }
}

// Function to generate a timestamp based on millis()
String getTimestamp() {
  unsigned long ms = millis();
  unsigned long seconds = ms / 1000;
  unsigned long minutes = seconds / 60;
  unsigned long hours = minutes / 60;

  char buffer[20];
  snprintf(buffer, sizeof(buffer), "%02lu:%02lu:%02lu.%03lu",
           hours % 24, minutes % 60, seconds % 60, ms % 1000);
  return String(buffer);
}

// Function to update distance with slight random fluctuations
int updateDistance(int currentDistance) {
  int change = random(-5, 6); // Random change between -5 and +5 cm
  int newDistance = currentDistance + change;

  // Clamp the distance to a realistic range (e.g., 20 to 100 cm)
  if (newDistance < 20) newDistance = 20;
  if (newDistance > 100) newDistance = 100;

  return newDistance;
}
