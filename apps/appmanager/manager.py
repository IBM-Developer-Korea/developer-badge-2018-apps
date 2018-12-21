import ujson as json
import ugfx

from home.launcher import Display, ButtonGroup
from home import ota
import util


class AppList(Display):

    BASE_URL = 'https://badge.arcy.me/apps'
    LIST_URL = '{}/list.json'.format(BASE_URL)

    def title(self):
        ugfx.Label(5, 5, 310, 40, text='App Manager', parent=self.window)

    def main(self):
        self.create_window()
        w = self.window
        self.title()
        self.list_apps()

        self.desc = ugfx.Textbox(160, 105, 155, w.height() - 115, parent=w)
        self.widgets.append(self.desc)
        self.version = ugfx.Label(160, 50, 155, 25, text='', parent=w)
        self.widgets.append(self.version)
        self.btngroup = ButtonGroup(self.window, 160, 75, 75, 25, 5, False)
        self.btngroup.add('Install', self.install_app)
        self.btngroup.add('Delete', self.delete_app)
        self.btngroup.end()
        self.widgets.append(self.btngroup)
        self.update_desc()

        self.input_attach()

    def input_attach(self):
        ugfx.input_attach(ugfx.JOY_DOWN, self.update_desc)
        ugfx.input_attach(ugfx.JOY_UP, self.update_desc)

    def update_desc(self, pressed=True):
        if not pressed:
            return
        app = self.apps[self.app_list.selected_index()]
        self.current_app = app
        self.btngroup.btns[0].btn.text('Upgrade' if app['upgrade'] else 'Install')
        self.btngroup.btns[0].btn.visible(not app['installed'] or app['upgrade'])
        self.btngroup.btns[1].btn.visible(app['installed'])
        if 'desc' in app:
            self.desc.text(app['desc'])
        else:
            self.desc.text('')
        self.version.text(app['ver_string'])

    def install_app(self, data=None):
        self.clear()
        self.create_status_box()
        slug = self.current_app['slug']
        self.set_status('Installing {}..'.format(slug))
        ota.install_url('{}/{}.tar.gz'.format(self.BASE_URL, slug),
            '/apps/{}/'.format(slug))
        self.set_status('{} installed'.format(slug))
        self.reload()

    def delete_app(self, data=None):
        print('delete')

    def reload(self):
        self.destroy()
        self.main()

    def list_apps(self):
        self.create_status_box()
        self.set_status('Waiting for network')
        if not util.wait_network():
            self.set_status('Cannot connect WiFi')
            raise Exception('Cannot connect WiFi')
        self.set_status('Downloading app list')
        apps = ota.download_json(self.LIST_URL)
        self.close_status_box()
        w = self.window
        ugfx.set_default_font('IBMPlexSans_Regular18')
        self.app_list = ugfx.List(5, 50, 150, w.height() - 60, parent = w)
        self.app_list.visible(False)
        self.apps = []
        for slug, app in apps.items():
            app['installed'] = False
            app['slug'] = slug
            app['upgrade'] = False
            app['ver_string'] = '{}'.format(app['version'])
            try:
                with open('/apps/{}/app.json'.format(slug)) as fp:
                    data = json.load(fp)
                app['installed'] = data['version']
                if app['version'] != app['installed']:
                    app['upgrade'] = True
                    app['ver_string'] = '{} -> {}'.format(
                        app['installed'], app['version'])
            except Exception as e:
                print(e)
            self.apps.append(app)
            self.app_list.add_item(app['name'] if 'name' in app else slug)
        self.app_list.visible(True)

        #ugfx.input_attach(ugfx.BTN_A, self.network_selected)
        ugfx.input_attach(ugfx.BTN_B, util.reboot)
        self.widgets.append(self.app_list)
