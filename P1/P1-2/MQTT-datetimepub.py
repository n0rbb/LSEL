import paho.mqtt.client as mqtt # Import the MQTT library
import time # The time library is useful for delays
from itertools import cycle
from datetime import datetime
import sys

client_topic_hora = 'MQTT_NETWORK/DMZ/TIME'
client_topic_fecha = 'MQTT_NETWORK/DMZ/TIME'

mode=sys.argv[1]
def get_date():
    now = datetime.now()
    if now.day == 1:
        suffix = "st"
    elif now.day == 2:
        suffix = "nd"
    elif now.day == 3:
        suffix = "rd"
    else:
        suffix = "th"
    return f"It’s {now.strftime('%A')}, the {now.day}{suffix} of {now.strftime('%B')} of {now.year}\n"

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
	if mode == "t" or mode == "h":
		current_datetime = f"It’s {now.strftime('%H:%M:%S %p')}"
		ourClient.publish(client_topic_hora, current_datetime) # Publish message to MQTT broker
		time.sleep(2) # Sleep for 2 seconds
	if mode == "d":
		if now.day == 1:
			suffix = "st"
		elif now.day == 2:
			suffix = "nd"
		elif now.day == 3:
			suffix = "rd"
		else:
			suffix = "th"
		current_datetime = f"It’s {now.strftime('%A')}, the {now.day}{suffix} of {now.strftime('%B')} of {now.year}"
		ourClient.publish(client_topic_fecha, current_datetime) # Publish message to MQTT broker
		time.sleep(2) # Sleep for 2 seconds