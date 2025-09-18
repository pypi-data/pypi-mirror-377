from .core import InterfaceMeta as _InterfaceMeta
from .decorators import interface, concrete


@interface
class InterfaceBase(metaclass=_InterfaceMeta):
    pass
