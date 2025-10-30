int ledcount=9;
int sensorpin=A0;
int ledpins[]={2,3,4,5,6,7,8,9,10};
void setup()
{
  for(int pin=0;pin<ledcount;pin++){
  pinMode(ledpins[pin], OUTPUT);
  }
}

void loop()
{
 int sensorreading=analogRead(sensorpin);
 int ledlevel=map(sensorreading,0,1023,0,ledcount);
  for(int pin=0;pin<ledcount;pin++){
    if(pin<ledlevel){
      digitalWrite(ledpins[pin],HIGH);
    }  else{
    digitalWrite(ledpins[pin],LOW);
    }
  }
}