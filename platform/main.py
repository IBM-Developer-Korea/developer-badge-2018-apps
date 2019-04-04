import gc
import sys

import util
import ugfx
from util import *

rtc = machine.RTC()
appname = rtc.memory()
sys.path.append('/apps')

if appname:
    rtc.memory('')
    util.startup()
    #tim = machine.Timer(-1)
    #tim.init(period=2000, mode=machine.Timer.ONE_SHOT, callback=util.startup)
    gc.collect()
    app = __import__(appname.decode('ascii'))
    app.main()
else: # Cold boot
    ugfx.init()
    util.display_logo()
    util.startup()
    try:
        import home
        home.main()
    except Exception as e:
        print(e)
    else:
        gc.collect()
