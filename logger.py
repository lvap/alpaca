# global toggle for debugging logs
DEBUG = True


# TODO maybe rewrite this to use python logging module https://docs.python.org/3/library/logging.html
def log(message, enabled: bool = True):
    if DEBUG and enabled:
        print(message)
