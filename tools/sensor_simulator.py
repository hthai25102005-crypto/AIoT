import json
import time
import math
import random
import paho.mqtt.client as mqtt

client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
client.connect("localhost", 1883)
client.loop_start()

t = 0
while True:
    t += 0.05
    cycle = t % 15

    if 10 < cycle < 10.5:
        # free fall phase: all axes drop
        ax = random.gauss(0, 0.3)
        ay = random.gauss(0, 0.3)
        az = random.gauss(0.5, 0.3)
    elif 10.5 < cycle < 10.7:
        # impact spike
        ax = random.gauss(5, 2)
        ay = random.gauss(3, 2)
        az = random.gauss(15, 5)
    else:
        # normal standing
        ax = random.gauss(0, 0.3)
        ay = random.gauss(0, 0.3)
        az = 9.8 + random.gauss(0, 0.3)

    mag = math.sqrt(ax**2 + ay**2 + az**2)
    payload = json.dumps({"ax": round(ax, 2), "ay": round(ay, 2), "az": round(az, 2), "mag": round(mag, 2)})
    client.publish("fall/sensor", payload)
    print(f"[SIM] mag={mag:6.2f}  ax={ax:5.1f} ay={ay:5.1f} az={az:5.1f}  {'FALL' if 10 < cycle < 11 else ''}", end="\r")
    time.sleep(0.05)
