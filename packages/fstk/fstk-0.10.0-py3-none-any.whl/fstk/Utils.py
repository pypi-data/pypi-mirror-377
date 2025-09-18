import re

try:
    import importlib.resources as pkg_resources
except ImportError:
    import importlib_resources as pkg_resources

from . import assets

ASSETS_PATHS_CACHE = {}

def get_local_file_path(filename):
    if filename not in ASSETS_PATHS_CACHE:
        with pkg_resources.path(assets, filename) as f:
            ASSETS_PATHS_CACHE[filename] = str(f)

    return ASSETS_PATHS_CACHE[filename]

def format_time(seconds):
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 3600) % 60

    return '{:02d}:{:02d}:{:02d}'.format(hours, minutes, seconds)

# VALIDATORS

def integer_number_validator(text):
    """

    :param text:
    :return: Success, Error message
    """
    n = text.strip('# ')

    if n == '':
        return True, None

    try:
        n = int(n)
        if 0 < n < 1000000:
            return True, None
        else:
            return False, 'The number must be between 1 and 1000000'
    except ValueError:
        return False, 'The number is invalid. It must be an integer'

def not_empty_validator(text):
    """

    :param text:
    :return: Success, Error message
    """
    if text.strip() == '':
        return False, 'The text cannot be empty'
    else:
        return True, None

def time_validator(text):
    """

    :param text:
    :return: Success, Error message
    """
    t = text.replace(' ', '')
    err = 'The time format is invalid (eg. 1h 20m 30s or 01:20)'

    if 'h' in t or 'm' in t or 's' in t:
        # match all aoccurrences with the regex ^(?:(\d+)[hms])+$
        matches = re.findall(r'(\d+[hms])+', t)
        if not matches:
            return False, err

    elif ':' in t:
        parts = t.split(':')
        if len(parts) > 2:
            return False, err

        try:
            parts = [int(p) for p in parts]
        except ValueError:
            return False, err

    else:
        return False, err

    return True, None

THREADS_KEEPALIVE = []

def launch_thread(thread_class, params, signals_handlers):
    if params is None:
        params = []

    th = thread_class(*params)
    for signal, handler in signals_handlers:
        getattr(th, signal).connect(handler)

    th.finished.connect(th.deleteLater)
    th.finished.connect(lambda: THREADS_KEEPALIVE.remove(th))
    th.start()
    THREADS_KEEPALIVE.append(th)


def set_prop_and_refresh(widget, prop, value):
    widget.setProperty(prop, value)
    widget.setStyle(widget.style())


def is_property_different(d1, d2, property):
    # scorro i dizionari
    for key in property:
        d1 = d1[key]
        d2 = d2[key]

    return d1 != d2
