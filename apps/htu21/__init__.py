import time
import ugfx

from htu21 import htu21d

def main():
    h = htu21d.HTU21D(25, 26)

    ugfx.set_default_font('IBMPlexMono_Bold48')
    l = ugfx.Label(40, 60, 240, 120, text='')

    while True:
        try:
            l.text('{}'.format(h.temperature))
        except OSError:
            l.text('OSError')
        time.sleep(0.5)
