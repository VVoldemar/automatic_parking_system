#include <ESP8266WiFi.h>
// #include <MQTTClient.h>
#include <MQTT.h>

#define LEFT_WHEEL D5
#define RIGHT_WHEEL D6
#define LEFT_WHEEL_DIRECTION D4 //?
#define RIGHT_WHEEL_DIRECTION D7 //?

#define SOUND_SPEED 0.034

const char WIFI_SSID[] = "MQTTT-1";
const char WIFI_PASSWORD[] = "11223344";

const char MQTT_BROKER_ADRRESS[] = "10.42.0.1";
const int MQTT_PORT = 1883;
const char MQTT_CLIENT_ID[] = "esp";
const char MQTT_USERNAME[] = "";
const char MQTT_PASSWORD[] = "";

const char PUBLISH_TOPIC[] = "esp";
const char SUBSCRIBE_TOPIC[] = "rasp";

const int PUBLISH_INTERVAL = 1000;

const int trigPin = D2;
const int echoPin = D3;

WiFiClient network;
MQTTClient mqtt = MQTTClient(256);

unsigned long lastPublishTime = 0;

int FORWARD_STOP_DISTANCE = 5;
int BACKWARD_STOP_DISTANCE = 5;

void setup() {
  Serial.begin(9600);

  pinMode(D4, OUTPUT);
  pinMode(D5, OUTPUT);
  pinMode(D6, OUTPUT);
  pinMode(D7, OUTPUT);
  pinMode(trigPin, OUTPUT);
  pinMode(echoPin, INPUT);

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

  if (millis() - lastPublishTime > PUBLISH_INTERVAL) {
    sendToRB(String(millis()));
    lastPublishTime = millis();
  }
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

void setConfig(String &payload) {
  // parse the payload and set the config
  FORWARD_STOP_DISTANCE = payload.substring(7).toFloat();
  Serial.println("Arduino - set config: " + String(FORWARD_STOP_DISTANCE));
  
}

void messageHandler(String &topic, String &payload) {
  if (payload.length >= 6 && payload.substring(0, 6) == "config"){
    setConfig(payload);
  }

  else if (payload == "forward"){
    moveForward();
  }

  else if (payload == "backward"){
    moveBackward();
  }
}

void moveForward(){
    sendToRB("ok forward");  // why just don't use json?

    digitalWrite(LEFT_WHEEL, HIGH);
    digitalWrite(RIGHT_WHEEL, HIGH);
    digitalWrite(LEFT_WHEEL_DIRECTION, HIGH);
    digitalWrite(RIGHT_WHEEL_DIRECTION, LOW);

    while (!enoughDistance(FORWARD_STOP_DISTANCE)){
      delay(100);
    }

    digitalWrite(LEFT_WHEEL, LOW);
    digitalWrite(RIGHT_WHEEL, LOW);
    digitalWrite(LEFT_WHEEL_DIRECTION, LOW);
    digitalWrite(RIGHT_WHEEL_DIRECTION, LOW);

    sendToRB("done forward");  // why just don't use json?
}

bool enoughDistance(int &dist){
  return getDistance() <= dist;
}

float getDistance(){
  digitalWrite(trigPin, LOW);
  delayMicroseconds(2);

  digitalWrite(trigPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(trigPin, LOW);
  
  duration = pulseIn(echoPin, HIGH);
  distanceCm = duration * SOUND_SPEED / 2;

  Serial.print("Distance (cm): ");
  Serial.println(distanceCm);
  return distance;
}

void moveBackward(){
  sendToRB("ok backward");  // why just don't use json?

  digitalWrite(LEFT_WHEEL, HIGH);
  digitalWrite(RIGHT_WHEEL, HIGH);
  digitalWrite(LEFT_WHEEL_DIRECTION, LOW);
  digitalWrite(RIGHT_WHEEL_DIRECTION, HIGH);

  while (!enoughDistance(BACKWARD_STOP_DISTANCE)){
    delay(100);
  }

  digitalWrite(LEFT_WHEEL, LOW);
  digitalWrite(RIGHT_WHEEL, LOW);
  digitalWrite(LEFT_WHEEL_DIRECTION, LOW);
  digitalWrite(RIGHT_WHEEL_DIRECTION, LOW);

  sendToRB("done backward");  // why just don't use json?
}