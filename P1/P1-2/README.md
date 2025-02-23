# MQTT publisher and subscriber
Brief description of the included files for the LSEL assignment 1.2 and instructions on proper usage.
## 1) MQTT-datetimesub.py
An MQTT Client that subscribes to both date and time topics. \
**Run it as:** \
 ``> python3 MQTT-datetimesub.py clientname``
 ### Parameters
* ``clientname``: specifies client id. Default value: DEFAULT.
 ## 2) MQTT-datetimepub.py
 An MQTT Client that publishes date, time or both to the date / time topics. \
 **Run it as:** \
 ``> python3 MQTT-datetimepub.py mode clientname``
 ### Parameters
 * ``mode``: specifies publisher operation mode. Default value: b.
	* t : Publishes current time to TIME topic (also works with h)
	* d : Publishes current date to DATE topic
	* b : Performs both t & d tasks
* ``clientname``: specifies client id. Default value: DEFAULT.

## 3) mosquitto.conf
Mosquitto configuration file to run on port 1885. May be placed under /etc/mosquitto folder. ``allow_anonymous`` line may be removed. \ 
**Start the broker with** \
``> sudo mosquitto -c /etc/mosquitto/mosquitto.conf``
