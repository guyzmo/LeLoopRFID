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

byte mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
byte ip[] = { 192, 168, 42, 242 };
byte server[] = { 192, 168, 42, 100}; 

Client client(server, 42000);

SL018 rfid;

#define YES_DOOR 42

const int PIN_RED=9;
const int PIN_GREEN=8;
const int PIN_SND=6;
const int PIN_DOOR=7;

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
    tone(PIN_SND, 988);
    delay(80);
    tone(PIN_SND, 1319);
    delay(240);
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

void low_beep(int len) {
  //tone(PIN_SND,440);
  //delay(len);
  //noTone(PIN_SND);
}

void set_green(){
    digitalWrite(PIN_GREEN,HIGH);
}
void set_red(){
    digitalWrite(PIN_RED,HIGH);
}
void reset_leds(){
    digitalWrite(PIN_GREEN,LOW);
    digitalWrite(PIN_RED,LOW);
}

void ether_setup()
{
  set_green();
  Serial.println("ether init...");
  Ethernet.begin(mac, ip);
  
  delay(1000);
  reset_leds();
  set_red();
  low_beep(250);
}

void open_door() {
    Serial.println("Door Opened");
    set_green();
    digitalWrite(PIN_DOOR, HIGH);
    delay(500);
    digitalWrite(PIN_DOOR, LOW);
    mushroom_beep();
    reset_leds();
}

void verify_entrance(const char* uid) {
  Serial.println("connecting...");
  
  if (client.connect()) {
    Serial.println("connected");
    client.print("GET /uid/");
    client.print(uid);
    client.println(" HTTP/1.0");
    client.println();
    Serial.print("uid sent:");
    Serial.println(uid);
    if (client.available()) {
        char c;
        Serial.println("returned value: ");
        while (client.available()) {
            c = client.read();
            Serial.print(c);
        }
        if (c == '1') {
            open_door();
            Serial.println("success");
        } else {
            set_red();
            death_beep();
            delay(2000);
            Serial.println("failed");
        }
        reset_leds();

    }
  } else {
    Serial.println("connection failed");
    low_beep(1000);
  }
  client.stop();
}

void setup()
{
  pinMode(3,INPUT);
  digitalWrite(3,HIGH);

  pinMode(9,OUTPUT);
  pinMode(8,OUTPUT);
  pinMode(7,OUTPUT);

  Wire.begin();
  Serial.begin(19200);

  noTone(PIN_SND);

  ether_setup();
  reset_leds();

  coin_beep();
  delay(500);
}

void loop()
{
  // start seek mode
  rfid.seekTag();
  // wait until tag detected
  if (rfid.available()) {
    coin_beep();
#ifdef YES_DOOR
    open_door();
#else
  verify_entrance(rfid.getTagString());
#endif
  }
  if (digitalRead(3) == LOW) {
    open_door();
    while (digitalRead(3) == LOW);
  }
}

