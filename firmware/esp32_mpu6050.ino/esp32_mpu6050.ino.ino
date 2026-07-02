#include <WiFi.h>
#include <PubSubClient.h>
#include <Wire.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>

const char* ssid = "Hoang Hai";
const char* password = "25102005";
const char* mqtt_server = "192.168.0.104";

WiFiClient espClient;
PubSubClient client(espClient);
Adafruit_MPU6050 mpu;

uint32_t seq = 0;

float complementaryFilter(float accAngle, float gyroRate, float prevAngle, float dt) {
  return 0.98 * (prevAngle + gyroRate * dt) + 0.02 * accAngle;
}

void connectWifi() {
  WiFi.begin(ssid, password);
  Serial.print("Connecting WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println();
  Serial.println("WiFi Connected");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.println("Connecting MQTT...");
    if (client.connect("ESP32_FALL")) {
      Serial.println("MQTT Connected");
    } else {
      Serial.println("MQTT Failed");
      delay(2000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  Wire.begin(21, 22);

  if (!mpu.begin()) {
    Serial.println("MPU6050 not found!");
    while (true) delay(100);
  }

  mpu.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu.setFilterBandwidth(MPU6050_BAND_44_HZ);

  connectWifi();
  client.setServer(mqtt_server, 1883);

  Serial.println("ESP32 FALL DETECTOR READY");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }

  sensors_event_t a, g, temp;
  mpu.getEvent(&a, &g, &temp);

  float ax = a.acceleration.x;
  float ay = a.acceleration.y;
  float az = a.acceleration.z;

  float gx = g.gyro.x;
  float gy = g.gyro.y;
  float gz = g.gyro.z;

  float acc_mag = sqrt(ax * ax + ay * ay + az * az);
  float gyro_mag = sqrt(gx * gx + gy * gy + gz * gz);

  // Orientation tu accelerometer (pitch, roll)
  float pitch = atan2(-ax, sqrt(ay * ay + az * az)) * 180.0 / PI;
  float roll = atan2(ay, az) * 180.0 / PI;

  uint32_t ts = millis();

  // JSON nang cao
  String json = "{";
  json += "\"ax\":" + String(ax, 2) + ",";
  json += "\"ay\":" + String(ay, 2) + ",";
  json += "\"az\":" + String(az, 2) + ",";
  json += "\"gx\":" + String(gx, 2) + ",";
  json += "\"gy\":" + String(gy, 2) + ",";
  json += "\"gz\":" + String(gz, 2) + ",";
  json += "\"mag\":" + String(acc_mag, 2) + ",";
  json += "\"gyro\":" + String(gyro_mag, 2) + ",";
  json += "\"temp\":" + String(temp.temperature, 1) + ",";
  json += "\"pitch\":" + String(pitch, 1) + ",";
  json += "\"roll\":" + String(roll, 1) + ",";
  json += "\"seq\":" + String(seq) + ",";
  json += "\"ts\":" + String(ts);
  json += "}";

  client.publish("fall/sensor", json.c_str());
  seq++;

  delay(20);  // 50Hz
}
