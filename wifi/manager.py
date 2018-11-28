import machine
import network
import time

import ugfx

button_pushed = None

class WifiConfig:

    def __init__(self):
        self.sta_if = network.WLAN(network.STA_IF)
        self.ap_if = network.WLAN(network.AP_IF)

        ugfx.input_init()

    def scan(self):
        if not self.sta_if.active():
            self.sta_if.active(True)
        print('Scanning..')
        self.scan_configs = self.sta_if.scan()

    def network_selected(self, pressed):
        if not pressed:
            return

        scan_config = self.scan_configs[self.scan_list.selected_index()]
        print(scan_config)
        ugfx.input_attach(ugfx.BTN_A, None)
        self.teardown()

    def list_network(self):
        self.scan()

        w = ugfx.Container(5, 5, ugfx.width() - 10, ugfx.height() - 10)
        self.window = w
        ugfx.set_default_font('IBMPlexSans_Regular22')

        self.scan_list = ugfx.List(10, 10, w.width() - 20, w.height() - 20, parent = w)
        for scan_config in self.scan_configs:
            ap_name = '{} {}'.format(
                '@' if scan_config[4] else ' ',
                scan_config[0].decode('utf-8')
            )
            self.scan_list.add_item(ap_name)
            print(scan_config)
        w.show()

        ugfx.input_attach(ugfx.BTN_A, self.network_selected)

    def teardown(self):
        self.window.hide()
        self.scan_list.destroy()
        self.window.destroy()
        ugfx.poll()

    def kb_handler(self, keycode):
        if keycode == 13: # GKEY_ENTER
            pw = self.pw_input.text()
            print(pw)
            self.window.destroy()

    def get_password(self):
        w = ugfx.Container(5, 5, ugfx.width() - 12, ugfx.height() - 12)
        self.window = w
        edit_size = 40
        self.pw_input = ugfx.Textbox(5, 5, w.width() - 12, edit_size, parent=w)
        self.kb = ugfx.Keyboard(5, edit_size + 12, w.width() - 12, w.height() - edit_size - 20, parent=w)
        self.kb.set_keyboard_callback(self.kb_handler)
        w.show()
