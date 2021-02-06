# global toggle for debugging logs
DEBUG = True


def log(s):
    """Used to print debugging statements if DEBUG in main is set to True.

    :param s: Statement to be printed to standard output.
    """
    if DEBUG:
        print(s)
