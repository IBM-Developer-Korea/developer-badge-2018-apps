import ugfx
import machine
import network
import uos as os # for uPyCraft

sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)

import webrepl
webrepl.start()

ugfx.init()
