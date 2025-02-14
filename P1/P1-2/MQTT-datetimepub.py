import paho.mqtt.client as mqtt # Import the MQTT library
import time # The time library is useful for delays
from itertools import cycle
from datetime import datetime
import sys

mode=sys.argv[2]

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
 
ourClient = mqtt.Client(str(sys.argv[1])) # Create a MQTT client object
ourClient.connect("10.8.42.100", 1885) # Connect to the test MQTT broker
ourClient.loop_start() # Start the MQTT client

def publish_msg(ourClient, mode):
	topics = ['MQTT_NETWORK/DMZ/TIME', 'MQTT_NETWORK/DMZ/DATE']
	tim = f"It’s {datetime.now().strftime('%H:%M:%S %p')}"
	day = get_date()
	if mode == "t" or mode == "h":
		
		ourClient.publish(time_topic, tim)
		
	elif mode == "d":
		ourClient.publish(day_topic, day)
	
	elif mode == "b": #Case to publish both	
		ourClient.publish(topics[0], tim)
		ourClient.publish(topics[1], day)
	
		
# Main program loop
while(1):
	if now.second % 10 == 0:
		publish_msg(ourClient, mode) # Publish message to MQTT broker
	time.sleep(1) # Sleep for 10 seconds
