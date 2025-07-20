def get_qss_styling(file : str = "main_window.qss"):
    path = "./resources/style/"
    with open(path + file) as f:
        return f.read()