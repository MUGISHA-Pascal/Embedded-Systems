int potpin=A0;
int potvalue=0;
int led=9;

void setup(){
pinMode(led,OUTPUT);
pinMode(potpin,INPUT);
}

void loop(){
 potvalue=analogRead(potpin);
  analogWrite(led,potvalue/4);
}