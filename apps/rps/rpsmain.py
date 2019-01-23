import ujson as json
import ugfx
import util
import network
import time
import urequests
import umqtt.simple as simple

from rps import iotf as iotfcfg
from rps.views import RPSCommonView
from rps.views import GameListView, ActionMenuView, MessagePopupView
from home import styles

class RPSViewManager(RPSCommonView):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.views = {}
        self.current_view = None
        self.previous_view = None

        # Initialize Input
        ugfx.input_init()
        
        # A/B Button Handler
        ugfx.input_attach(ugfx.BTN_A, self.select_a_cb)
        ugfx.input_attach(ugfx.BTN_B, self.select_b_cb)

        # Title
        self.set_title('RPS Game')

        # Message Box
        self.message_box = ugfx.Label(0, self.container.height() - 88, self.container.width(),  88, '', parent=self.container, style=styles.wb, justification=ugfx.Label.LEFT)

        # Status box
        self.create_status_box()

        # Message Popup
        self.message_popup_view = MessagePopupView(manager=self)

        # TODO: Splash screen
        #
    
    def show(self):
        self.container.show()

    # Message Box Label
    def set_message_box(self, msg=''):
      self.message_box.text(msg)

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

    # Sub-view control
    def attach_view_cb(self, view):
        self.views[id(view)] = view
  
    def appear_view(self, view):
        print('---appear_view---: {0} -> {1}'.format(self.previous_view, view))
        if self.current_view != None and id(self.current_view) != id(view):
            self.current_view.hide()
            self.previous_view = self.current_view
        self.current_view = view
        view.show()

    def close_view(self, view):
        print('---close_view---: {0} -> {1}'.format(view, self.previous_view))
        if self.previous_view != None:
            self.appear_view(self.previous_view)
            self.previous_view = None

    def select_key_cb(self, key, pressed):
        # check if current view is assigned
        if self.current_view == None:
          print('current_view is None')
          return
        
        if pressed:
            self.current_view.on_key_pressed(key)
        else:
            self.current_view.on_key_released(key)

    def select_a_cb(self, pressed=True):
        self.select_key_cb(ugfx.BTN_A, pressed)

    def select_b_cb(self, pressed=True):
        self.select_key_cb(ugfx.BTN_B, pressed)

    def destroy(self):
        for id in self.views:
            self.views[id].destroy()
        self.status_box.destroy()
        super.destroy()

    def openMessagePopup(self, title='', message='', fg_color=ugfx.GREY, bg_color=ugfx.IBMCoolGrey10):
        self.message_popup_view.set_title(title)
        self.message_popup_view.set_text(message)
        self.message_popup_view.set_color(fg_color, bg_color)
        self.appear_view(self.message_popup_view)
        return self.message_popup_view

    def closeDialogPopup(self):
        print('close!')

class RPSGame():
    
    EVENT_TOPIC_RPS = b'iot-2/evt/rps/fmt/json'
    COMMAND_TOPIC_RPS = b'iot-2/cmd/rps/fmt/json'

    default_font = 'NanumSquareRound_Regular16'

    def __init__(self):
        # initialize ugfx
        ugfx.init()

        # Create RPS View manager
        self.view_manager = RPSViewManager(self)

    def run(self):

        # TODO: input user's name
        self.username = ''.join('{:02X}'.format(c) for c in network.WLAN(network.STA_IF).config('mac'))
        
        # Show
        self.view_manager.show()

        # Create views and register to the view manager
        self.game_list_view = GameListView(manager=self.view_manager)
        self.action_menu_view = ActionMenuView(manager=self.view_manager)
        
        # Initialize IoT
        try:
          self.init_iotf()
        except Exception as e:
            print(e)
            print(e.args)
            msg = e.args[0]
            self.view_manager.openMessagePopup('Error', msg, ugfx.BLACK, ugfx.RED)
            return

        # List Games
        self.list_games()

        try:
            while True:
                self.mqtt.check_msg()
                time.sleep_ms(500)
        finally:
            self.mqtt.disconnect()
            print('Disconnected')

    def exit(self):
        #self.destroy()
        #util.run('home')
        util.reboot()

    def message_cb(self, msg):
        print(msg)
        self.view_manager.set_message_box(msg)

    def destroy(self):
        self.view_manager.destroy()

    def test(self):
        popup = self.view_manager.openMessagePopup('HELP', 'AAAAAAA', ugfx.BLACK, ugfx.RED)
        popup.set_select_result_cb(self.on_select_result_cb)

    def on_select_result_cb(self, result):
        self.view_manager.set_message_box('selected : {}'.format(result))

    ## RPS 
    def init_iotf(self):
        # Show
        self.view_manager.open_status_box()

        # Check for network availability
        self.view_manager.set_status_text('Waiting for network')
        if not util.wait_network():
            self.view_manager.set_status_text('Cannot connect WiFi')
            raise Exception('Cannot connect WiFi')
        
        sta_if = network.WLAN(network.STA_IF)
        mac_addr = ''.join('{:02X}'.format(c) for c in sta_if.config('mac'))

        orgId = iotfcfg.orgId
        deviceType = iotfcfg.deviceType
        deviceId = iotfcfg.deviceId if  hasattr(iotfcfg, 'deviceId') else mac_addr
        user = 'use-token-auth'
        authToken = iotfcfg.authToken

        clientID = 'd:' + orgId + ':' + deviceType + ':' + deviceId
        broker = orgId + '.messaging.internetofthings.ibmcloud.com'

        # Check for device registration
        url = 'https://hongjs-nodered.mybluemix.net/api/badge2018/register'
        deviceInfo = {
            'deviceId': deviceId,
            'authToken': authToken,
            'deviceInfo': {},
            'groups': [],
            'location': {},
            'metadata': {}
        }
        headers = {'token':'helloiot'}
        r = urequests.post(url, json=deviceInfo, headers=headers)
        if r.status_code == 201:
          print('OK')
        elif r.status_code == 409:
          print('Already Exists')
        else:
          print(r.text)
          raise Exception(r.text)
        r.close()

        self.deviceId = deviceId

        self.mqtt = simple.MQTTClient(clientID, broker, user=user, password=authToken, ssl=True)
        self.mqtt.set_callback(self.sub_cb)
        self.mqtt.connect()
        self.mqtt.subscribe(self.COMMAND_TOPIC_RPS)

        # Close Popup
        self.view_manager.close_status_box()

    def sub_cb(self, topic, msg):
        obj = json.loads(msg)
        print((topic, msg, obj))
        if topic == self.COMMAND_TOPIC_RPS:
            self.rps_cb(obj)

    #
    def check_network(self):
        self.view_manager.open_status_box()
        self.view_manager.set_status_text('Wait for network')
        if not util.wait_network():
            self.view_manager.set_status_text('Cannot connect WiFi')
            raise Exception('Cannot connect WiFi')
        self.view_manager.set_status_text('Listing RPS games')
        self.view_manager.close_status_box()

    # Events
    def list_games(self):
        self.view_manager.open_status_box()
        self.view_manager.set_status_text('Wait for list...')
        cmd = {'type':'games','value':{'username':self.username}}
        self.mqtt.publish(self.EVENT_TOPIC_RPS, json.dumps(cmd))

    def join_game(self, game):
        self.gid = game['id']
        self.gtitle = game['title']
        cmd = {'type':'join','value':{'gid':self.gid,'username':self.username}}
        self.mqtt.publish(self.EVENT_TOPIC_RPS, json.dumps(cmd))
    
    def submit_option(self, value):
        cmd = {'type':'submit','value':{'submit':value, 'gid':self.gid,'username':self.username}}
        self.mqtt.publish(self.EVENT_TOPIC_RPS, json.dumps(cmd))
    
    def leave_game(self):
        cmd = {'type':'leave','value':{'gid':self.gid,'username':self.username}}
        self.mqtt.publish(self.EVENT_TOPIC_RPS, json.dumps(cmd))

    # RPS Command Callback
    def rps_cb(self, obj):
        obj_d = obj['d']
        cmd_type = obj_d['type'] if 'type' in obj['d'] else 'system'
        cmd_value = obj_d['value']
        cmd_status = cmd_value['status'] if 'status' in cmd_value else 'ok'
        cmd_text = cmd_value['text'] if 'text' in cmd_value else None

        # show error
        if cmd_status == 'error':
            self.message_cb('[error]{}'.format(cmd_text))
            return
        
        # games
        if cmd_type == 'judge':
          if 'result' in cmd_value:
              result = cmd_value['result']
              self.message_popup_view.set_title('Result')
              self.message_popup_view.set_text(cmd_text)
              if result == 'won':
                self.message_popup_view.set_color(ugfx.WHITE, ugfx.BLUE)
              else:
                self.message_popup_view.set_color(ugfx.BLACK, ugfx.RED)
              self.view_manager.appear_view(self.message_popup_view)
              return
          else:
              self.message_popup_view.close()

        if cmd_text != None:
            self.message_cb('[{0}]{1}'.format(cmd_type, cmd_text))

        if cmd_type == 'games':
            self.game_list_view.update(cmd_value['games'])
            self.view_manager.close_status_box()
            self.view_manager.appear_view(self.game_list_view)
        elif cmd_type == 'join':
            self.action_menu_view.set_title(self.gtitle)
            self.view_manager.appear_view(self.action_menu_view)
        elif cmd_type == 'chat':
            # show chatting message
            print('{}'.format(cmd_value['text']))
        elif cmd_type == 'submit':
            # Submit
            print('{}'.format(cmd_value['text']))
        elif cmd_type == 'leave':
            print('{}'.format(cmd_value['text']))
            self.view_manager.appear_view(self.game_list_view)
        else:
            print('Unknown type ({})'.format(cmd_type))
            return
