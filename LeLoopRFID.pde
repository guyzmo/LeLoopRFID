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

uint8_t mac[] = { 0xDE, 0xAD, 0xBE, 0xEF, 0xFE, 0xED };
uint8_t ip[] = { 192, 168, 42, 242 };
uint8_t ip_serv[] = { 192, 168, 42, 42};

Server rfid_serv = Server(4242);
Client db_client = Client(ip_serv, 4242);

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
    rfid_serv.begin();

    delay(1000);
    reset_led();
}

void setup()
{

    pinMode(PIN_LED,OUTPUT);
    pinMode(PIN_DOOR,INPUT);
    digitalWrite(PIN_DOOR,HIGH);

    Wire.begin();
    Serial.begin(19200);

    noTone(PIN_SND);

    ether_setup();

    reset_led();

    coin_beep();
    delay(500);
}

void loop()
{
    char c='Z';

    Client rfid_client = rfid_serv.available();

    if (rfid_client.connected()) {
        if (rfid_client.available()) {
            Serial.println("rfid_client available");
            c = rfid_client.read();
            if (c == '1') {
                //rfid_serv.write("OPEN\n");
                Serial.println("OPEN");
                set_led();
                open_door();
                mushroom_beep();
                reset_led();
                //rfid_serv.write("CLOSE\n");
            } else if (c == '0') {
                Serial.println("DENIED");
                set_led();
                delay(500);
                reset_led();
                delay(500);
                set_led();
                delay(500);
                reset_led();
            }
        }
        rfid_client.stop();
    } 

    // je cherche un tag
    rfid.seekTag();
    if (rfid.available()) {
        coin_beep();
        Serial.println("card in");
        if (!db_client.connect()) {
            Serial.println("connection to db failed.");
            db_client.stop();
            return;
        }
        Serial.println("id sent");
        // on retourne l'id de tag a l'hote
        db_client.print("CARD ");
        db_client.println(rfid.getTagString());
        db_client.stop();
    } 

}

