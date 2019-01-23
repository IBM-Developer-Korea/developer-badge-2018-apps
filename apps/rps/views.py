import ujson as json
import ugfx

from home import styles

class RPSCommonView():
    
    default_font = 'NanumSquareRound_Regular16'

    def __init__(self, width=ugfx.width(), height=ugfx.height()):
        # Default font
        ugfx.set_default_font(self.default_font)

        # Container
        self.container = ugfx.Container(0, 0, width, height, style=styles.ibm_st)
        
        # Title Label
        self.title_label = ugfx.Label(5, 5, 310, 40, text='', parent=self.container)

    def set_title(self, text=''):
        self.title_label.text(text)
    
    def show(self):
        self.container.show()

    def hide(self):
        self.container.hide()

    def destroy(self):
        self.container.destroy()
        self.title_label.destroy()

class RPSChildView(RPSCommonView):

    def __init__(self, manager, show=False, full_size=False):
        # Set view manager
        self.manager = manager

        # Attach
        self.manager.attach_view_cb(self)

        # On select item callback
        self.init_select_item_cb()
        
        # Container
        if full_size:
            width = self.manager.container.width()
            height = self.manager.container.height()
        else:
            width = self.manager.container.width()
            height = self.manager.container.height() - 88

        super().__init__(width, height)
        if show:
            self.show()

    def on_key_pressed(self, key):
        print('pressed: {}'.format(key))

    def on_key_released(self, key):
        print('released: {}'.format(key))

    def init_select_item_cb(self):
        self.on_select_item_cb = lambda result: print(result)

    def set_select_result_cb(self, cb):
        if not callable(cb):
            raise Exception('It is NOT callable!')
        self.on_select_item_cb = cb

    def destroy(self):
        super().destroy()

class GameListView(RPSChildView):

    # Entry
    def __init__(self, manager):
        super().__init__(manager)
        self.set_title('Select Game')
        self.game_list = ugfx.List(10, 40, self.container.width() - 20, self.container.height() - 40, up=ugfx.JOY_UP, down=ugfx.JOY_DOWN, parent=self.container)
    
    def update(self, games):
        self.games = games
        for _ in range(self.game_list.count()):
            self.game_list.remove_item(0)
        
        self.game_list.add_item('### EXIT ###')
        self.game_list.add_item('### TEST ###')
        for game in games:
            self.game_list.add_item(game['title'])

    def on_key_released(self, key):
        if key == ugfx.BTN_A:
            idx = self.game_list.selected_index()
            if idx == 0: # Exit
                self.manager.parent.exit()
                return
            elif idx == 1: # Test
                self.manager.parent.test()
                return
            
            # Select Game
            game = self.games[idx - 2]
            print('selected gid: {}'.format(game['id']))
            self.manager.parent.join_game(game)
        elif key == ugfx.BTN_B:
            # Refresh
            self.manager.parent.list_games()

    def destroy(self):
        self.game_list.destroy()
        super().destroy()

class ActionMenuView(RPSChildView):

    # Entry
    def __init__(self, manager):
        super().__init__(manager)
        self.set_title('Select Action')
        self.action_list = ugfx.List(10, 40, self.container.width() - 20, self.container.height() - 40, up=ugfx.JOY_UP, down=ugfx.JOY_DOWN, parent=self.container)
        self.actions = ['Rock', 'Paper', 'Scissors', 'Leave']
        for action in self.actions:
            self.action_list.add_item(action)

    def on_key_released(self, key):
        if key == ugfx.BTN_A:
            idx = self.action_list.selected_index()
            print('selected action: {}'.format(self.actions[idx]))
            # Leave Game
            if idx == 3:
                self.manager.parent.leave_game()
                return
            
            value = ['rock', 'paper', 'scissors']
            self.manager.parent.submit_option(value[idx])

    def destroy(self):
        self.action_list.destroy()
        super().destroy()

class MessagePopupView(RPSChildView):

    # Entry
    def __init__(self, manager, fg_color=ugfx.GREY, bg_color=ugfx.IBMCoolGrey10):
        super().__init__(manager, full_size=True)

        # 
        self.fg_color = fg_color
        self.bg_color = bg_color

        popup_st = ugfx.Style()

        # Ref. to styles.ibm_st
        popup_st.set_background(ugfx.WHITE)
        popup_st.set_focus(ugfx.WHITE)
        popup_st.set_pressed([
            ugfx.BLACK, # Text
            ugfx.IBMCyan10, # Edge
            ugfx.BLACK, # Fill
            ugfx.BLACK, # Progress
        ])
        popup_st.set_enabled([
            ugfx.BLACK,
            ugfx.IBMCyan10,
            ugfx.IBMTeal30,
            ugfx.BLACK,
        ])
        popup_st.set_disabled([
            self.fg_color,
            ugfx.IBMCyan10,
            self.bg_color,
            ugfx.BLACK,
        ])

        self.popup_st = popup_st

        self.set_title('Message Popup')

        self.message_box = None
        self.text = ''
        self.create_textbox()
        #self.message_box.visible(0) #hide
    
    def create_textbox(self):
        y = 40
        if self.message_box != None:
            self.message_box.destroy()
        self.message_box = ugfx.Textbox(10, y,
            self.container.width() - 20, self.container.height() - y - 20,
            parent=self.container, style=self.popup_st)
        self.message_box.enabled(False)
        self.message_box.text(self.text)

    def set_text(self, text=''):
        self.text = text
        self.message_box.text(self.text)

    def set_color(self, fg_color=ugfx.GREY, bg_color=ugfx.IBMCoolGrey10):
        self.fg_color = fg_color
        self.bg_color = bg_color
        self.popup_st.set_disabled([
            self.fg_color,
            ugfx.IBMCyan10,
            self.bg_color,
            ugfx.BLACK,
        ])
        self.create_textbox()

    def set_fgcolor(self, fg_color=ugfx.GREY):
        self.fg_color = fg_color
        self.popup_st.set_disabled([
            self.fg_color,
            ugfx.IBMCyan10,
            self.bg_color,
            ugfx.BLACK,
        ])
        self.create_textbox()

    def set_bgcolor(self, bg_color=ugfx.IBMCoolGrey10):
        self.bg_color = bg_color
        self.popup_st.set_disabled([
            self.fg_color,
            ugfx.IBMCyan10,
            self.bg_color,
            ugfx.BLACK,
        ])
        self.create_textbox()

    def on_key_released(self, key):
        if key == ugfx.BTN_A:
            # OK
            self.on_select_item_cb(True)

        if key == ugfx.BTN_B:
            # Cancel
            self.on_select_item_cb(False)

        # Close
        self.close()
    
    def close(self):
        self.init_select_item_cb()
        self.manager.close_view(self)

    def destroy(self):
        self.message_box.destroy()
        super().destroy()