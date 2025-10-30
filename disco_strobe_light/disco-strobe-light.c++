int sensorpin=A0;
int parallel1=12;
int parallel2=13;
void setup()
{
  pinMode(12, OUTPUT);
  pinMode(13, OUTPUT);
}

void loop()
{
  int sensorreading=analogRead(sensorpin);
  int timer=map(sensorreading,0,1023,10,500);
  digitalWrite(12, HIGH);
  delay(timer);
  digitalWrite(12, LOW);
  delay(timer);
  digitalWrite(13, HIGH);
  delay(timer);
   digitalWrite(13, LOW);
  delay(timer);
}