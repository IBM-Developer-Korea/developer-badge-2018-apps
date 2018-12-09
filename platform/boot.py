import ugfx
import machine
import network

sta_if = network.WLAN(network.STA_IF)
ap_if = network.WLAN(network.AP_IF)

import webrepl
webrepl.start()

ugfx.init()
