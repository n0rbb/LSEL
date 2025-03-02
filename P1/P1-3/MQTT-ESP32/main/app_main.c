#include <stdio.h>
#include <stdint.h>
#include <stddef.h>
#include <string.h>
#include "esp_wifi.h"
#include "esp_system.h"
#include "nvs_flash.h"
#include "esp_event.h"
#include "esp_netif.h"
#include "protocol_examples_common.h"

#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "freertos/semphr.h"
#include "freertos/queue.h"

#include "lwip/sockets.h"
#include "lwip/dns.h"
#include "lwip/netdb.h"

#include "esp_log.h"
#include "mqtt_client.h"

#define PUBLISH_PERIOD 5000 //Publish period, in ms 
#define MAX_N_CHARS 300 //A macro to set a maximum size of strings to be used (we use an overly big value to avoid size issues)
#define MAX_FIELD_CHARS 15 //Maximum size of strings contained event fields
#define MAX_DESP_CHARS 3 //Maximum size of string containing the offie value
#define NSAMPLES 5 //Number of each-sensor samples to keep stored at a time
#define DESP_CYCLES 3 // Number of cycles for despacho: Despacho is the 3rd parameter: LSE/Instalaciones/Despachos/HERE
#define MAG_CYCLES 4  // Number of cycles for our new topic: "Email_ocupante" is the 4th parameter: LSE/Instalaciones/Despachos/00/HERE 
//Temperature threshold values
#define MIN_TEMP 20
#define MAX_TEMP 25
//Humidity threshold values
#define MIN_HUM 30
#define MAX_HUM 60
//Light threshold values
#define MIN_LUZ 300
#define MAX_LUZ 500
//Air concentration threshold values
#define MAX_AIRE 1000

//Email of the student whose office is to be analysed
#define CORREO "d.muniz@alumnos.upm.es"
//#define CORREO "mario.demiguel@alumnos.upm.es"

static const char *TAG = "mqtt_LSEL11";
uint32_t MQTT_CONNECTED = 0;
esp_mqtt_client_handle_t mqtt_client = NULL;
char despacho[MAX_DESP_CHARS];
float aire[NSAMPLES] = {0, 0, 0, 0, 0};
float humedad[NSAMPLES] = {0, 0, 0, 0, 0};
float luz[NSAMPLES] = {0, 0, 0, 0, 0};
float temperatura[NSAMPLES] = {0, 0, 0, 0, 0};
float mean_aire = 0, mean_humedad = 0, mean_luz = 0, mean_temperatura = 0;
uint8_t rcvd_samples[4] = {0, 0, 0, 0};

/*
/// @brief Function to compute the average of size-first values of an array
/// @param array An array of raw values (float) used to compute the average
/// @param size Generally the size of the array, but may indicate the number of samples to be considered for the average (size-first) 
/// @return Float of single precision with the computed average
*/
float fmean(float *array, uint8_t size)
{
    float sum = 0;
    for (uint8_t i = 0; i < size; i++)
    {
        sum += array[i];
    }
    return sum / size;
}
/*
/// @brief Parsing function of MQTT topic: Will get the "cycle" token of a MQTT topic with "/" dividers
/// @param msg_topic String with the full topic of the received message
/// @param target_str String to which the parsed token is to be written
/// @param cycle Max number of iterations within the function (position of the parameter we want)
*/
void get_parameter(char *msg_topic, char *target_str, int cycle)
{
    char temp_msg_topic[MAX_N_CHARS];
    strcpy(temp_msg_topic, msg_topic); //Since strtok overwrites the strings, we first copy the it to a new one and work with that
    char *temp_str = strtok(temp_msg_topic, "/");
    for (int i = 0; i < cycle; i++)
    {
        temp_str = strtok(NULL, "/");
    }
    strcpy(target_str, temp_str); 
}
/*
/// @brief Void function to publish the necessary alarms
/// @param mag String with the alarm message payload: For instance, "Humedad alta"
*/
void publish_alarma(char *mag)
{
    char topic[MAX_N_CHARS] = "";
    char payload[MAX_N_CHARS] = "";
    int msg_id = 0;
    sprintf(topic, "LSE/trabajadores/%s/alerta", CORREO);
    sprintf(payload, "%s", mag);
    printf("\r\n[Publisher_Task]\r\n[TOPIC][%s]\r\n[PAYLOAD][%s]\r\n", topic, payload);
    msg_id = esp_mqtt_client_publish(mqtt_client, topic, payload, 0, 0, 0);
    ESP_LOGI(TAG, "sent publish successful, msg_id=%d", msg_id);
}
/*
/// @brief Void function that publishes the averages of the sensor measurements to their corresponding topics
/// @param mag Which average are we going to publish, i.e. Aire, Humedad, Luz... (Used to determine the correct topic)
/// @param mean Numeric value of the average, message payload
*/
void publish_promedios(char *mag, float mean)
{
    char topic[MAX_N_CHARS] = "";
    char payload[MAX_N_CHARS] = "";
    int msg_id = 0;
    sprintf(topic, "LSE/trabajadores/%s/promedios/%s", CORREO, mag);
    sprintf(payload, "%.2f", mean);
    printf("\r\n[Publisher_Task]\r\n[TOPIC][%s]\r\n[PAYLOAD][%s]\r\n", topic, payload);
    msg_id = esp_mqtt_client_publish(mqtt_client, topic, payload, 0, 0, 0);
    //ESP_LOGI(TAG, "[TOPIC][%s]\r\n[PAYLOAD][%s]", topic, payload);
    ESP_LOGI(TAG, "sent publish successful, msg_id=%d", msg_id);
}
/*
/// @brief FreeRTOS task that manages publishing of the sensor averages and the alarms 
/// @param params 
*/
void Publisher_Task(void *params) {
    ESP_LOGI(TAG,"Publisher_Task");

    while (true) {
        vTaskDelay(PUBLISH_PERIOD / portTICK_PERIOD_MS); //Free RTOS delay function that ensures the publication at the set PUBLISH_PERIOD rate
        if(MQTT_CONNECTED) {
            
            /*First we get the four means with the available samples. All positions in rcvd_samples will be 5, except in the case of the first iterations,
            when not enough samples will have been received and so the average will be computed with less than 5 values. 
            */
            mean_aire = fmean(aire, rcvd_samples[0]);
            mean_humedad = fmean(humedad, rcvd_samples[1]);
            mean_luz = fmean(luz, rcvd_samples[2]);
            mean_temperatura = fmean(temperatura, rcvd_samples[3]);

            //We now publish all the means
            publish_promedios("aire", mean_aire);
            publish_promedios("humedad", mean_humedad);
            publish_promedios("luz", mean_luz);
            publish_promedios("temperatura", mean_temperatura);

            //Finally we compare our averages with the threshold values and publish the corresponding alarms
            if(mean_aire > MAX_AIRE) {
                publish_alarma("Aire");
            }
            
            if(mean_humedad > MAX_HUM) {
                publish_alarma("Humedad Alta");
            }
            else if(mean_humedad < MIN_HUM) {
                publish_alarma("Humedad Baja");
            }

            
            if (mean_luz > MAX_LUZ) {
                publish_alarma("Luz Alta");
            }
            else if(mean_luz < MIN_LUZ) {
                publish_alarma("Luz Baja");
            }

            
            if(mean_temperatura > MAX_TEMP) {
                publish_alarma("Temperatura Alta");
            }
            else if(mean_temperatura < MIN_TEMP) {
                publish_alarma("Temperatura Baja");
            }
            
        }
        else{
            ESP_LOGI(TAG,"[Publisher_Task][MQTT NOT CONNECTED]");
        }
    }
}
/*
/// @brief MessageFunction: Function that handles the received MQTT messages. We may differentiate 2 tasks within the function. 
/// a) Find the correct office: Parses all the topics to which the client is subscribed on start and finds the office with a given email (CORREO macro).
/// b) Once subscribed to correct sensor data, handles the reception of raw values of each sensor (updates the data arrays and increments the rcvd_data values on the first iterations).
/// @param event_data Pointer to a reception event, with a topic and a payload, among others
*/
static void MessageFunction(void *event_data)
{
    esp_mqtt_event_handle_t event = event_data;
    char msg_data[MAX_N_CHARS];
    char msg_topic[MAX_N_CHARS];
    char rcvd_field[MAX_FIELD_CHARS];
    
    //We save the values we need to variables msg_topic and msg_data (payload)
    sprintf(msg_topic, "%.*s", event->topic_len, event->topic);
    sprintf(msg_data, "%.*s", event->data_len, event->data);

    //We parse the fourth token from the topic and save it to rcvd_field 
    get_parameter(msg_topic, rcvd_field, MAG_CYCLES);

    //If we are getting a fourth token "email_ocupante" we get the payload and compare it to our set CORREO.
    if (strcmp(rcvd_field, "email_ocupante") == 0) 
    {
        if (strcmp(msg_data, CORREO) == 0) //We have found our office
        {
            get_parameter(msg_topic, despacho, DESP_CYCLES); //We parse the token again to get the office number
            printf("--------------------------------------------\r\n");
            printf("TOPIC=%s\r\n", msg_topic);
            printf("DATA=%s\r\n", msg_data);
            printf("Despacho: %s\r\n", despacho);
            printf("--------------------------------------------\r\n");
            esp_mqtt_client_unsubscribe(mqtt_client, "LSE/instalaciones/despachos/+/email_ocupante"); //We can now unsubscribe to all-offices to resubscribe to our office data

            // We now subscribe to all topics but the email within our office and start our publishing task (That's why we don't use #)
            char subs_topic[MAX_N_CHARS];
            sprintf(subs_topic, "LSE/instalaciones/despachos/%s/aire", despacho);
            esp_mqtt_client_subscribe(mqtt_client, subs_topic, 1);
            sprintf(subs_topic, "LSE/instalaciones/despachos/%s/humedad", despacho);
            esp_mqtt_client_subscribe(mqtt_client, subs_topic, 1);
            sprintf(subs_topic, "LSE/instalaciones/despachos/%s/luz", despacho);
            esp_mqtt_client_subscribe(mqtt_client, subs_topic, 1);
            sprintf(subs_topic, "LSE/instalaciones/despachos/%s/temperatura", despacho);
            esp_mqtt_client_subscribe(mqtt_client, subs_topic, 1);
            xTaskCreate(Publisher_Task, "Publisher_Task", 1024 * 5, NULL, 5, NULL);
        }
    }

    //After we subscribed to our office topics, we can start getting our sensor samples and storing it to the arrays.
    if (strcmp(rcvd_field, "aire") == 0)
    {
        uint8_t i = 0;
        for (i = NSAMPLES - 1; i > 0; i--)
        {
            aire[i] = aire[i - 1];
        }
        aire[0] = atof(msg_data);
        if (rcvd_samples[0] < NSAMPLES) rcvd_samples[0]++;
       
    }
    if (strcmp(rcvd_field, "humedad") == 0)
    {
        uint8_t i = 0;
        for (i = NSAMPLES - 1; i > 0; i--)
        {
            humedad[i] = humedad[i - 1];
        }
        humedad[0] = atof(msg_data);
        if (rcvd_samples[1] < NSAMPLES) rcvd_samples[1]++;
    }
    if (strcmp(rcvd_field, "luz") == 0)
    {
        uint8_t i = 0;
        for (i = NSAMPLES - 1; i > 0; i--)
        {
            luz[i] = luz[i - 1];
        }
        luz[0] = atof(msg_data);
        if (rcvd_samples[2] < NSAMPLES) rcvd_samples[2]++;
    }
    if (strcmp(rcvd_field, "temperatura") == 0)
    {
        uint8_t i = 0;
        for (i = NSAMPLES - 1; i > 0; i--)
        {
            temperatura[i] = temperatura[i - 1];
        }
        temperatura[0] = atof(msg_data);
        if (rcvd_samples[3] < NSAMPLES) rcvd_samples[3]++;
    }
}

static void log_error_if_nonzero(const char *message, int error_code)
{
    if (error_code != 0)
    {
        ESP_LOGE(TAG, "Last error %s: 0x%x", message, error_code);
    }
}

/*
 * @brief Event handler registered to receive MQTT events
 *
 *  This function is called by the MQTT client event loop.
 *
 * @param handler_args user data registered to the event.
 * @param base Event base for the handler(always MQTT Base in this example).
 * @param event_id The id for the received event.
 * @param event_data The data for the event, esp_mqtt_event_handle_t.
 */
static void mqtt_event_handler(void *handler_args, esp_event_base_t base, int32_t event_id, void *event_data)
{
    ESP_LOGD(TAG, "Event dispatched from event loop base=%s, event_id=%" PRIi32 "", base, event_id);
    esp_mqtt_event_handle_t event = event_data;
    esp_mqtt_client_handle_t client = event->client;
    int msg_id = 0;
    switch ((esp_mqtt_event_id_t)event_id)
    {
    case MQTT_EVENT_CONNECTED:
        MQTT_CONNECTED = 1;
        ESP_LOGI(TAG, "MQTT_EVENT_CONNECTED");
        msg_id = esp_mqtt_client_subscribe(client, "LSE/instalaciones/despachos/+/email_ocupante", 1);
        ESP_LOGI(TAG, "sent subscribe successful, msg_id=%d", msg_id);
        break;
    case MQTT_EVENT_DISCONNECTED:
        MQTT_CONNECTED = 0;
        ESP_LOGI(TAG, "MQTT_EVENT_DISCONNECTED");
        break;

    case MQTT_EVENT_SUBSCRIBED:
        ESP_LOGI(TAG, "MQTT_EVENT_SUBSCRIBED, msg_id=%d", event->msg_id);
        ESP_LOGI(TAG, "sent publish successful, msg_id=%d", msg_id);
        break;
    case MQTT_EVENT_UNSUBSCRIBED:
        ESP_LOGI(TAG, "MQTT_EVENT_UNSUBSCRIBED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_PUBLISHED:
        ESP_LOGI(TAG, "MQTT_EVENT_PUBLISHED, msg_id=%d", event->msg_id);
        break;
    case MQTT_EVENT_DATA:
        ESP_LOGI(TAG, "MQTT_EVENT_DATA");
        MessageFunction(event_data);
        break;
    case MQTT_EVENT_ERROR:
        ESP_LOGI(TAG, "MQTT_EVENT_ERROR");
        if (event->error_handle->error_type == MQTT_ERROR_TYPE_TCP_TRANSPORT)
        {
            log_error_if_nonzero("reported from esp-tls", event->error_handle->esp_tls_last_esp_err);
            log_error_if_nonzero("reported from tls stack", event->error_handle->esp_tls_stack_err);
            log_error_if_nonzero("captured as transport's socket errno", event->error_handle->esp_transport_sock_errno);
            ESP_LOGI(TAG, "Last errno string (%s)", strerror(event->error_handle->esp_transport_sock_errno));
        }
        break;
    default:
        ESP_LOGI(TAG, "Other event id:%d", event->event_id);
        break;
    }
}

static void mqtt_app_start(void)
{
    esp_mqtt_client_config_t mqtt_cfg = {
        .broker.address.uri = CONFIG_BROKER_URL,
        .broker.address.port = 1885};
#if CONFIG_BROKER_URL_FROM_STDIN
    char line[128];

    if (strcmp(mqtt_cfg.broker.address.uri, "FROM_STDIN") == 0)
    {
        int count = 0;
        printf("Please enter url of mqtt broker\n");
        while (count < 128)
        {
            int c = fgetc(stdin);
            if (c == '\n')
            {
                line[count] = '\0';
                break;
            }
            else if (c > 0 && c < 127)
            {
                line[count] = c;
                ++count;
            }
            vTaskDelay(10 / portTICK_PERIOD_MS);
        }
        mqtt_cfg.broker.address.uri = line;
        printf("Broker url: %s\n", line);
    }
    else
    {
        ESP_LOGE(TAG, "Configuration mismatch: wrong broker url");
        abort();
    }
#endif /* CONFIG_BROKER_URL_FROM_STDIN */

    esp_mqtt_client_handle_t client = esp_mqtt_client_init(&mqtt_cfg);
    mqtt_client = client;
    /* The last argument may be used to pass data to the event handler, in this example mqtt_event_handler */
    esp_mqtt_client_register_event(client, ESP_EVENT_ANY_ID, mqtt_event_handler, NULL);
    esp_mqtt_client_start(client);
}

void app_main(void)
{
    ESP_LOGI(TAG, "[APP] Startup..");
    ESP_LOGI(TAG, "[APP] Free memory: %" PRIu32 " bytes", esp_get_free_heap_size());
    ESP_LOGI(TAG, "[APP] IDF version: %s", esp_get_idf_version());

    esp_log_level_set("*", ESP_LOG_INFO);
    esp_log_level_set("mqtt_client", ESP_LOG_VERBOSE);
    esp_log_level_set("mqtt_example", ESP_LOG_VERBOSE);
    esp_log_level_set("transport_base", ESP_LOG_VERBOSE);
    esp_log_level_set("esp-tls", ESP_LOG_VERBOSE);
    esp_log_level_set("transport", ESP_LOG_VERBOSE);
    esp_log_level_set("outbox", ESP_LOG_VERBOSE);

    ESP_ERROR_CHECK(nvs_flash_init());
    ESP_ERROR_CHECK(esp_netif_init());
    ESP_ERROR_CHECK(esp_event_loop_create_default());

    /* This helper function configures Wi-Fi or Ethernet, as selected in menuconfig.
     * Read "Establishing Wi-Fi or Ethernet Connection" section in
     * examples/protocols/README.md for more information about this function.
     */
    ESP_ERROR_CHECK(example_connect());

    mqtt_app_start();
}