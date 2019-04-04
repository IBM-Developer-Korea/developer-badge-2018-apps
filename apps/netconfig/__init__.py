import ugfx

def main():
    from netconfig import manager

    global app

    ugfx.init()
    app = manager.Status()
    app.main()
