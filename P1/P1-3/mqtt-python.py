import paho.mqtt.client as mqtt
import time
import sys


global topic, msg, despacho, found_office, aire, humedad, luz, temperatura

found_office = False
rcvd_samples = [0, 0, 0, 0]

aire = [0, 0, 0, 0, 0]
humedad = [0, 0, 0, 0, 0]
luz = [0, 0, 0, 0, 0]
temperatura = [0, 0, 0, 0, 0]

period = 5 #s

def messageEvent (client, userdata, message):
    global topic, msg
    topic = str(message.topic)
    msg = str(message.payload.decode("utf-8"))
    print(msg)
    #return [topic, msg]

if len(sys.argv) < 2:
	correo = "mario.demiguel@alumnos.upm.es" #No email entered by user
else:
	correo = str(sys.argv[1])
	
if len(sys.argv) < 3:
	clientid = "DEFAULT_CLIENT" #No client id entered by user
else:
	clientid = str(sys.argv[2])
	
topic_all = "LSE/instalaciones/despachos/+/email_ocupante"
topic = topic_all
msg = ""
ourClient = mqtt.Client(clientid)
ourClient.connect("192.168.1.42", 1885)
ourClient.on_message = messageEvent
ourClient.subscribe(topic_all)
ourClient.loop_start()

def messageFunction():
    global topic, msg, despacho, found_office, aire, temperatura, humedad, luz
    t_split = topic.split("/")
    print("token" + t_split[4])
    if (t_split[4] == "email_ocupante") and (found_office == False):
        #print(msg)
        #print(correo)
        if (msg == correo):
            despacho = t_split[3]
            print(f"Despacho encontrado: {despacho}")
            found_office = True
            ourClient.unsubscribe(topic_all)
            ourClient.subscribe(f"LSE/instalaciones/despachos/{despacho}/aire")
            ourClient.subscribe(f"LSE/instalaciones/despachos/{despacho}/humedad")
            ourClient.subscribe(f"LSE/instalaciones/despachos/{despacho}/luz")
            ourClient.subscribe(f"LSE/instalaciones/despachos/{despacho}/temperatura")
    elif (t_split[4] == "aire"):
        for i in range(len(aire) - 1):
            aire[i] = aire[i + 1]
        aire[4] = float(msg)
        if rcvd_samples[0] < 5: rcvd_samples[0] += 1

    elif (t_split[4] == "humedad"):
        for i in range(len(humedad) - 1):
            humedad[i] = humedad[i + 1]
        humedad[4] = float(msg)
        if rcvd_samples[1] < 5: rcvd_samples[1] += 1

    elif (t_split[4] == "luz"):
        for i in range(len(luz) - 1):
            luz[i] = luz[i + 1]
        luz[4] = float(msg)
        if rcvd_samples[2] < 5: rcvd_samples[2] += 1

    elif (t_split[4] == "temperatura"):
        for i in range(len(temperatura) - 1):
            temperatura[i] = temperatura[i + 1]
        temperatura[4] = float(msg)
        if rcvd_samples[3] < 5: rcvd_samples[3] += 1

def fmean(array, size):
    if (size != 0):
        s = 0
        array = array[::-1]
        for i in range(size):
            s += array[i]
        return s/size
    else:
        return 0
    
          

def publisherFunction(period):
    global despacho, aire, temperatura, humedad, luz
    
    print(aire)
    print(humedad)
    print(luz)
    print(temperatura)

    a_mean = fmean(aire, rcvd_samples[0])
    h_mean = fmean(humedad, rcvd_samples[1])
    l_mean = fmean(luz, rcvd_samples[2])
    t_mean = fmean(temperatura, rcvd_samples[3])

    ourClient.publish(f"LSE/trabajadores/{correo}/promedios/aire", f"Aire: {str(a_mean)}")
    ourClient.publish(f"LSE/trabajadores/{correo}/promedios/humedad", f"Humedad: {str(h_mean)}")
    ourClient.publish(f"LSE/trabajadores/{correo}/promedios/luz", f"Luz: {str(l_mean)}")
    ourClient.publish(f"LSE/trabajadores/{correo}/promedios/temperatura", f"Temperatura: {str(t_mean)}")
    time.sleep(period)

while True:
	messageFunction()
	if (found_office): publisherFunction(period) 
	time.sleep(0.01)
	