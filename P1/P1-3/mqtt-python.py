import paho.mqtt.client as mqtt
import time
import sys
import asyncio

global topic, msg, despacho, found_office, aire, humedad, luz, temperatura, update_flags

found_office = False
rcvd_samples = [0, 0, 0, 0]
update_flags = [1, 1, 1, 1]
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


async def officeHandler():
    global topic, msg, despacho, found_office
    while True:
        await asyncio.sleep(0.01)

        t_split = topic.split("/")
        #print("token" + t_split[4])
        
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

#Creo un diccionario que mapee los tokens del topic a las listas de valores recibidos, me servirá para actualizar la lista de received_samples.
sensores = {
    "aire" : aire,
    "humedad" : humedad,
    "luz" : luz,
    "temperatura" : temperatura
}
#Por problemas de temporización, voy a crear 4 tareas concurrentes idénticas que se preocupen de hacer las gestiones de cada parámetro por separado.
async def paramHandler(param):
        global topic, msg, aire, temperatura, humedad, luz, update_flags
        
        while True:
            print(update_flags)
            await asyncio.sleep(0.003)
            t_split = topic.split("/") #Pillo el índice de la posición de t_split[4] dentro de la lista de claves del diccionario de sensores. asumo que el orden de todo es igual
            if t_split[4] in sensores and t_split[4] == param:
                i = list(sensores.keys()).index(t_split[4])
                if update_flags[i]:
                    update_flags[i] = 0
                    muestra = sensores[t_split[4]] # Meto en muestra (lista) la clave de sensores correspondiente al valor t_split[4] (string)
                    for i in range(len(muestra) - 1):
                        muestra[i] = muestra[i + 1] #Desplazo una posición a la izquierda todas las muestras, liberando la posición 4 o -1 de la lista
                    muestra[-1] = float(msg) #Actualizo la última posición de la lista con el payload del mensaje
                    if rcvd_samples[i] < 5: rcvd_samples[i] += 1 #Actualizo el valor correspondiente de muestras recibidas


def fmean(array, size):
    if (size != 0):
        s = 0
        array = array[::-1]
        for i in range(size):
            s += array[i]
        return s/size
    else:
        return 0
    

async def publisherFunction(period):
    global despacho, aire, temperatura, humedad, luz, update_flags
    while True:
        await asyncio.sleep(period) #secs
        if all(elem == 0 for elem in update_flags):
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
            update_flags = [1, 1, 1, 1]


async def mqtt_multitask():
    task1 = asyncio.create_task(officeHandler())
    task2 = asyncio.create_task(publisherFunction(period))

    task3 = asyncio.create_task(paramHandler("aire"))
    task4 = asyncio.create_task(paramHandler("humedad"))
    task5 = asyncio.create_task(paramHandler("luz"))
    task6 = asyncio.create_task(paramHandler("temperatura"))

    if not found_office:
        await asyncio.gather(task1) #Corro solo el officehandler
    else: 
        await asyncio.gather(task2, task3, task4, task5, task6) #corro los paramhandlers y publisherfunction
        #5 funciones de repente corriendo concurrentemente. Puro rock n roll.


asyncio.run(mqtt_multitask())