import ugfx

def main():
    from home import launcher

    global app

    ugfx.init()
    app = launcher.Display()
    app.main()
