/**
 *  @title:  RFID door control system for the Loop
 *  @author: Guyzmo <guyzmo at leloop dot org>
 *  @see:    http://www.stronglink.cn/english/sl030.htm
 *  @see:    http://github.com/guyzmo/LeLoopRFID
 *  @see:    http://wiki.leloop.org/index.php/LeLoopRFID
 *
 *  Arduino to SL018/SL030 wiring:
 *  A4/SDA     2     3
 *  A5/SCL     3     4
 *  5V         4     -
 *  GND        5     6
 *  3V3        -     1
 */

#include <Wire.h>
#include <SL018.h>

#include <Ethernet.h>

SL018 rfid;

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
byte ip[] = { 192, 168, 42, 242 };

Server server = Server(23);

#define YES_DOOR 42

const int PIN_LED=8;
const int PIN_SND=9;
const int PIN_DOOR=2;

void death_beep() {
    tone(PIN_SND, 880);
    delay(80);
    tone(PIN_SND, 300);
    delay(120);
    tone(PIN_SND, 880);
    delay(80);
    tone(PIN_SND, 300);
    delay(120);
    noTone(PIN_SND);
}

void coin_beep() {
    tone(PIN_SND, 988);
    delay(80);
    tone(PIN_SND, 1319);
    delay(200);
    noTone(PIN_SND);
}

void mushroom_beep() {
    tone(PIN_SND, 165);
    delay(80);
    tone(PIN_SND, 196);
    delay(80);
    tone(PIN_SND, 329);
    delay(80);
    tone(PIN_SND, 262);
    delay(80);
    tone(PIN_SND, 277);
    delay(80);
    tone(PIN_SND, 392);
    delay(80);
    noTone(PIN_SND);
}

void high_beep(int len) {
  tone(PIN_SND,440);
  delay(len);
  tone(PIN_SND,880);
  delay(len);
  tone(PIN_SND,1000);
  delay(len);
  tone(PIN_SND,1400);
  delay(len);
  noTone(PIN_SND);
}

void set_led(){
    digitalWrite(PIN_LED,HIGH);
}
void reset_led(){
    digitalWrite(PIN_LED,LOW);
}

void open_door() {
    Serial.println("Door Opened");
    pinMode(7,OUTPUT);
    digitalWrite(PIN_DOOR, LOW);
    delay(500);
    pinMode(7,INPUT);
}

void ether_setup() {
  set_led();
  Serial.println("ether init...");
  Ethernet.begin(mac, ip);
  server.begin();
  
  delay(1000);
  reset_led();
}

void setup()
{
  //pinMode(3,INPUT);
  //digitalWrite(3,HIGH);

  pinMode(PIN_LED,OUTPUT);
  pinMode(PIN_DOOR,INPUT);

  Wire.begin();
  Serial.begin(19200);

  noTone(PIN_SND);

  ether_setup();

  reset_led();

  coin_beep();
  delay(500);
}

void verify_entrance() {
    return;
}

void loop()
{
  char c='0';

  Client client = server.available();
  while (client.connected()) {

      rfid.seekTag();
      if (rfid.available()) {
          coin_beep();
          Serial.println("card in");
          client.print("CARD ");
          client.println(rfid.getTagString());
      }

      if (client.available()) {
          Serial.println("client available");
          c = client.read();
      } else {
          c = '0'
      }

      if (c == '1') {
          //server.write("OPEN\n");
          Serial.println("OPEN");
          set_led();
          open_door();
          if (c == '1')
            mushroom_beep();
          else
            delay(1000);
          reset_led();
          //server.write("CLOSE\n");
      } else if (c == '0') {
          Serial.println("DENIED");
          set_led();
          delay(500);
          reset_led();
          delay(500);
          set_led();
          delay(500);
          reset_led();
          if (c == 'F')
            death_beep();
      } else if (c == 'I') {
          death_beep();
          server.write("System initialized. Please enter the loop.\n");
          Serial.println("Init...");
      }
  } 

  if (!client.connected()) {
      Serial.println("disconnected");
      client.stop();
  }
}
