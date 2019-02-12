import sys
import os


def td2seconds(td):
    """
    Converts a timedelta to seconds. This is equivlanet in python >= 2.7 to
    td.total_seconds(). Thus this method is only used for backward compatibility
    with python 2.6
    :param td: timedelta to convert into seconds.
    :return: number of seconds corresponding to the input timedelta
    """
    if isPython26():
        return (td.microseconds + (td.seconds + td.days * 24 * 3600) * 10**6) / 10**6
    else:
        return td.total_seconds()


def prettyPrintSeconds(seconds):
    negative = False
    if seconds < 0:
        seconds *= -1
        negative = True
    m, s = divmod(seconds, 60)
    h, m = divmod(m, 60)
    if negative:
        return "-%d:%02d:%02d" % (h, m, s)
    else:
        return "%d:%02d:%02d" % (h, m, s)


def isPython26():
    if sys.version_info[0:2] <= (2, 6):
        return True
    else:
        return False


def isPython27():
    if sys.version_info[0:2] == (2, 7):
        return True
    else:
        return False


def isPython3():
    if sys.version_info[0:2] >= (3, 0):
        return True
    else:
        return False
