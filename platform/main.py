import gc

import util
from util import *

rtc = machine.RTC()
appname = rtc.memory()

if appname:
    rtc.memory('')
    tim = machine.Timer(-1)
    tim.init(period=2000, mode=machine.Timer.ONE_SHOT, callback=util.startup)
    gc.collect()
    __import__('apps.{}'.format(appname.decode('ascii')))
    gc.collect()
else: # Cold boot
    display_logo()
    util.startup()
    try:
        __import__('apps.home')
    except:
        pass
    else:
        gc.collect
