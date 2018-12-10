import ujson as json
import uos

import ugfx

from home import styles
import util


class Button:
    def __init__(self, grp, text, callback):
        self.btn = ugfx.Button(grp.x, grp.y, grp.w, grp.h,
            text, parent=grp.parent)
        self.callback = callback

    def defocus(self):
        self.btn.detach_input(0)

    def focus(self, toggle=ugfx.BTN_A):
        self.btn.attach_input(toggle, 0)
        self.btn.set_focus()


class ButtonGroup:
    def __init__(self, parent, x, y, w, h, gap):
        self.parent = parent
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.gap = gap
        self.btns = []
        self.index = 0
        self.current = None

    def add(self, text, callback, data=None):
        btn = Button(self, text, callback)
        btn.data = data
        self.btns.append(btn)
        if self.current:
            self.current.next_btn = btn
            btn.prev_btn = self.current
        self.current = btn
        self.y += self.h + self.gap

    def end(self):
        if self.btns:
            self.btns[0].prev_btn = self.current
            self.current.next_btn = self.btns[0]
            self.next(True)
            self.attach_input()

    def attach_input(self):
        ugfx.input_attach(ugfx.JOY_DOWN, self.next)
        ugfx.input_attach(ugfx.JOY_UP, self.prev)
        ugfx.input_attach(ugfx.BTN_A, self.select)

    def detach_input(self):
        ugfx.input_attach(ugfx.JOY_DOWN, None)
        ugfx.input_attach(ugfx.JOY_UP, None)
        ugfx.input_attach(ugfx.BTN_A, None)

    def prev(self, pressed):
        if pressed:
            self.current.defocus()
            self.current = self.current.prev_btn
            self.current.focus()

    def next(self, pressed):
        if pressed:
            self.current.defocus()
            self.current = self.current.next_btn
            self.current.focus()

    def select(self, pressed=True):
        if not pressed:
            self.current.callback(self.current.data)

    def destroy(self, pressed=True):
        if pressed:
            self.detach_input()
            for button in self.btns:
                button.btn.destroy()

class Display:

    menus = ['Apps', 'Config', 'Status']

    def __init__(self):
        self.window = None
        self.widgets = []

        ugfx.input_init()
        ugfx.set_default_font('IBMPlexMono_Bold24')
        self.main()

    def destroy(self, pressed=True):
        if pressed and self.window and self.window.enabled():
            while self.widgets:
                self.widgets.pop().destroy()
            self.window.destroy()

    def create_window(self):
        ugfx.clear(ugfx.BLACK)
        self.window = ugfx.Container(0, 0, ugfx.width(), ugfx.height(), style=styles.ibm_st)
        w = self.window
        w.show()
        w.area(0, 0, w.width(), w.height(), ugfx.HTML2COLOR(0x3c3c3b))

    def main(self):
        self.create_window()
        self.window.text(10, 20, 'IBM', ugfx.WHITE)
        self.window.text(60, 20, 'Developer Day 2018', ugfx.HTML2COLOR(0x01d7dd))
        self.btngroup = ButtonGroup(self.window, 80, 60, 140, 40, 10)
        self.widgets.append(self.btngroup)

        for menu in self.menus:
            self.btngroup.add(menu, getattr(self, menu))
        self.btngroup.end()

    def run_app(self, app):
        util.run(app)

    def Apps(self, data=None):
        self.destroy()
        self.create_window()
        self.btngroup = ButtonGroup(self.window, 40, 30, 240, 40, 10)
        self.widgets.append(self.btngroup)
        for app in uos.listdir('/apps'):
            try:
                with open('/apps/{}/app.json'.format(app)) as fp:
                    data = json.load(fp)
            except Exception as e:
                print(e)
                continue
            if 'name' in data:
                self.btngroup.add(data['name'], self.run_app, data=app)
        self.btngroup.end()

    def Config(self, data=None):
        self.destroy()

    def Status(self, data=None):
        self.destroy()
