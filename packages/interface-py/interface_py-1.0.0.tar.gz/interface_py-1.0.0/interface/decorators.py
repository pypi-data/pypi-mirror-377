
def interface(cls):
    cls._is_interface_ = True
    cls.__validate__()
    return cls


def concrete(cls):
    cls._is_interface_ = False
    cls.__validate__()
    return cls
