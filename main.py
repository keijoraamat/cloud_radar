import re
import serial
import ssl
import json  # For converting radar data to JSON format
import paho.mqtt.client as mqtt
import os
import datetime

def extract_radar_data(serial_port, baudrate=256000, client=None, topic=None):
    print("starting radar data extraction")
    # Regular expressions to capture relevant information
    out_status_pattern = r"OUT pin status: (\w+)"
    moving_obj_pattern = r"Moving object at distance: (\d+) cm"
    stationary_obj_pattern = r"Stationary object at distance: (\d+) cm"
    separator_obj = "--------------------"

    # Open the serial port
    with serial.Serial(serial_port, baudrate=baudrate, timeout=1) as ser:
        print("serial port opened")
        while True:
            try:
                line = ser.readline().decode('utf-8').strip()

                if not line:  # Skip empty lines
                    continue

                # Add the line to the current data chunk
                data_chunk.append(line)

                # Check for the separator indicating the end of a chunk
                if separator_obj in line:
                    # Join the accumulated lines for parsing
                    full_data = "\n".join(data_chunk)
                    data_chunk = []  # Reset for the next chunk

                    # Extract relevant fields
                    out_status_match = re.search(out_status_pattern, full_data)
                    moving_obj_match = re.search(moving_obj_pattern, full_data)
                    stationary_obj_match = re.search(stationary_obj_pattern, full_data)

                    # Process the data if all patterns match
                    if out_status_match and moving_obj_match and stationary_obj_match:
                        data = {
                            "timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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
                    print(full_data)

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
broker = "angi07afcqoi3-ats.iot.eu-central-1.amazonaws.com"
port = 8883
topic = "your/topic/here"
serial_port = "/dev/ttyACM0"
baud_rate = 256000

# Paths to certificates
current_dir = os.path.dirname(os.path.abspath(__file__))
ca_cert = os.path.join(current_dir, "root-CA.pem")
client_cert = os.path.join(current_dir, "certificate.pem")
private_key = os.path.join(current_dir, "private.key")

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
