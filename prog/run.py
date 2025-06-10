from gui import *


if __name__ == "__main__":
    params = None
    while True:
        app = WindowParams(params)
        app.run()
        if app.get_continue_state():
            params = app.get_result()
            exp = WindowExperiment(params)
            exp.run()
            if not exp.get_continue_state():
                break
        else:
            break
