import time
import machine
import ugfx
from machine import Pin
from machine import ADC

from home import styles

# init ugfx
ugfx.init()
ugfx.clear(ugfx.BLACK)

# Container
width = ugfx.width()
height = ugfx.height()
container = ugfx.Container(0, 0, width, height, style=styles.ibm_st)

y = 40
status_box = ugfx.Textbox(10, y, container.width() - 20, container.height() - y - 20, parent=container)
status_box.enabled(False)
status_box.visible(1) # show

container.show()

# Set LED pin for output
sharpLEDPin = Pin(32, Pin.OUT)
sharpVoPin = ADC(Pin(36))

# ADC Setup
sharpVoPin.atten(ADC.ATTN_11DB)

# Output volate at no dust in V
Voc = 0.6 # 0.1 to 1.1

# Sensitivity in units of V per 100ug/m3.
K = 0.5 # 0.425 to 0.575

# Smooth
Vos = 0.8
idx = 0

def readValue():
    global Voc, Vos, idx

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
    Vo = VoRaw / 4095.0 * 3.3

    # Exponential Moving Average
    # https://www.investopedia.com/terms/e/ema.asp
    # EMA(t) = Value(t)*k + EMA(y) * (1-k)
    # k = 2 / (N+1)
    # k = 0.005 where N = 399
    Vos = Vo * 0.005 + Vos * 0.995
    dV = Vos - Voc
    if dV < 0:
        dV = 0

    # Convert to Dust Density in units of ug/m3.
    dustDensity = dV / K * 100.0
    
    #print('VoRaw={}, Vo={} mV, Density={} ug/m3'.format(VoRaw, Vo*1000.0, dustDensity))
    
    print('{}, {}, {}'.format(idx, Vo*1000.0, Vos*1000.0))

    status_box.text(str(dustDensity)+'ug/m3')

    idx += 1

    #time.sleep_us(10000 - 320)
    time.sleep_us(4000)

while True:
  readValue()
