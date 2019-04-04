import ugfx

def main():
    from appmanager import manager
    dir(manager)

    global app

    ugfx.init()
    app = manager.AppList()
    app.main()
