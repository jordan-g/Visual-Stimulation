int scopePin = 1; // pin for receiving a signal from the scope
int startPin = 0; // pin for sending a start signal
int pulsePin = 13; // pin for sending pulses

// TTL parameters
int pulseDelay = 500;
int pulseFrequency = 5;
int pulseWidth = 5;
int pulseDuration = 5;
int pulseNumber = (int) pulseDuration*pulseFrequency;
int pulseOffset = (int) 1000/pulseFrequency;

// pulse count initialization
int pulseCount = 0;
bool startPulseCount = false;

void setup()
{
  // set up pins
  pinMode(startPin, OUTPUT);
  pinMode(pulsePin, OUTPUT);
  Serial.begin(9600);

  // print TTL parameters
  Serial.print("TTL Delay (ms): ");
  Serial.println(pulseDelay);
  Serial.print("TTL Frequency (Hz): ");
  Serial.println(pulseFrequency);
  Serial.print("TTL Pulse Width (ms): ");
  Serial.println(pulseWidth);
  Serial.print("TTL Duration (ms): ");
  Serial.println(pulseDuration);
  Serial.print("# of TTL Pulses: ");
  Serial.println(pulseNumber);
  Serial.print("Time Between TTL Pulses: ");
  Serial.println(pulseOffset);

  // wait for delay
  delay(pulseDelay);
  
  // start TTL pulsing
  startPulseCount = true;
}

void loop()
{
//  int scopeReading = analogRead(scopePin);
//  float scopeVoltage = scopeReading / 204.6;
//  Serial.print("Scope reading = ");
//  Serial.print(scopeReading);
//  Serial.print("\t\tScope volts = ");
//  Serial.println(scopeVoltage);
//  
//  if (scopeVoltage == 5.0) {
//    // start stimulation
//    digitalWrite(startPin, HIGH);
//    Serial.println("Sending start signal.");
//
//    if (startPulseCount == false) {
//      // wait for delay
//      delay(pulseDelay);
//  
//      // start TTL pulse
//      startPulseCount = true;
//    }
//  }
  
  if (startPulseCount == true) {
    // do a pulse
    digitalWrite(pulsePin, HIGH);
    delay(pulseWidth);
    digitalWrite(pulsePin, LOW);
    delay(pulseOffset - pulseWidth);

    // increment pulse count
    pulseCount ++;

    // print current pulse
    Serial.print("Sending pulse ");
    Serial.println(pulseCount);

    // stop pulsing if we reach the total # of pulses
    if (pulseCount == pulseNumber) {
      pulseCount = 0;
      startPulseCount = false;
    }
  }

}