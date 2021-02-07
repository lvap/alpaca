# global toggle for debugging logs
DEBUG = True


def log(s, enabled=True):
    if DEBUG and enabled:
        print(s)
