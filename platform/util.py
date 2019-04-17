import gc
import machine
import network
import time
import ujson as json
import uos
import upip

import ugfx

def reboot(pressed=True):
    machine.reset()

def restart():
    machine.deepsleep(1)

def unload(mod):
    import sys
    try:
        mod_name = mod.__name__
    except:
        mod_name = mod
        print('Module is not loaded yet')
    if mod_name in sys.modules:
        print('Delete module {}'.format(mod_name))
        del sys.modules[mod_name]
        try:
            del mod_name
        except:
            pass
        import gc
        gc.collect()

def run(appname='home'):
    rtc = machine.RTC()
    rtc.memory(appname)
    print('Restrt to run app {}'.format(appname))
    restart()

def execfile(filename):
    print('Run {}'.format(filename))
    return exec(open(filename).read(), globals())

def get_version():
    try:
        with open('version.txt') as fp:
            version = float(fp.read())
    except OSError:
        return 0.0
    return version

def startup(timer=None):
    conf = Config('global')
    for app in uos.listdir('/apps'):
        try:
            uos.stat('/apps/{}/boot.py'.format(app))
        except OSError:
            pass
        else:
            execfile('/apps/{}/boot.py'.format(app))
            gc.collect()
    del conf
    gc.collect()

def display_logo():
    ugfx.clear(ugfx.BLACK)
    ugfx.string(280, 228, 'v{}'.format(get_version()),
            'IBMPlexSans_Regular12', ugfx.WHITE)
    ugfx.display_image(40, 70, bytearray(open('ibm_logo.gif', 'rb').read()), 2, 300)
    ugfx.string_box(0, 140, ugfx.width(), 50, 'Developer Day 2018',
            'IBMPlexSans_Regular22', ugfx.HTML2COLOR(0x01d7dd), ugfx.justifyCenter)
    gc.collect()

def wait_network(timeout=10, interval=0.2):
    sta_if = network.WLAN(network.STA_IF)
    while timeout > 0:
        if sta_if.isconnected() and sta_if.ifconfig()[0] != '0.0.0.0':
            return True
        time.sleep(interval)
        timeout -= interval
    return False

def download_file(url, filename=None):
    if filename is None:
        filename = url.split('/')[-1]

    print('Downloading file from {}.'.format(url))
    print('It will be saved as \'{}\''.format(filename))

    try:
        st = uos.stat(filename)
        raise Exception('Already exist file')
    except OSError:
        pass

    if not wait_network(5):
        raise Exception('Not connected: check your internet')

    gc.collect()

    s = upip.url_open(url)
    s.setblocking(False)

    with open(filename, 'w') as f:
        BUF_LEN = 256
        try:
            while True:
                data = s.read(BUF_LEN)
                print('.',end='')
                # print(data,end='')
                if data is None or len(data) < BUF_LEN:
                    break
                f.write(data)
        except Exception as e:
            s.close()
            f.close()
            raise e

    s.close()
    print('\n')

def cat_file(filename):
    open(filename,"rb").read()

class Config:
    config_dir = '/config'

    def __init__(self, name):
        self.name = name
        self.data = {}
        try:
            with open('/config/{}.json'.format(name)) as fp:
                self.data = json.load(fp)
        except OSError:
            print('Cannot find config file, create new one.')
        except Exception as e:
            print(e)

    def __getitem__(self, key):
        if not key in self.data:
            raise KeyError(key)
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        return self.data.__setitem__(key, value)

    def __contains__(self, key):
        return key in self.data

    def save(self):
        # Create config_dir if do not exists
        try:
            uos.stat(self.config_dir)
        except OSError:
            uos.mkdir(self.config_dir)
        with open('{}/{}.json'.format(self.config_dir, self.name), 'w') as fp:
            json.dump(self.data, fp)
