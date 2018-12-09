import ugfx
import ujson as json
import uos

def reboot():
    import machine
    machine.reset()

def restart():
    import machine
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

def run(appname):
    import machine
    rtc = machine.RTC()
    rtc.memory(appname)
    restart()

def get_version():
    try:
        with open('version.txt') as fp:
            version = float(fp.read())
    except OSError:
        return 0.0
    return version


class Config:
    config_dir = '/config'

    def __init__(self, name):
        self.name = name
        self.data = {}
        try:
            with open('/config/{}.json'.format(name)) as fp:
                data = json.load(fp)
        except OSError:
            print('Cannot find config file, create new one.')
        except Exception as e:
            print(e)

    def __getitem__(self, key):
        return self.data.__getitem__(key)

    def __setitem__(self, key, value):
        return self.data.__setitem__(key, value)

    def save(self):
        # Create config_dir if do not exists
        try:
            uos.stat(self.config_dir)
        except OSError:
            uos.mkdir(self.config_dir)
        with open('{}/{}.json'.format(self.config_dir, self.name), 'w') as fp:
            json.dump(self.data, fp)


def abc():
    return 1
