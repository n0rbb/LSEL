import paho.mqtt.client as mqtt # Import the MQTT library
import time # The time library is useful for delays
from datetime import datetime
import sys

#Functions
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
    return f"It’s {now.strftime('%A')}, the {now.day}{suffix} of {now.strftime('%B')} of {now.year}"

# Our "on message" event
def messageFunction (client, userdata, message):
	topic = str(message.topic)
	message = str(message.payload.decode("utf-8"))
	print(message)
 


def publish_msg(ourClient, mode):
	topics = ['MQTT_NETWORK/DMZ/TIME', 'MQTT_NETWORK/DMZ/DATE']
	tim = f"It’s {datetime.now().strftime('%H:%M:%S %p')}"
	day = get_date()
	if mode == "t" or mode == "h":
		ourClient.publish(topics[0], tim)
		
	elif mode == "d":
		ourClient.publish(topics[1], day)
	
	elif mode == "b": #Case to publish both	
		ourClient.publish(topics[0], tim)
		ourClient.publish(topics[1], day)

##Main program setup
#Compruebo los argumentos pasados
if len(sys.argv) < 3:
	client_id = "DEFAULT" #No mode entered by user
else:
	client_id = str(sys.argv[2])
	
if len(sys.argv) < 2:
	mode = "b" #no client id entered by user
else:
	mode = str(sys.argv[1])

#Append mode to ID name to avoid a conflict where the broker would skip messages
#if two versions of this script were running at the same time with the same ID
client_id = f"{client_id} > {mode}"

ourClient = mqtt.Client(client_id) # Create a MQTT client object
ourClient.connect("10.8.42.19", 1885) # Connect to the test MQTT broker
ourClient.loop_start() # Start the MQTT client

#initialize stored_seconds with an unattainable value
stored_seconds = 80
# Main program loop
while(1):
    now = datetime.now()
    #Showing time or date each 10 second multiplicand
    if now.second % 10 == 0 and now.second != stored_seconds:
        publish_msg(ourClient, mode) # Publish message to MQTT broker
        #Storing seconds to avoid a problem where 10 multiplicands would be skipped with a sleep of 1 second or more
        #This couldn't be resolved even using techniques like taking time before and after the execution to
        #compensate for execution time drifts, the only solution was to use a sleep time of less than 1 second
        stored_seconds = now.second
    time.sleep(0.5) # Sleep for 0.2 seconds (to guarantee that there is no skip in a 10 multiplicand)
