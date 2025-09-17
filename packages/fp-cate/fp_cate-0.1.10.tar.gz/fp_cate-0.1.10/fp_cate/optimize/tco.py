__all__ = ["TailCall", "tco"]


class TailCall:
    def __init__(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs


def tco(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        while isinstance(result, TailCall):
            result = func(*result.args, **result.kwargs)
        return result

    return wrapper
