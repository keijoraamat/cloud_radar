import re
import serial
import ssl
import json  # For converting radar data to JSON format
import paho.mqtt.client as mqtt

def extract_radar_data(serial_port, baudrate=256000, client=None, topic=None):
    print("starting radar data extraction")
    # Regular expressions to capture relevant information
    timestamp_pattern = r"^(\d{2}:\d{2}:\d{2}\.\d{3})"
    out_status_pattern = r"OUT pin status: (\w+)"
    moving_obj_pattern = r"Moving object at distance: (\d+) cm"
    stationary_obj_pattern = r"Stationary object at distance: (\d+) cm"

    # Open the serial port
    with serial.Serial(serial_port, baudrate=baudrate, timeout=1) as ser:
        print("serial port opened")
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()
                timestamp_match = re.search(timestamp_pattern, line)
                out_status_match = re.search(out_status_pattern, line)
                moving_obj_match = re.search(moving_obj_pattern, line)
                stationary_obj_match = re.search(stationary_obj_pattern, line)

                # Extract and send values if all matches are found
                if timestamp_match and out_status_match and moving_obj_match and stationary_obj_match:
                    data = {
                        "timestamp": timestamp_match.group(1),
                        "out_status": out_status_match.group(1),
                        "moving_obj_distance": int(moving_obj_match.group(1)),
                        "stationary_obj_distance": int(stationary_obj_match.group(1)),
                    }

                    # Print the extracted data in real-time
                    print(data)

                    # Publish to AWS IoT Core
                    if client and topic:
                        payload = json.dumps(data)
                        result = client.publish(topic, payload)
                        result.wait_for_publish()  # Ensure the message is sent
                else:
                    print("Error in parsing the line")
                    print(f"TS: {timestamp_match}, out_stat: {out_status_match}, moving_o: {moving_obj_match}, stationary: {stationary_obj_match}")

            except KeyboardInterrupt:
                print("Stopping data extraction.")
                break

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to AWS IoT Core!")
    else:
        print(f"Failed to connect, return code {rc}")

def on_publish(client, userdata, mid):
    print(f"Message {mid} published!")

# Configuration
broker = "angi07afcqoi3-ats.iot.eu-north-1.amazonaws.com"
port = 8883
topic = "your/topic/here"
serial_port = "/dev/ttyACM0"
baud_rate = 256000

# Paths to certificates
ca_cert = "root-CA.pem"
client_cert = "certificate.pem"
private_key = "private.key"

# Initialize MQTT client
client = mqtt.Client()
client.on_connect = on_connect
client.on_publish = on_publish

# Configure TLS/SSL
client.tls_set(ca_certs=ca_cert,
               certfile=client_cert,
               keyfile=private_key,
               cert_reqs=ssl.CERT_REQUIRED,
               tls_version=ssl.PROTOCOL_TLSv1_2,
               ciphers=None)

# Connect to AWS IoT Core
try:
    client.connect(broker, port, keepalive=60)
    client.loop_start()  # Start the network loop

    # Start data extraction and transmission
    extract_radar_data(serial_port, baud_rate, client, topic)

except Exception as e:
    print(f"Failed to connect or publish: {e}")
finally:
    client.loop_stop()
    client.disconnect()