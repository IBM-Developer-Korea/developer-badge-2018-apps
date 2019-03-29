import ujson as json
import ugfx
import util
import network
import utime as time
import urequests
import umqtt.simple as simple

from machine import Pin
from dustapp import iotfcfg
from dustapp.buzzer import Buzzer

class IoTFoundation():
    def __init__(self):
        # TODO: input user's name
        self.username = ''.join('{:02X}'.format(c) for c in network.WLAN(network.STA_IF).config('mac'))
        
        # LED
        self.led_red = Pin(17, Pin.OUT, value=0)
        self.led_blue = Pin(16, Pin.OUT, value=0)

        # Buzzer
        self.buzzer = Buzzer()

        self.init_iotf()

    EVENT_TOPIC_BUTTON = b'iot-2/evt/button/fmt/json'
    EVENT_TOPIC_DUST = b'iot-2/evt/dust/fmt/json'
    COMMAND_TOPIC_LED = b'iot-2/cmd/led/fmt/json'
    COMMAND_TOPIC_BUZZER = b'iot-2/cmd/buzzer/fmt/json'

    def process(self):
        try:
            self.mqtt.check_msg()
        except Exception as e:
            print(e)

    def disconnect(self):
        try:
            self.mqtt.disconnect()
        except Exception as e:
            pass

    def init_iotf(self):
        # Check for network availability
        print('Waiting for network')
        if not util.wait_network(3):
            print('Cannot connect WiFi')
            raise Exception('Cannot connect WiFi')
        
        sta_if = network.WLAN(network.STA_IF)
        mac_addr = ''.join('{:02X}'.format(c) for c in sta_if.config('mac'))

        orgId = iotfcfg.orgId
        deviceType = iotfcfg.deviceType
        deviceId = iotfcfg.deviceId if hasattr(iotfcfg, 'deviceId') else mac_addr
        user = 'use-token-auth'
        authToken = iotfcfg.authToken

        clientID = 'd:' + orgId + ':' + deviceType + ':' + deviceId
        broker = orgId + '.messaging.internetofthings.ibmcloud.com'

        self.deviceId = deviceId

        if orgId == 'quickstart':
            self.mqtt = simple.MQTTClient(clientID, broker)
        else:
            self.mqtt = simple.MQTTClient(clientID, broker, user=user, password=authToken, ssl=True)
        self.mqtt.set_callback(self.sub_cb)
        self.mqtt.connect()

        if orgId == 'quickstart':
            print('https://quickstart.internetofthings.ibmcloud.com/?deviceId=test#/device/{}'.format(deviceId))
        else:
            self.mqtt.subscribe(self.COMMAND_TOPIC_LED)
            self.mqtt.subscribe(self.COMMAND_TOPIC_BUZZER)

        print('DeviceID is {}'.format(deviceId))
        print('IoT Ready')

    def getDeviceId(self):
        return self.deviceId

    def sub_cb(self, topic, msg):
        obj = json.loads(msg)
        print((topic, msg, obj))
        if topic == self.COMMAND_TOPIC_LED:
            self.led_cb(obj)
        elif topic == self.COMMAND_TOPIC_BUZZER:
            self.buzzer_cb(obj)

    #
    def check_network(self):
        print('Wait for network')
        if not util.wait_network():
            print('Cannot connect WiFi')
            raise Exception('Cannot connect WiFi')
        print('Ready')

    # Events
    def select_key_cb(self, key, pressed):
        event = {'d': {'char': key, 'type': 'keydown' if pressed else 'keyup' }}
        self.mqtt.publish(self.EVENT_TOPIC_BUTTON, json.dumps(event))

    def send_dustinfo(self, data):
        event = {'d': data}
        self.mqtt.publish(self.EVENT_TOPIC_DUST, json.dumps(event))

    # Command Callback
    def led_cb(self, obj):
        if obj['d']['target'] == "red":
            led = self.led_red
        elif obj['d']['target'] == "blue":
            led = self.led_blue
        else:
            print('Unknown target')
            return
        if obj['d']['action'] == "on":
            led.value(1)
        elif obj['d']['action'] == "off":
            led.value(0)
        elif obj['d']['action'] == "toggle":
            led.value(1 if led.value() == 0 else 0)
        else:
            print('Unknown action')
            return
    
    def buzzer_cb(self, obj):
        title = obj['d']['title']

        print('buzzer:{}'.format(title))

        self.buzzer.playnotes(title)
