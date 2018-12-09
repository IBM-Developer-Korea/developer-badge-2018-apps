import machine
import network
import time

import ugfx

import util

ibm_st = ugfx.Style(ugfx.Font('IBMPlexSans_Regular22'))

ibm_st.set_background(ugfx.BLACK)
ibm_st.set_focus(ugfx.WHITE)
ibm_st.set_pressed([
        ugfx.WHITE,
        ugfx.WHITE,
        ugfx.BLACK,
        ugfx.BLACK,
])
ibm_st.set_enabled([
    ugfx.BLUE,
    ugfx.GREEN,
    #HTML2COLOR(0x01d7dd),
    ugfx.HTML2COLOR(0x3c3c3b),
    ugfx.YELLOW,
])
ibm_st.set_disabled([
        ugfx.WHITE,
        ugfx.WHITE,
        ugfx.BLACK,
        ugfx.BLACK,
])

class WifiConfig:

    def __init__(self):
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)
        self.status_box = None
        self.saved_config = None
        self.window = None

        ugfx.input_init()
        ugfx.set_default_font('IBMPlexSans_Regular22')

    def get_status(self, interface):
        for stat in dir(network):
            if stat.startswith('STAT_'):
                if getattr(network, stat) == interface.status():
                    return stat.replace('STAT_', '')

    def set_status(self, text):
        print(text)
        if self.status_box and self.status_box.visible():
            self.status_box.text(text)

    def create_window(self):
        if self.window and self.window.enabled != 0:
            self.teardown()
            del self.window
        self.window = ugfx.Container(5, 5, ugfx.width() - 10, ugfx.height() - 10)
        self.window.show()
        return self.window

    def create_status_box(self):
        self.status_box = ugfx.Textbox(10, 30,
                self.window.width() - 20, self.window.height() - 60,
                parent=self.window)
        self.status_box.enabled(False)

    def teardown(self, pressed=True):
        if pressed and self.window and self.window.enabled() != 0:
            self.window.hide()
            self.window.destroy()
            ugfx.poll()

    def scan(self):
        if not self.sta_if.active():
            self.sta_if.active(True)
        self.create_status_box()
        self.set_status('Scanning..')
        self.scan_configs = self.sta_if.scan()
        self.status_box.destroy()

    def connect_network(self, ssid, pw=None, timeout=15):
        self.create_window()
        self.window.text(10, 10, 'Connecting to {}'.format(ssid), ugfx.BLACK)
        if not self.sta_if.active():
            self.sta_if.active(True)
        else:
            self.sta_if.active(False)
            time.sleep(0.3)
            self.sta_if.active(True)
        self.create_status_box()
        self.sta_if.connect(ssid, pw)
        tried = 0
        while self.get_status(self.sta_if) != 'GOT_IP' and tried < timeout:
            self.set_status(self.get_status(self.sta_if))
            time.sleep(0.2)
            tried += 0.2
        if self.get_status(self.sta_if) == 'GOT_IP':
            self.set_status('Connected!')
            config = util.Config('wifi')
            config['sta_if'] = {
                'ssid': ssid,
                'password': pw,
            }
            config.save()
            time.sleep(1)
            self.set_status('WiFi configuration saved.')
            time.sleep(1)
            util.reboot()
        else:
            self.set_status('Connection failed.')

    def network_selected(self, pressed):
        if not pressed:
            return

        scan_config = self.scan_configs[self.scan_list.selected_index()]
        self.saved_config = scan_config
        ugfx.input_attach(ugfx.BTN_A, None)
        self.scan_list.destroy()
        if scan_config[4] == 0:
            self.connect_network(scan_config[0].decode('utf-8'))
        else:
            self.get_password()

    def list_network(self):
        w = self.create_window()
        self.scan()

        self.window.hide()
        self.scan_list = ugfx.List(10, 10, w.width() - 20, w.height() - 20, parent = w)
        for scan_config in self.scan_configs:
            ap_name = '{} {}'.format(
                '@' if scan_config[4] else ' ',
                scan_config[0].decode('utf-8')
            )
            self.scan_list.add_item(ap_name)
            print(scan_config)

        ugfx.input_attach(ugfx.BTN_A, self.network_selected)
        ugfx.input_attach(ugfx.BTN_B, util.reboot)
        self.window.show()

    def kb_handler(self, keycode):
        if keycode == 13: # GKEY_ENTER
            pw = self.pw_input.text()
            if self.connect_network(self.saved_config[0].decode('utf-8'), pw):
                print(pw)

    def get_password(self):
        ugfx.input_attach(ugfx.BTN_B, util.reboot)
        w = self.create_window()
        edit_size = 40
        ugfx.Textbox(5, 0, w.width() - 12, edit_size, text='Input password', parent=w).enabled(False)
        self.pw_input = ugfx.Textbox(5, 7 + edit_size, w.width() - 12, edit_size, parent=w)
        self.kb = ugfx.Keyboard(5, edit_size * 2 + 12, w.width() - 12, w.height() - edit_size * 2 - 20, parent=w)
        self.kb.set_keyboard_callback(self.kb_handler)
