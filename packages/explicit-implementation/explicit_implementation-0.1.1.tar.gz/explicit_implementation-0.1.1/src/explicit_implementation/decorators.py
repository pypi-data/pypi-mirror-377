from typing import Any, Callable, Concatenate, ParamSpec, TypeVar


_P = ParamSpec("_P")
_T = TypeVar("_T")
_R = TypeVar("_R")


def implements(interface_method: Callable[Concatenate[Any, _P], _R]):
    def mark_implementation(
        implementation_method: Callable[Concatenate[_T, _P], _R]
    ) -> Callable[Concatenate[_T, _P], _R]:
        implementation_method.__explicit_implementation_for__ = interface_method
        
        return implementation_method
    
    return mark_implementation
