import inspect

from .helper_functions import Helper


class InterfaceMeta(type):
    
    def __new__(mcls, name, bases, namespace):
        cls = super().__new__(mcls, name, bases, namespace)
        cls._is_interface_ = getattr(cls, "_is_interface_", None)
        cls._interface_contracts_ = set()
        return cls
    
    
    def __call__(cls, *args, **kwargs):
        if getattr(cls, "_is_interface_", False):
            raise TypeError(f"Cannot instantiate interface class '{cls.__name__}'")
        return super().__call__(*args, **kwargs)
    

    def __validate__(cls):
        if cls._is_interface_ is None:
            del cls
            raise TypeError(
                f"Class must be decorated with @interface or @concrete"
            )

        if cls._is_interface_:
            # enforce interface
            for attr, value in list(vars(cls).items()):
                if attr.startswith("__") and attr.endswith("__"):
                    continue
                if attr in ("__annotations__", "_is_interface_", "_interface_contracts_"):
                    continue

                if inspect.isfunction(value):
                    if not Helper.is_empty_function(value):
                        cls_name = cls.__name__
                        del cls
                        raise TypeError(
                            f"Method '{attr}' in interface '{cls_name}' must have empty body."
                        )
                    cls._interface_contracts_.add(attr)
                    continue

                if isinstance(value, staticmethod):
                    if not Helper.is_empty_function(value.__func__):
                        cls_name = cls.__name__
                        del cls
                        raise TypeError(
                            f"Static method '{attr}' in interface '{cls_name}' must have empty body."
                        )
                    cls._interface_contracts_.add(attr)
                    continue

                if isinstance(value, classmethod):
                    if not Helper.is_empty_function(value.__func__):
                        cls_name = cls.__name__
                        del cls
                        raise TypeError(
                            f"Class method '{attr}' in interface '{cls_name}' must have empty body."
                        )
                    cls._interface_contracts_.add(attr)
                    continue

                if isinstance(value, property):
                    if value.fget and not Helper.is_empty_function(value.fget):
                        cls_name = cls.__name__
                        del cls
                        raise TypeError(
                            f"Property getter '{attr}' in interface '{cls_name}' must have empty body."
                        )
                    if value.fset and not Helper.is_empty_function(value.fset):
                        cls_name = cls.__name__
                        del cls
                        raise TypeError(
                            f"Property setter '{attr}' in interface '{cls_name}' must have empty body."
                        )
                    cls._interface_contracts_.add(attr)
                    continue
                
                cls_name = cls.__name__
                del cls
                raise TypeError(
                    f"Attribute '{attr}' in interface '{cls_name}' should not have a value."
                )


            # inherit contracts from parents
            for base in cls.__mro__[1:]:
                if hasattr(base, "_interface_contracts_"):
                    cls._interface_contracts_ |= base._interface_contracts_

        else:
            # enforce concrete
            contracts = set()
            for base in cls.__mro__[1:]:
                if hasattr(base, "_interface_contracts_"):
                    contracts |= base._interface_contracts_

            missing = []
            for contract in contracts:
                impl = getattr(cls, contract, None)
                if impl is None or Helper.is_empty_function(impl):
                    missing.append(contract)

            if missing:
                cls_name = cls.__name__
                del cls
                raise TypeError(
                    f"Concrete class '{cls_name}' must implement contracts: {', '.join(missing)}"
                )
