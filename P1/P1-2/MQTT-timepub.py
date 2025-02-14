import paho.mqtt.client as mqtt # Import the MQTT library
import time # The time library is useful for delays
from itertools import cycle
from datetime import datetime
import sys

client_topic = 'MQTT_NETWORK/DMZ/TIME'

# Our "on message" event
def messageFunction (client, userdata, message):
	topic = str(message.topic)
	message = str(message.payload.decode("utf-8"))
	print(message)
 
ourClient = mqtt.Client("ZMD") # Create a MQTT client object
ourClient.connect("10.8.42.19", 1885) # Connect to the test MQTT broker
ourClient.loop_start() # Start the MQTT client

# Main program loop
while(1):
	now = datetime.now()
	#if now.second % 10 == 0:
	current_datetime = f"It’s {now.strftime('%H:%M:%S %p')}"
	ourClient.publish(client_topic, current_datetime) # Publish message to MQTT broker
	time.sleep(1) # Sleep for 2 seconds