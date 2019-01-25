import ujson as json
import uos
import util
import network
import utime as time
import urequests
import ugfx

from home import styles

class TagMain():

    IS_TEST = False

    # Labels
    name = '홍길동'
    org = 'IBM'

    # Nametag Image Server
    url = 'https://2018-devday-nametag.au-syd.mybluemix.net/nametag'
    
    def __init__(self):
        # initialize ugfx
        ugfx.init()

        # Container
        width = ugfx.width()
        height = ugfx.height()
        self.container = ugfx.Container(0, 0, width, height, style=styles.ibm_st)

        # Status box
        self.create_status_box()

        # Nametag Image
        self.filename = '/nametag.gif'

    def run(self):

        # Check if it was downloaded before
        try:
            if self.IS_TEST:
                uos.remove(self.filename)
            else:
                f = open(self.filename, 'r')
                self.display_nametag(bytearray(f.read()))
                f.close()
                return
        except Exception as  e:
            print(e)
            print('nametag image file ({}) loading failure'.format(self.filename))

        # Show container
        self.container.show()
        self.open_status_box()

        # Check network
        try:
          self.check_network()
        except Exception as e:
            self.set_status_text(str(e))
            return

        # Get Device ID
        sta_if = network.WLAN(network.STA_IF)
        deviceId = ''.join('{:02X}'.format(c) for c in sta_if.config('mac'))
        self.set_status_text('Your device ID is {}'.format(deviceId))

        # TODO: Get device owner by device id

        # Download nametag
        try:
            self.download_nametag()
        except Exception as e:
            self.set_status_text(str(e))
            return
        
    def download_nametag(self):
        payload = {
            "name": self.name,
            "org": self.org,
            "ext": self.filename.split('.')[-1] # file extension
        }
        headers = {'Content-Type':'application/json'}
        data = (json.dumps(payload)).encode()
        r = urequests.post(self.url, data=data, headers=headers)
        if r.status_code == 200:
            ugfx.display_image(0, 0, bytearray(r.content))

            if not self.IS_TEST:
                # Write it as a file
                f = open(self.filename, 'wb')
                f.write(bytearray(r.content))
                f.close()
        else:
          print(r.text)
          raise Exception(r.text)
        r.close()

    def restart(self):
        util.run('nametag')

    def exit(self):
        util.reboot()

    def check_network(self):
        self.set_status_text('Wait for network')
        if not util.wait_network():
            raise Exception('Cannot connect WiFi')
        self.set_status_text('Network is ready')

    def display_nametag(self, data):
        ugfx.display_image(0, 0, data)

    # Status Box
    def create_status_box(self, y=40):
        self.status_box = ugfx.Textbox(10, y, self.container.width() - 20, self.container.height() - y - 20, parent=self.container)
        self.status_box.enabled(False)
        self.status_box.visible(0) # hide

    def open_status_box(self):
        print('---open_status_box---')
        self.status_box.visible(1) # show

    def set_status_text(self, text):
        print('---set_status_text---:{}'.format(text))
        if self.status_box and self.status_box.visible():
            self.status_box.text(text)

    def close_status_box(self):
        print('---close_status_box---')
        self.status_box.visible(0) # hide
    
    def destroy_status_box(self):
        self.status_box.destroy()
