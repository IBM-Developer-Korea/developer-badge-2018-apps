import network

import util

conf = util.Config('wifi')
if 'sta_if' in conf:
    sta_if = network.WLAN(network.STA_IF)
    sta_if.active(True)
    sta_conf = conf['sta_if']
    if 'ssid' in sta_conf:
        pw = sta_conf['password'] if 'password' in sta_conf else None
        sta_if.connect(sta_conf['ssid'], pw)
        del pw
    del sta_conf
del conf
