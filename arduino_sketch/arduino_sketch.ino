int analogPin = 1;
int val = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(250000);
}

void loop() {
  // put your main code here, to run repeatedly:
  val = analogRead(analogPin);
  Serial.println(val);
}
