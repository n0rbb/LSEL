---MQTT PUBLISHER AND SUBSCRIBER

1) MQTT-datetimesub.py: MQTT Client that subscribes to both date and time channel
Run as > python3 MQTT-datetimesub.py clientname

**PARAMETERS
-clientname: specifies client id. Default value: DEFAULT.

2) MQTT-datetimepub.py: MQTT Client that publishes date, time or both to date / time topics
Run as > python3 MQTT-datetimepub.py mode clientname

**PARAMETERS
-mode: specifies publisher operation mode. Default value: b.
	[t : Publishes current time to TIME topic] (also works with h)
	[d : Publishes current date to DATE topic]
	[b : Performs both t & d tasks]

-clientname: specifies client id. Default value: DEFAULT*,* being the operation mode.

3) Mosquitto config file to run on port 1885. May be placed under /etc/mosquitto folder. allow_anonymous line may be removed