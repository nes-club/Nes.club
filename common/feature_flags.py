def feature_switch(feature_flag, yes, no):
    def result(*args, **kwargs):
        if feature_flag:
            return yes(*args, **kwargs)
        else:
            return no(*args, **kwargs)
    return result


def noop(func):
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper
