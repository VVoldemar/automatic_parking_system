#include <ESP8266WiFi.h>
// #include <MQTTClient.h>
#include <MQTT.h>

#define LEFT_WHEEL D5
#define RIGHT_WHEEL D6
#define LEFT_WHEEL_DIRECTION D4 
#define RIGHT_WHEEL_DIRECTION D7

#define TRIG_PIN D2
#define ECHO_PIN D3

#define SOUND_SPEED 0.034

// #define NO_DISTANCE_MODULE

const char WIFI_SSID[] = "MQTTT-1";
const char WIFI_PASSWORD[] = "11223344";

const char MQTT_BROKER_ADRRESS[] = "10.42.0.1";
const int MQTT_PORT = 1883;
const char MQTT_CLIENT_ID[] = "esp";
const char MQTT_USERNAME[] = "";
const char MQTT_PASSWORD[] = "";

const char PUBLISH_TOPIC[] = "esp";
const char SUBSCRIBE_TOPIC[] = "rasp";

const int PUBLISH_INTERVAL = 10000;

WiFiClient network;
MQTTClient mqtt = MQTTClient(256);

unsigned long lastPublishTime = 0;

int forward_stop_distance = 5;
int backward_stop_distance = 5;
int left_motor_speed = 255;
int right_motor_speed = 255;

void setup() {
  Serial.begin(9600);

  pinMode(D4, OUTPUT);
  pinMode(D5, OUTPUT);
  pinMode(D6, OUTPUT);
  pinMode(D7, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);

  int status = WL_IDLE_STATUS;
  while (status != WL_CONNECTED) {
    Serial.print("Arduino - Attempting to connect to SSID: ");
    Serial.println(WIFI_SSID);
    status = WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    Serial.println(status);
    delay(5000);
  }

  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  connectToRB();

  sendToRB("hello");
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
  switch (payload[6])
  { 
  case 'F':
    forward_stop_distance = payload.substring(8).toFloat();
    break;
  case 'B':
    backward_stop_distance = payload.substring(8).toFloat();
    break;
  case 'L':
    left_motor_speed = payload.substring(8).toFloat();
    break;
  case 'R':
    right_motor_speed = payload.substring(8).toFloat();
    break;
  }
  Serial.println("Arduino - set config: " + 
    String(forward_stop_distance) + " " + 
    String(backward_stop_distance) + " " +
    String(left_motor_speed) + " " +
    String(right_motor_speed) + " ");
  sendToRB("ok config");
}

void messageHandler(String &topic, String &payload) {
  if (payload.length() >= 6 && payload.substring(0, 6) == "config"){
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

  analogWrite(LEFT_WHEEL, left_motor_speed);
  analogWrite(RIGHT_WHEEL, right_motor_speed);
  digitalWrite(LEFT_WHEEL_DIRECTION, LOW);
  digitalWrite(RIGHT_WHEEL_DIRECTION, HIGH);

  while (!enoughDistance(forward_stop_distance)){
    delay(100);
  }

  digitalWrite(LEFT_WHEEL, LOW);
  digitalWrite(RIGHT_WHEEL, LOW);
  digitalWrite(LEFT_WHEEL_DIRECTION, LOW);
  digitalWrite(RIGHT_WHEEL_DIRECTION, LOW);

  sendToRB("done forward");  // why just don't use json?
}

bool enoughDistance(int &dist){
#ifdef NO_DISTANCE_MODULE
  delay(2000);
  return true;
#else
  return getDistance() <= dist;
#endif
}

float getDistance(){
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);

  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH);
  float distanceCm = duration * SOUND_SPEED / 2.0;

  Serial.print("Distance (cm): ");
  Serial.println(distanceCm);
  return distanceCm;
}

void moveBackward(){
  sendToRB("ok backward");  // why just don't use json?

  analogWrite(LEFT_WHEEL, left_motor_speed);
  analogWrite(RIGHT_WHEEL, right_motor_speed);
  digitalWrite(LEFT_WHEEL_DIRECTION, HIGH);
  digitalWrite(RIGHT_WHEEL_DIRECTION, LOW);

  while (enoughDistance(backward_stop_distance)){
    delay(100);
  }

  digitalWrite(LEFT_WHEEL, LOW);
  digitalWrite(RIGHT_WHEEL, LOW);
  digitalWrite(LEFT_WHEEL_DIRECTION, LOW);
  digitalWrite(RIGHT_WHEEL_DIRECTION, LOW);

  sendToRB("done backward");  // why just don't use json?
}