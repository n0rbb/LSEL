import paho.mqtt.client as mqtt # Import the MQTT library
import time # The time library is useful for delays
from itertools import cycle
from datetime import datetime

# Our "on message" event
def messageFunction (client, userdata, message):
	topic = str(message.topic)
	message = str(message.payload.decode("utf-8"))
	print(message)
 
ourClient = mqtt.Client("DMZ") # Create a MQTT client object
ourClient.connect("10.8.42.100", 1885) # Connect to the test MQTT broker
ourClient.subscribe("MQTT_NETWORK/DMZ/#") # Subscribe to the topic AC_unit
ourClient.on_message = messageFunction # Attach the messageFunction to subscription
ourClient.loop_start() # Start the MQTT client

# Main program loop
while(1):
	time.sleep(0.1) # Sleep for 0.1 seconds