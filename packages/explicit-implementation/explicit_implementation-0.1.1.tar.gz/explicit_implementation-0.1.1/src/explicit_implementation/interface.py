from abc import ABCMeta
from typing import Callable, Dict, FrozenSet, Type, TypeVar, cast


ImplementationMapping = Dict[Callable, Callable]
T = TypeVar('T', bound='Interface')


class InterfaceMeta(ABCMeta):
    __explicit__implementations__: Dict[Type['Interface'], ImplementationMapping]
    __explicit__specifications__: FrozenSet[Callable]

    def __new__(mcs, name, bases, namespace, *, concrete: bool = False):
        inherited_specifications = []
        for base in bases:
            if not issubclass(base, Interface):
                continue

            inherited_specifications.extend(base.__explicit__specifications__)

        defined_specifications = []
        for attr_name, attr_value in namespace.items():
            if not callable(attr_value) or not getattr(attr_value, "__isabstractmethod__", False):
                continue

            defined_specifications.append(attr_value)

        inherited_specifications.extend(defined_specifications)
        inherited_specifications = set(inherited_specifications)

        inherited_implementations: Dict[Type['Interface'], ImplementationMapping] = {}
        multiple_overrides: list[Callable] = []
        for base in bases:
            if not issubclass(base, Interface):
                continue

            try:
                explicit_implementations = base.__explicit__implementations__
            except AttributeError:
                continue

            if base.__explicit__specifications__:
                inherited_implementations[base] = {}

            for interface, implementations in explicit_implementations.items():
                if interface not in inherited_implementations:
                    inherited_implementations[interface] = {}

                for specification, implementation in implementations.items():
                    if implementation in multiple_overrides:
                        continue

                    if implementation in inherited_implementations[interface]:
                        multiple_overrides.append(implementation)

                    inherited_implementations[interface][specification] = implementation

        values_to_remove = []
        for attr_name, attr_value in namespace.items():
            if not callable(attr_value):
                continue

            try:
                explicit_implementation_for = attr_value.__explicit_implementation_for__
            except AttributeError:
                continue

            declaring_interface = explicit_implementation_for.__declaring_interface__

            try:
                inherited_specifications.remove(explicit_implementation_for)
            except (KeyError, ValueError):
                raise TypeError(f"Method '{attr_name}' is marked as an explicit implementation for method '{explicit_implementation_for.__name__}', which is not an abstract method of any base interface of '{name}'") from None
            
            try:
                explicit_implementations = inherited_implementations[declaring_interface]
            except KeyError:
                explicit_implementations = inherited_implementations[declaring_interface] = {}

            explicit_implementations[explicit_implementation_for] = attr_value
            if explicit_implementation_for in multiple_overrides:
                multiple_overrides.remove(explicit_implementation_for)
            values_to_remove.append(attr_name)

        if multiple_overrides:
            method_names = ", ".join(f"'{m.__name__}'" for m in multiple_overrides)
            raise TypeError(f"Methods {method_names} are marked as explicit implementations for methods of multiple base interfaces of '{name}'")

        for attr_name in values_to_remove:
            del namespace[attr_name]

        cls = super().__new__(mcs, name, bases, namespace)

        for specification in defined_specifications:
            specification.__declaring_interface__ = cls

        if concrete and inherited_specifications:
            raise TypeError(f"Concrete class '{name}' does not provide explicit implementations for all abstract methods: {', '.join(m.__name__ for m in inherited_specifications)}")

        cls.__explicit__specifications__ = frozenset(inherited_specifications)
        cls.__explicit__implementations__ = inherited_implementations

        try:
            cls.__abstractmethods__ = frozenset(map(lambda m: m.__name__, cls.__explicit__specifications__))
        except AttributeError:
            cls.__abstractmethods__ = frozenset()

        return cls
    
    def as_interface_type(cls, interface: Type[T]) -> Callable[[T], T]:
        if not isinstance(interface, type) or not issubclass(interface, Interface):
            raise TypeError(f"Expected an interface type, got {interface}")
        
        if not issubclass(cls, interface):
            raise TypeError(f"Class {cls.__name__} does not implement interface {interface.__name__}")

        if not interface.__explicit__specifications__:
            return lambda instance: cast(T, instance)
            
        if interface not in cls.__explicit__implementations__:
            raise TypeError(f"Class {cls.__name__} does not implement interface {interface.__name__}")

        implementation_mapping = cls.__explicit__implementations__[interface]

        class ExplicitImplementation:
            def __init__(self, instance: T):
                self._instance = instance

            def __getattr__(self, name):
                try:
                    specification = getattr(interface, name)
                except AttributeError as e:
                    raise e from None
                
                if hasattr(specification, "__declaring_interface__"):
                    try:
                        return implementation_mapping[specification].__get__(self._instance)
                    except KeyError:
                        raise TypeError(f"Class {cls.__name__} does not provide an explicit implementation for method '{name}' of interface {interface.__name__}") from None
                
                return getattr(self._instance, name)

        return cast(Callable[[T], T], ExplicitImplementation)


class Interface(metaclass=InterfaceMeta):
    def as_interface(self, interface: Type[T]) -> T:
        return type(self).as_interface_type(interface)(cast(T, self))
