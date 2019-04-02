import json
import network
import time
import math
import umqtt.simple as simple
import machine
import random

from util import Config, wait_network


sta_if = network.WLAN(network.STA_IF)

conf = Config('ibmiot')
if not conf.data:
    random.seed(time.time())
    conf.data = {
        'orgID': 'quickstart', # <<< org_id 
        'deviceType': 'badge2018',
        'deviceID': ''.join('{:02X}'.format(c) for c in sta_if.config('mac')),
        'user': 'use-token-auth',
        'authToken': 'badge{}'.format(str(random.random()).split('.')[1]),
    }
    conf.save()

clientID = 'd:' + conf.data['orgID'] + ':' + conf.data['deviceType'] + ':' + conf.data['deviceID']
broker = conf.data['orgID'] + '.messaging.internetofthings.ibmcloud.com'
statusTopic = b'iot-2/evt/status/fmt/json'
signalTopic = b'iot-2/evt/signal/fmt/json'
ledCommandTopic = b'iot-2/cmd/led/fmt/json'
irCommandTopic = b'iot-2/cmd/ir/fmt/json'

if conf.data['orgID'] == 'quickstart':
    c = simple.MQTTClient(clientID, broker, ssl=False)
    print('Quickstart URL: https://quickstart.internetofthings.ibmcloud.com/#/device/{}/sensor/'.format(
        conf.data['deviceID']))
else:
    c = simple.MQTTClient(clientID, broker,
            user=conf.data['user'], password=conf.data['authToken'], ssl=True)

# LED
led_red = machine.Pin(17, machine.Pin.OUT, value=0)
#led_blue = machine.Pin(16, machine.Pin.OUT, value=0)

# IR
rx = machine.RMT(rmt_mode=machine.RMT.RX,
        channel=4, clk_div=80, pin=machine.Pin(26), mem_block_num=4)
rx.config(filter_en=True, filter_ticks_thresh=100, idle_threshold=30000, rx_buf_size=4000)

tx = machine.RMT(rmt_mode=machine.RMT.TX,
        channel=0, clk_div=80, pin=machine.Pin(16), mem_block_num=4)
tx.config()


def sub_cb(topic, msg):
    obj = json.loads(msg)
    print((topic, msg, obj))
    if topic == ledCommandTopic:
        led_cb(obj)
    elif topic == irCommandTopic:
        ir_cb(obj)
    else:
        print('Unknown topic: {}'.format(topic))


def led_cb(obj):
  if obj['d']['target'] == 'red':
      led = led_red
  elif obj['d']['target'] == 'blue':
      led = led_blue
  else:
      print('Unknown target')
      return
  if obj['d']['action'] == 'on':
      led.value(1)
  elif obj['d']['action'] == 'off':
      led.value(0)
  elif obj['d']['action'] == 'toggle':
      led.value(1 if led.value() == 0 else 0)
  else:
      print('Unknown action')
      return

def ir_cb(obj):
    if obj['d']['action'] == 'record':
        print('Recording IR signal..')
        cmd = rx.receive()
        rcmd = list(map(lambda x: [[x[0][0], 1 - x[0][1]], [x[1][0], 1 - x[1][1]]], cmd))
        print(rcmd)
        c.publish(signalTopic, json.dumps({'d': {'cmd': rcmd}}))
    elif obj['d']['action'] == 'send':
        tx.send(obj['d']['cmd'])

def sineVal(minValue, maxValue, duration, count):
    sineValue = math.sin(2.0 * math.pi * count / duration) * (maxValue - minValue) / 2.0
    return '{:.2f}'.format(sineValue)

def main():
    c.set_callback(sub_cb)
    if not wait_network():
        print('Cannot connect WiFi')
        raise Exception('Cannot connect WiFi')

    c.connect()
    if conf.data['orgID'] != 'quickstart':
        c.subscribe(ledCommandTopic)
        c.subscribe(irCommandTopic)
    print('Connected, waiting for event ({})'.format(conf.data['deviceID']))

    status = {'d': {'sine':{}}}
    count = 0
    try:
        while True:
            status['d']['sine'] = sineVal(-1.0, 1.0, 16, count)
            count += 1
            c.publish(statusTopic, json.dumps(status))
            time.sleep_ms(10000)
            #c.wait_msg()
            c.check_msg()
    finally:
        c.disconnect()
        print('Disonnected')
