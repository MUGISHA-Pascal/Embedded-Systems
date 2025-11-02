int buzzerpin=12;
void setup()
{
  pinMode(11, OUTPUT);
  pinMode(10, OUTPUT);
  pinMode(9, OUTPUT);
  pinMode(buzzerpin, OUTPUT);
  pinMode(A0, OUTPUT);
  pinMode(A1, INPUT);
}

void loop()
{
  digitalWrite(A0,HIGH);
  delay(10);
  int sensorreading=analogRead(A1);
  digitalWrite(A0,LOW);
  if (sensorreading<300){
    digitalWrite(11,HIGH);
    digitalWrite(10,LOW);
    digitalWrite(9,LOW);
    digitalWrite(buzzerpin,LOW);
  }else if(sensorreading<600){
      digitalWrite(10,HIGH);
    digitalWrite(11,LOW);
    digitalWrite(9,LOW);
    digitalWrite(buzzerpin,LOW);
  }else {
     digitalWrite(9,HIGH);
    digitalWrite(11,LOW);
    digitalWrite(10,LOW);
    digitalWrite(buzzerpin,HIGH);
  }
  delay(1000);
}