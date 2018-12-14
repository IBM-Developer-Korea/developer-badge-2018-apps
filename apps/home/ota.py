import gc
import network
import upip

import ugfx

from util import get_version, reboot

version_url = 'https://badge.arcy.me/ota/version.json'

class OtaException(Exception):
    pass

def install_url(url, install_path=''):
    gc.collect()

    f1 = upip.url_open(url)
    try:
        f2 = upip.uzlib.DecompIO(f1, 31)
        f3 = upip.tarfile.TarFile(fileobj=f2)
        meta = upip.install_tar(f3, install_path)
    finally:
        f1.close()
    reboot()

def check_version(timer=None):
    sta_if = network.WLAN(network.STA_IF)
    if not sta_if.isconnected() or sta_if.ifconfig()[0] == '0.0.0.0':
        raise OtaException('OTA: Network is not ready.')
    try:
        f = upip.url_open(version_url)
    except:
        raise OtaException('Cannot get ota version')

    try:
        data = upip.json.load(f)
    except:
        f.close()
        raise OtaException('Cannot decode OTA json data')
    else:
        f.close()
        if data['version'] != get_version():
            return data
        else:
            return None
