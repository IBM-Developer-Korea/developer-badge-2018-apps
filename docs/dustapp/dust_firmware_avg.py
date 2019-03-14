import time
import machine
import ugfx
import gp2y1014au

from home import styles

# init
dust_sensor = gp2y1014au.GP2Y1014AU(iled=32, vo=36, K=0.5, Voc=0.6)

# Smooth
Vos = 0.8
idx = 0

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
status_box.visible(1) # hide

def readValue():
    global Voc, Vos, idx

    VoRaw = dust_sensor.readRawVo(220, 40) # adjusted 280 -> 220

    # Compute the output voltage in Volts.
    Vo = VoRaw / 4095.0 * 5.0

    # Exponential Moving Average
    # https://www.investopedia.com/terms/e/ema.asp
    # EMA(t) = Value(t)*k + EMA(y) * (1-k)
    # k = 2 / (N+1)
    # k = 0.005 where N = 399
    Vos = Vo * 0.005 + Vos * 0.995
        
    # print('{}, {}, {}, {}'.format(idx, VoRaw, Vo*1000.0, Vos*1000.0))

    density = (Vos - 0.6) / 0.5 * 100.0
    if density < 0:
      density = 0

    print('{}, {}, {}'.format(Vo*1000.0, Vos*1000.0, density*10))
    
    status_box.text(density+'ug/m3')

    idx += 1

    #time.sleep_us(10000 - 320)
    time.sleep_us(4000)

while True:
  readValue()