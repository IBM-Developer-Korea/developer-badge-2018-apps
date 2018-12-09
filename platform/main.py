from util import *

def display_logo():
    ugfx.clear(ugfx.BLACK)
    ugfx.string(280, 228, 'v{}'.format(get_version()),
            'IBMPlexSans_Regular12', ugfx.WHITE)
    ugfx.display_image(40, 10, bytearray(open('ibm_logo.gif', 'rb').read()), 2, 300)
    ugfx.string_box(0, 140, ugfx.width(), 50, 'Developer Day 2018',
            'IBMPlexSans_Regular22', ugfx.HTML2COLOR(0x01d7dd), ugfx.justifyCenter)
    gc.collect()

def wifi(start=True):
    ap_if = network.WLAN(network.AP_IF)
    ap_if.active(True)

    sta_if.active(True)
    #sta_if.connect('badge', 'helloiot')
    #sta_if.ifconfig()

def execfile(filename):
    print(filename)
    return exec(open(filename).read(), globals())

rtc = machine.RTC()
appname = rtc.memory()

if appname:
    rtc.memory('')
    tim = machine.Timer(-1)
    tim.init(period=2000, mode=machine.Timer.ONE_SHOT, callback=wifi)
    execfile(str(appname.decode('ascii')) + '.py')
else: # Cold boot
    display_logo()
    wifi()
    try:
        uos.stat('home.py')
    except:
        pass
    else:
        execfile('home.py')
