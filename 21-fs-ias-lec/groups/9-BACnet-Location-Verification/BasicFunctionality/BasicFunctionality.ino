#include <SPI.h>
#include <MFRC522.h>
#include <LiquidCrystal_I2C.h>
#include <SoftwareSerial.h>
#include <TinyGPS++.h>

constexpr uint8_t SS_PIN = 10;
constexpr uint8_t RST_PIN = 9;


// Define variables
LiquidCrystal_I2C lcd(0x27,16,2);
MFRC522 mfrc522(SS_PIN, RST_PIN);  // Create MFRC522 instance
SoftwareSerial ss(4, 3); // RX, TX - inverse on arduino board because output routes to input!
TinyGPSPlus gps;
float longitude;
float latitude;
boolean gpsFix = false; // GPS Fix := Reliable geoposition information based on visible satellites

void setup(){
  lcd.init();
  lcd.backlight();
  
  Serial.begin(9600);
  ss.begin(9600);

  while (!Serial);    // Do nothing if no serial port is opened (added for Arduinos based on ATMEGA32U4)
  SPI.begin();      // Init SPI bus
  mfrc522.PCD_Init();   // Init MFRC522
  mfrc522.PCD_DumpVersionToSerial();  // Show details of PCD - MFRC522 Card Reader details
  printGpsData();
}

void loop(){
  // Check whether a RFID Tag/Card has been detected
  if (mfrc522.PICC_IsNewCardPresent() && mfrc522.PICC_ReadCardSerial()) {
      // Print UID onto Serial and LCD  
      if (gps.encode(ss.read())){
        updateGpsData();
      }
      lcd.clear();
      lcd.setCursor(0,0);
      lcd.print("Card UID:");
      Serial.print(F("x1uid"));
      dump_byte_array(mfrc522.uid.uidByte, mfrc522.uid.size);
      Serial.println("");
      
      mfrc522.PICC_HaltA();       // Halt PICC
      mfrc522.PCD_StopCrypto1();  // Stop encryption on PCD
      delay(1000);                // Delay to give user time to acknoswledge that tag has been read
      printGpsData();             // Return LCD to usual display information
  }

  while (ss.available() > 0){
    if (gps.encode(ss.read())){
        updateGpsData();
      }
  }
}

// UID is given in bytes, this function decodes bytes into hex values for display and prints them
void dump_byte_array(byte *buffer, byte bufferSize) {
  int cursorLoc = 0;
  for (byte i = 0; i < bufferSize; i++) {
    lcd.setCursor(cursorLoc, 1);
    lcd.print(buffer[i] < 0x10 ? " 0" : " ");
    lcd.print(buffer[i], HEX);
    Serial.print(buffer[i] < 0x10 ? " 0" : " ");
    Serial.print(buffer[i], HEX);
    cursorLoc += 3; 
  }
}


void updateGpsData() { 
  if (gps.location.isValid() && gps.location.isUpdated())
  {
    gpsFix = true;
    
    Serial.print("x2lon");         //Used to identify the information 
                                   //type in python script
    longitude = gps.location.lng();
    Serial.print(longitude,4);     
    Serial.println("");

    Serial.print("x3lat");
    latitude = gps.location.lat();
    Serial.print(latitude,4);
    Serial.println("");
  }
}

void printGpsData() {
  if(!gpsFix){
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Waiting for");
    lcd.setCursor(0,1);
    lcd.print("GPS Signal...");
  } else {
    lcd.clear();
    lcd.setCursor(0,0);
    lcd.print("Lng: ");
    lcd.print(longitude, 6);
    lcd.setCursor(0,1);
    lcd.print("Lat: ");
    lcd.print(latitude, 6);
  }
}
