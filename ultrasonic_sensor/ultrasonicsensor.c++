#include <LiquidCrystal_I2C.h>

 LiquidCrystal_I2C lcd(0x27,16,2);

int trigPin = 13; 
int echoPin = 12;   
float duration_us, distance_cm; 
void setup() { 
  lcd.init();              
  lcd.backlight();         
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);   
} 
void loop() {
  int rawData = analogRead(A5);
  
  digitalWrite(trigPin, HIGH); 
  delayMicroseconds(10); 
  digitalWrite(trigPin, LOW); 
  
  duration_us = pulseIn(echoPin, HIGH); 
  distance_cm = (duration_us/2) * (1/29.1);
  
  lcd.clear(); 
  lcd.setCursor(0, 0); 
  lcd.print("You're: "); 
  lcd.print(distance_cm); 
  lcd.print("cm"); 
  delay(500); 
} 