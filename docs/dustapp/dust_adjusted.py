import time
import machine
import ugfx
from machine import Pin
from machine import ADC

# init ugfx
ugfx.init()
ugfx.clear(ugfx.BLACK)

# Set LED pin for output
sharpLEDPin = Pin(32, Pin.OUT)
sharpVoPin = ADC(Pin(36))

# ADC Setup
sharpVoPin.atten(ADC.ATTN_11DB)

Vcc = 5

# Output volate at no dust in V
Voc = 0.6 # 0.1 to 1.1

# Sensitivity in units of V per 100ug/m3.
K = 0.5 # 0.425 to 0.575


def readValue():
    global Voc

    # Turn on ILED
    sharpLEDPin.value(0)

    # Wait 0.28 ms 
    # time.sleep_us(280) # Actually, it took 0.4 ms.
    time.sleep_us(196) # It was measured about value of 0.28 ms

    VoRaw = sharpVoPin.read()

    # Wait 0.04 ms
    #time.sleep_us(40)

    # Turn off ILED
    sharpLEDPin.value(1)

    # Compute the output voltage in Volts.
    Vo = VoRaw / 4095.0 * 5.0

    # Convert to Dust Density in units of ug/m3.
    dV = Vo - Voc
    if dV < 0:
        dV = 0
        Voc = Vo
    
    dustDensity = dV / K * 100.0
    
    print('VoRaw={}, Vo={} mV, Density={} ug/m3'.format(VoRaw, Vo*1000.0, dustDensity))

    #time.sleep_us(10000 - 320)
    time.sleep_us(4000)

while True:
  readValue()