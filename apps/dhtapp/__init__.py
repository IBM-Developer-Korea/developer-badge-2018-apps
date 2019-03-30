import ugfx, time
from dht import DHT11, DHT22

def main():
    #h = DHT11(machine.Pin(33)) # J8
    h = DHT11(machine.Pin(26)) # J7

    ugfx.set_default_font('IBMPlexMono_Bold24')
    ugfx.clear()
    ugfx.Label(40, 0, 240, 60, text='DHT11/22 Demo')

    ugfx.set_default_font('IBMPlexMono_Regular24')
    l = ugfx.Label(40, 60, 240, 120, text='')

    while True:
        h.measure()
        h.temperature()
        l.text('temperature:{},humidity:{}'.format(h.temperature(), h.humidity()))
        time.sleep(1)