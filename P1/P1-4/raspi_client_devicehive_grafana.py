# Copyright (C) 2018 DataArt
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# =============================================================================


import glob
import hashlib
import sched
import time
import threading
from devicehive import Handler
from devicehive import DeviceHive
from sense_hat import SenseHat

#SERVER_URL = 'http://playground.devicehive.com/api/rest'
SERVER_URL = 'ws://10.8.42.19/api/websocket'
#SERVER_REFRESH_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJwYXlsb2FkIjp7InVzZXJJZCI6MTAsImFjdGlvbnMiOlsiR2V0TmV0d29yayIsIkdldERldmljZSIsIkdldERldmljZVN0YXRlIiwiR2V0RGV2aWNlTm90aWZpY2F0aW9uIiwiR2V0RGV2aWNlQ29tbWFuZCIsIkdldERldmljZUNsYXNzIiwiUmVnaXN0ZXJEZXZpY2UiLCJDcmVhdGVEZXZpY2VOb3RpZmljYXRpb24iLCJDcmVhdGVEZXZpY2VDb21tYW5kIiwiVXBkYXRlRGV2aWNlQ29tbWFuZCIsIkdldEN1cnJlbnRVc2VyIiwiVXBkYXRlQ3VycmVudFVzZXIiLCJNYW5hZ2VUb2tlbiJdLCJuZXR3b3JrSWRzIjpbIjEwIl0sImRldmljZUlkcyI6WyIqIl0sImV4cGlyYXRpb24iOjE1MzU4MDMxNDMzMTQsInRva2VuVHlwZSI6IlJFRlJFU0gifX0.5qgXmEZTvnMlMjByGGhcxpfD0s_TSFM3cAQKoo22Ees' # 'PUT_YOUR_REFRESH_TOKEN_HERE'
SERVER_REFRESH_TOKEN = 'eyJhbGciOiJIUzI1NiJ9.eyJwYXlsb2FkIjp7ImEiOlswXSwiZSI6MTc1NjcxNzMzMjcwMiwidCI6MCwidSI6MSwibiI6WyIqIl0sImR0IjpbIioiXX19.T2hssBioSzeFGg1uq4S9TTFUoIOp8dNq9uilfmSo418'
DEVICE_ID = '06612507-' \
            + hashlib.md5(SERVER_REFRESH_TOKEN.encode()).hexdigest()[0:8]
LED_PIN = 17
debug = 1

''' Real or fake GPIO handler.
'''
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
except ImportError:
    class FakeGPIO(object):
        OUT = "OUT"

        def __init__(self):
            print('Fake gpio initialized')

        def setup(self, io, mode):
            print('Set gpio {0}; Mode: {1};'.format(io, mode))

        def output(self, io, vlaue):
            print('Set gpio {0}; Value: {1};'.format(io, vlaue))

    GPIO = FakeGPIO()


''' Temperature, pressure, humidity sensor wrapper. Gets temperature readings form file.
'''
class MultiSensor(object):
    def __init__(self):
        self.last_good_temp = 0.0
        self.last_good_pressure = 0.0
        self.last_good_humidity = 0.0
        self.sense = SenseHat()

    def get_temp(self):
        self.last_good_temp = float(self.sense.get_temperature())
        if debug:
            print("Temperature: %0.2f C" % self.last_good_temp)

        return self.last_good_temp

    def get_pressure(self):
        self.last_good_pressure = float(self.sense.get_pressure())
        if debug:
            print("Pressure: %s Millibars" % self.last_good_pressure)
        return self.last_good_pressure

    def get_humidity(self):
        self.last_good_humidity = float(self.sense.get_humidity())
        if debug:
            print("Humidity: %s %%rH" % self.last_good_humidity)
        return self.last_good_humidity

class SampleHandler(Handler):
    #INTERVAL_SECONDS = 5
    INTERVAL_SECONDS = 2

    def __init__(self, api, device_id=DEVICE_ID):
        super(SampleHandler, self).__init__(api)
        self._device_id = device_id
        self._device = None
        self._sensor = MultiSensor()
        self._scheduler = sched.scheduler(time.time, time.sleep)
        GPIO.setup(LED_PIN, GPIO.OUT)
        GPIO.output(LED_PIN, 0)
        self.num_notification = 0
        print('DeviceId: ' + self._device_id)
        self._sensor.sense.show_message("ALERT!!!", scroll_speed=0.25, text_colour=[255,0,0], back_colour=[0,0,0])

    def _timer_loop(self):
        self.num_notification += 1
        if debug:
            print('\n[NOTIFICATION][%d]\n' % self.num_notification)
        t = self._sensor.get_temp()
        p = self._sensor.get_pressure()
        h = self._sensor.get_humidity()
        self._device.send_notification('temperature', parameters={'value': t})
        self._device.send_notification('pressure', parameters={'value': p})
        self._device.send_notification('humidity', parameters={'value': h})

        self._scheduler.enter(self.INTERVAL_SECONDS, 1, self._timer_loop, ())

    def handle_connect(self):
        self._device = self.api.put_device(self._device_id)
        self._device.subscribe_insert_commands()
        print('Connected')
        self._timer_loop()
        t = threading.Thread(target=self._scheduler.run)
        t.setDaemon(True)
        t.start()

    def handle_command_insert(self, command):
        if command.command == 'led/on':
            GPIO.output(LED_PIN, 1)
            self._sensor.sense.clear(0,255,0)
            command.status = "Ok"
        elif command.command == 'led/off':
            GPIO.output(LED_PIN, 0)
            self._sensor.sense.clear()
            command.status = "Ok"
        elif command.command == 'alert':
            self._sensor.sense.show_message("ALERT!!!", scroll_speed=0.25, text_colour=[255,0,0], back_colour=[0,0,0])
            command.status = "Ok"
        else:
            command.status = "Unknown command"
        command.save()


dh = DeviceHive(SampleHandler)
dh.connect(SERVER_URL, refresh_token=SERVER_REFRESH_TOKEN)
