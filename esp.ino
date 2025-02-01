#include <ESP8266WiFi.h>
// #include <MQTTClient.h>
#include <MQTT.h>

#define LEFT_WHEEL D4
#define RIGHT_WHEEL D6
#define LEFT_WHEEL_DIRECTION D5 //?
#define RIGHT_WHEEL_DIRECTION D7 //?

const char WIFI_SSID[] = "Damn_TCPY";
const char WIFI_PASSWORD[] = "MQTTT-1";

const char MQTT_BROKER_ADRRESS[] = "192.168.0.15";
const int MQTT_PORT = 1883;
const char MQTT_CLIENT_ID[] = "esp";
const char MQTT_USERNAME[] = "";
const char MQTT_PASSWORD[] = "";

const char PUBLISH_TOPIC[] = "esp";
const char SUBSCRIBE_TOPIC[] = "rasp";

const int PUBLISH_INTERVAL = 5000;

WiFiClient network;
MQTTClient mqtt = MQTTClient(256);

void setup() {
  Serial.begin(9600);

  pinMode(D4, OUTPUT);
  pinMode(D5, OUTPUT);
  pinMode(D6, OUTPUT);
  pinMode(D7, OUTPUT);

  int status = WL_IDLE_STATUS;
  while (status != WL_CONNECTED) {
    Serial.print("Arduino - Attempting to connect to SSID: ");
    Serial.println(WIFI_SSID);
    status = WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    delay(5000);
  }

  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  connectToRB();

  sendToRB("hi");
}

void loop() {
  mqtt.loop();
}

void connectToRB() {
  mqtt.begin(MQTT_BROKER_ADRRESS, MQTT_PORT, network);

  mqtt.onMessage(messageHandler);

  Serial.print("Arduino - Connecting to MQTT broker");

  while (!mqtt.connect(MQTT_CLIENT_ID, MQTT_USERNAME, MQTT_PASSWORD)) {
    Serial.print(".");
    delay(100);
  }
  Serial.println();

  if (!mqtt.connected()) {
    Serial.println("Arduino - MQTT broker Timeout!");
    return;
  }

  if (mqtt.subscribe(SUBSCRIBE_TOPIC)){
    Serial.print("Arduino - Subscribed to the topic: ");
  } else {
    Serial.print("Arduino - Failed to subscribe to the topic: ");
  }

  Serial.println(SUBSCRIBE_TOPIC);
  Serial.println("Arduino - MQTT broker Connected!");
}

void sendToRB(const String &data) {
  mqtt.publish(PUBLISH_TOPIC, data);

  Serial.print("Arduino - sent to MQTT:");
  Serial.println(data);
}

void messageHandler(String &topic, String &payload) {
  if (payload == "forward"){
    move();
  }
}

void move(){
    sendToRB("ok forward");  // why just don't use json?

    while (!enoughDistance){
        digitalWrite(LEFT_WHEEL, HIGH);
        digitalWrite(RIGHT_WHEEL, HIGH);
    }

    digitalWrite(LEFT_WHEEL, LOW);
    digitalWrite(RIGHT_WHEEL, LOW);

    sendToRB("done forward");  // why just don't use json?
}

bool enoughDistance(){
    return false;
}
