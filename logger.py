# global toggle for debugging logs
DEBUG = True


def log(message, enabled=True):
    if DEBUG and enabled:
        print(message)
