import time
from functools import wraps
from dateutil import parser
from operator import itemgetter


def sort_list_of_dict_by_key(list_to_be_sorted, key):
    soreted = sorted(list_to_be_sorted, key=itemgetter(key), reverse=True)
    return soreted


def parse_string_date(list_of_dict, key, key2):
    defualt_date = "1999-08-21 13:13:32"
    new_list = []
    for dict_row in list_of_dict:
        new_dict = {}
        parsed_key1 = dict_row.get(key, defualt_date)
        parsed_key2 = dict_row.get(key2, defualt_date)
        dict_row[key] = parser.parse(parsed_key1).strftime("%Y-%m-%d %H:%M:%S") if parsed_key1 else defualt_date
        dict_row[key2] = parser.parse(parsed_key2).strftime("%Y-%m-%d %H:%M:%S") if parsed_key2 else defualt_date
        new_dict.update(dict_row)
        new_list.append(new_dict)

    return new_list


def retry(ExceptionToCheck, tries=4, delay=3, backoff=2, logger=None):
    """Retry calling the decorated function using an exponential backoff.

    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    original from: http://wiki.python.org/moin/PythonDecoratorLibrary#Retry

    :param ExceptionToCheck: the exception to check. may be a tuple of
        exceptions to check
    :type ExceptionToCheck: Exception or tuple
    :param tries: number of times to try (not retry) before giving up
    :type tries: int
    :param delay: initial delay between retries in seconds
    :type delay: int
    :param backoff: backoff multiplier e.g. value of 2 will double the delay
        each retry
    :type backoff: int
    :param logger: logger to use. If None, print
    :type logger: logging.Logger instance
    """

    def deco_retry(f):

        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    msg = "%s, Retrying in %d seconds..." % (str(e), mdelay)
                    if logger:
                        logger.warning(msg)
                    else:
                        print(msg)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            return f(*args, **kwargs)

        return f_retry  # true decorator

    return deco_retry
