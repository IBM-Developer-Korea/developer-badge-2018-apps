def main():
    from netconfig import manager

    global app

    app = manager.Status()
    app.main()
