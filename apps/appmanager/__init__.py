def main():
    from appmanager import manager
    dir(manager)

    global app

    app = manager.AppList()
    app.main()
