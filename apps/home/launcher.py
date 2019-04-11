import ujson as json
import uos

import ugfx

from home import styles
from home import ota
import util


class Button:
    def __init__(self, page, text, callback, data):
        self.btn = ugfx.Button(page.x, page.y, page.group.w, page.group.h,
            text, shape=ugfx.Button.ROUNDED, parent=page.group.parent)
        self.btn.enabled(False)
        self.btn.visible(False)
        self.callback = callback
        self.data = data

    def defocus(self):
        #self.btn.detach_input(0)
        self.btn.enabled(False)

    def focus(self, toggle=ugfx.BTN_A):
        #self.btn.attach_input(toggle, 0)
        self.btn.set_focus()
        self.btn.enabled(True)

    def call(self):
        self.callback(self.data)

class ButtonGroup:
    def __init__(self, parent, x, y, w, h, gap, vertical=True, per_page=4):
        self.parent = parent
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.gap = gap
        self.pages = []
        self.btns = []
        self.index = 0
        self.current = None
        self.vertical = vertical
        self.per_page = per_page
        self.current_page = ButtonPage(self, None)
        if vertical:
            self.prev_key = ugfx.JOY_UP
            self.next_key = ugfx.JOY_DOWN
            self.prev_page_key = ugfx.JOY_LEFT
            self.next_page_key = ugfx.JOY_RIGHT
        else:
            self.prev_key = ugfx.JOY_LEFT
            self.next_key = ugfx.JOY_RIGHT
            self.prev_page_key = ugfx.JOY_UP
            self.next_page_key = ugfx.JOY_DOWN

    def add(self, text, callback, data=None):
        self.current_page = self.current_page.add_button(text, callback, data)

    def end(self):
        if self.pages:
            self.pages[0].prev_page = self.current_page
            self.current_page.next_page = self.pages[0]
            self.current_page.end()
            self.next_page(True)
            self.attach_input()

    def attach_input(self):
        ugfx.input_attach(self.next_key, self.next)
        ugfx.input_attach(self.prev_key, self.prev)
        if len(self.pages) > 1:
            ugfx.input_attach(self.next_page_key, self.next_page)
            ugfx.input_attach(self.prev_page_key, self.prev_page)
        ugfx.input_attach(ugfx.BTN_A, self.select)

    def detach_input(self):
        ugfx.input_attach(self.next_key, None)
        ugfx.input_attach(self.prev_key, None)
        ugfx.input_attach(self.next_page_key, None)
        ugfx.input_attach(self.prev_page_key, None)
        ugfx.input_attach(ugfx.BTN_A, None)

    def prev(self, pressed):
        self.current_page.prev(pressed)

    def next(self, pressed):
        self.current_page.next(pressed)

    def prev_page(self, pressed):
        return self.next_page(pressed, False)

    def next_page(self, pressed, is_next=True):
        if pressed:
            self.current_page.visible(False)
            if is_next:
                self.current_page = self.current_page.next_page
            else:
                self.current_page = self.current_page.prev_page
            self.current_page.visible(True)

    def select(self, pressed=True):
        if not pressed:
            self.current_page.current.call()

    def destroy(self, pressed=True):
        self.detach_input()
        if pressed:
            while self.pages:
                self.pages.pop().destroy()


class ButtonPage:
    def __init__(self, group, prev_page):
        self.group = group
        self.x, self.y = group.x, group.y
        group.pages.append(self)
        self.id = len(group.pages)
        if prev_page:
            self.prev_page = prev_page
            prev_page.next_page = self
            # Hide previous page
            prev_page.visible(False)
        self.btns = []
        self.current = None

    def add_button(self, text, callback, data):
        if len(self.btns) >= self.group.per_page:
            self.end()
            new_page = ButtonPage(self.group, self)
            new_page.add_button(text, callback, data)
            return new_page
        btn = Button(self, text, callback, data)
        self.btns.append(btn)
        self.group.btns.append(btn)
        if self.current:
            self.current.next_btn = btn
            btn.prev_btn = self.current
        self.current = btn
        if self.group.vertical:
            self.y += self.group.h + self.group.gap
        else:
            self.x += self.group.w + self.group.gap
        return self

    def visible(self, value):
        for button in self.btns:
            button.btn.visible(value)

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

    def end(self):
        if self.btns:
            self.btns[0].prev_btn = self.current
            self.current.next_btn = self.btns[0]
            self.next(True)

    def destroy(self, pressed=True):
        if pressed:
            while self.btns:
                self.btns.pop().btn.destroy()


class Display:

    menus = ['Apps', 'Status']
    default_font = 'IBMPlexMono_Bold24'

    def __init__(self):
        self.window = None
        self.widgets = []

        ugfx.input_init()
        ugfx.set_default_font(self.default_font)
        ugfx.input_attach(ugfx.BTN_B, self.reload)

    def clear(self):
        while self.widgets:
            self.widgets.pop().destroy()

    def destroy(self, pressed=True):
        if pressed and self.window and self.window.enabled():
            self.clear()
            self.window.destroy()
            self.window = None

    def create_window(self, show=True):
        ugfx.clear(ugfx.BLACK)
        self.window = ugfx.Container(0, 0, ugfx.width(), ugfx.height(), style=styles.ibm_st)
        if show:
            self.window.show()
        return self.window

    def reload(self, pressed=True):
        if not pressed:
            self.destroy()
            self.main()

    def title(self):
        ugfx.Label(5, 5, 310, 40, text='IBM Developer Day 2018', parent=self.window)

    def main(self):
        self.create_window(show=False)
        self.title()
        self.btngroup = ButtonGroup(self.window, 80, 60, 140, 40, 10)
        self.widgets.append(self.btngroup)

        for menu in self.menus:
            self.btngroup.add(menu, getattr(self, menu))
        self.btngroup.end()
        self.window.show()

    def run_app(self, app):
        util.run(app)

    def Apps(self, data=None):
        self.destroy()
        self.create_window(show=False)
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
        self.window.show()

    def Config(self, data=None):
        self.destroy()

    def create_status_box(self, y=40):
        self.status_box = ugfx.Textbox(10, y,
                self.window.width() - 20, self.window.height() - y - 20,
                parent=self.window)
        self.status_box.enabled(False)

    def set_status(self, text):
        print(text)
        if self.status_box and self.status_box.visible():
            self.status_box.text(text)

    def close_status_box(self):
        self.status_box.destroy()

    def __close_status_box(self, pressed=True):
        if not pressed:
            self.status_box.destroy()

    def install_ota(self, data):
        self.destroy()
        print('On the air update..')
        self.create_window()
        ugfx.Label(80, 60, 160, 120, text='Upgrading..\nto {}'.format(data['version']),
            parent=self.window)
        print(data)
        ota.install_url(data['ota_url'], '/')

    def Status(self, data=None):
        self.destroy()
        self.create_window()
        w = self.window
        y = 10
        gap = 5
        height = 35
        ugfx.Label(10, y, w.width() - 20, height, 'Platform: {}'.format(util.get_version()), parent=w)
        y += gap + height
        ugfx.Label(10, y, w.width() - 20, height, 'Release: {}'.format(uos.uname()[2]), parent=w)
        y += gap + height
        ugfx.Label(10, y, w.width() - 20, height, 'firmware:', parent=w)
        ugfx.set_default_font('IBMPlexMono_Bold18')
        y += height
        ugfx.Label(10, y, w.width() - 20, height + 10, '{}'.format(uos.uname()[3]), parent=w)
        ugfx.set_default_font(self.default_font)
        ugfx.set_default_font('IBMPlexSans_Regular18')
        self.create_status_box()
        ugfx.set_default_font(self.default_font)
        ugfx.input_attach(ugfx.BTN_A, self.__close_status_box)
        try:
            ota_data = ota.check_version()
        except ota.OtaException as e:
            self.set_status('Error: {}'.format(e))
        else:
            if ota_data:
                self.status_box.destroy()
                ugfx.Label(10, 180, 200, 40, text='New: {}'.format(ota_data['version']),
                    parent=w)
                self.btngroup = ButtonGroup(self.window, 190, 180, 110, 40, 10)
                self.btngroup.add('Upgrade', self.install_ota, ota_data)
                self.btngroup.end()
            else:
                self.set_status('Up to date')
