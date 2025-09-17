def debug(func):
    def debug_wrapper(*args, **kwargs):
        args_repr = [repr(a) for a in args]
        kwargs_repr = ["{}={}".format(k, repr(v)) for k, v in kwargs.items()]
        signature = ", ".join(args_repr + kwargs_repr)
        print("Calling {}({})".format(func.__name__, signature))
        value = func(*args, **kwargs)
        print("{} returned {}".format(repr(func.__name__), value))
        return value
    return debug_wrapper
