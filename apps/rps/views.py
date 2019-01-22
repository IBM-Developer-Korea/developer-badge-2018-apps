import ujson as json
import ugfx

from home import styles

class CommonView():
    
    default_font = 'NanumSquareRound_Regular16'

    def __init__(self, parent, show=False, full_size=False):
        self.parent = parent

        # Attach View
        self.parent.attach_view_cb(self)
        
        #ugfx.input_init()
        ugfx.set_default_font(self.default_font)

        # create_container
        if full_size:
            width = self.parent.container.width()
            height = self.parent.container.height()
        else:
            width = self.parent.container.width()
            height = self.parent.container.height() - 88

        self.container = ugfx.Container(0, 0, width, height, style=styles.ibm_st)
        if show:
            self.container.show()
        
        # Title Label
        self.title_label = ugfx.Label(5, 5, 310, 40, text='', parent=self.container)

    def title(self, text=''):
        self.title_label.text(text)
    
    def show(self):
        self.container.show()

    def hide(self):
        self.container.hide()

    def close(self):
        if self.parent.previous_view != None:
            self.parent.appear_view(self.parent.previous_view)
        self.parent.previous_view = None
    
    def select_button_cb(self, key=None):
        print('on selected')

class GameListView(CommonView):

    # Entry
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Select Game')
        self.game_list = ugfx.List(10, 40, self.container.width() - 20, self.container.height() - 40, up=ugfx.JOY_UP, down=ugfx.JOY_DOWN, parent=self.container)
    
    def update(self, games):
        self.games = games
        for _ in range(self.game_list.count()):
            self.game_list.remove_item(0)
        
        self.game_list.add_item('>TEST<')
        for game in games:
            self.game_list.add_item(game['title'])

    def select_button_cb(self, key):
        if key == ugfx.BTN_A:
            idx = self.game_list.selected_index()
            # Testing
            if idx == 0:
                self.parent.test()
                return

            # Select Game
            game_id = self.games[idx]['id']
            print('selected gid: {}'.format(game_id))
            self.parent.join_game(game_id)
        elif key == ugfx.BTN_B:
            # Refresh
            self.parent.list_games()

class ActionMenuView(CommonView):

    # Entry
    def __init__(self, parent):
        super().__init__(parent)
        self.title('Select Action')
        self.action_list = ugfx.List(10, 40, self.container.width() - 20, self.container.height() - 40, up=ugfx.JOY_UP, down=ugfx.JOY_DOWN, parent=self.container)
        self.actions = ['Rock', 'Paper', 'Scissors', 'Leave']
        for action in self.actions:
            self.action_list.add_item(action)

    def select_button_cb(self, key):
        if key == ugfx.BTN_A:
            idx = self.action_list.selected_index()
            print('selected action: {}'.format(self.actions[idx]))
            # Leave Game
            if idx == 3:
                self.parent.leave_game()
                return
            
            value = ['rock', 'paper', 'scissors']
            self.parent.submit_option(value[idx])

class MessagePopupView(CommonView):

    # Entry
    def __init__(self, parent, fg_color=ugfx.GREY, bg_color=ugfx.IBMCoolGrey10):
        super().__init__(parent, full_size=True)

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

        self.title('Message Popup')

        self.message_box = None
        self.text = ''
        self.create_textbox()
        #self.message_box.visible(0) #hide
    
    def answer_cb(self, result):
        print(result)

    def set_answer_cb(self, cb):
        if not callable(cb):
            raise Exception("Answer callback is not callable!!")
        self.answer_cb = cb

    def create_textbox(self):
        y = 40
        if self.message_box != None:
            self.message_box.destroy()
        self.message_box = ugfx.Textbox(10, y,
            self.container.width() - 20, self.container.height() - y - 20,
            parent=self.container, style=self.popup_st)
        self.message_box.enabled(False)
        self.message_box.text(self.text)

    def set_title(self, title):
        self.title(title)

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

    def select_button_cb(self, key):
        if key == ugfx.BTN_A:
            # OK
            self.answer_cb(True)

        if key == ugfx.BTN_B:
            # Cancel
            self.answer_cb(False)

        # Close
        self.close()
        