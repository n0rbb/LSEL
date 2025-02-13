import sys
import paho.mqtt.client as mqtt # Import the MQTT library
import time # The time library is useful for delays
from datetime import datetime, date
from itertools import cycle
#myIterator = cycle(['LEJANIAS','SHORTCUT'])

if len(sys.argv) >= 1:
	mode = str(sys.argv[1])
else:
	mode = "l" #Default to listen

if len(sys.argv) > 1:
	topic  = str(sys.argv[2])
else: #Case no topic argument was introduced 
	topic = 'DEMO'
client_topic = 'MQTT_NETWORK/' + topic 

# Our "on message" event
def messageFunction (client, userdata, message):
	topic = str(message.topic)
	message = str(message.payload.decode("utf-8"))
	print(message)
 
 
ourClient = mqtt.Client("CERCANIAS") # Create a MQTT client object
ourClient.connect("10.8.42.100", 1885) # Connect to the test MQTT broker
ourClient.subscribe("MQTT_NETWORK/#") # Subscribe to the topic AC_unit
ourClient.on_message = messageFunction # Attach the messageFunction to subscription
ourClient.loop_start() # Start the MQTT client
 
 
# Main program loop
while(1):
	if mode == "t" or mode == "h":
		now = datetime.now()
		current_time = now.strftime("%H:%M:%S")
		ourClient.publish(client_topic, "Son las: " +  current_time + ". Es hora de comprar billetes de RENFE SHORTCUT.")
	elif mode  == "d":
		current_date = date.today()
		ourClient.publish(client_topic, "Hoy es " +  str(current_date) + ". Es un día espectacular para comprar billetes de RENFE SHORTCUT.")
	else:	
		ourClient.publish(client_topic, "Escuchando")
	time.sleep(5) # Sleep for a second

