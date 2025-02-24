import paho.mqtt.client as mqtt # Import the MQTT library
import time # The time library is useful for delays
from itertools import cycle
from datetime import datetime
import sys

# Our "on message" event
def messageFunction (client, userdata, message):
	topic = str(message.topic)
	message = str(message.payload.decode("utf-8"))
	print(message)
 
if len(sys.argv) < 3:
        topic_sub = "MQTT_NETWORK/#"
else:
        topic_sub = str(sys.argv[2])

if len(sys.argv) < 2:
	clientid = "DEFAULT"
else:
	clientid = str(sys.argv[1])


ourClient = mqtt.Client(clientid) # Create a MQTT client object
ourClient.connect("10.8.42.19", 1885) # Connect to the test MQTT broker -- Test with 192.168.1.42
ourClient.subscribe(topic_sub) # Subscribe to both topics (time/date)
ourClient.on_message = messageFunction # Attach the messageFunction to subscription
ourClient.loop_start() # Start the MQTT client

# Main program loop
while(1):
	time.sleep(0.1) # Sleep for 0.1 seconds
