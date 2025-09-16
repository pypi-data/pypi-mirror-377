import pytest
from explicit_implementation import Interface, abstractmethod, implements


class IFoo(Interface):
    @abstractmethod
    def foo(self, x: int) -> str:
        ...


class IBar(Interface):
    @abstractmethod
    def bar(self, y: int) -> bool:
        ...


class IFooBar(Interface):
    @abstractmethod
    def foo(self) -> None:
        ...

    @abstractmethod
    def bar(self) -> int:
        ...


class IBaz(Interface):
    @abstractmethod
    def baz(self, z: str) -> float:
        ...


class IWithConcreteMethod(Interface):
    @abstractmethod
    def abstract_method(self) -> str:
        ...
    
    def concrete_method(self) -> str:
        """A normal concrete method that should be accessible directly."""
        return "concrete method result"
    
    @classmethod
    def class_method(cls) -> str:
        """A class method that should be accessible directly."""
        return "class method result"


class TestInterfaceBasics:
    """Test basic interface functionality."""
    
    def test_interface_is_abstract(self):
        """Test that interfaces cannot be instantiated."""
        with pytest.raises(TypeError):
            IFoo()
    
    def test_interface_inheritance(self):
        """Test that interfaces can inherit from Interface."""
        assert issubclass(IFoo, Interface)
        assert issubclass(IBar, Interface)
        assert issubclass(IFooBar, Interface)


class TestExplicitImplementation:
    """Test explicit implementation functionality."""
    
    def test_single_interface_implementation(self):
        """Test implementing a single interface."""
        
        class Concrete(IFoo):
            @implements(IFoo.foo)
            def foo_implementation(self, x: int) -> str:
                return str(x)
        
        concrete = Concrete()
        foo_impl = concrete.as_interface(IFoo)
        assert foo_impl.foo(42) == "42"
    
    def test_multiple_interface_implementation(self):
        """Test implementing multiple interfaces."""
        
        class Concrete(IFoo, IBar):
            @implements(IFoo.foo)
            def foo_implementation(self, x: int) -> str:
                return str(x)
            
            @implements(IBar.bar)
            def bar_implementation(self, y: int) -> bool:
                return y > 5
        
        concrete = Concrete()
        
        foo_impl = concrete.as_interface(IFoo)
        assert foo_impl.foo(42) == "42"
        
        bar_impl = concrete.as_interface(IBar)
        assert bar_impl.bar(10) is True
        assert bar_impl.bar(3) is False
    
    def test_complex_implementation(self):
        """Test the complex example from the usage documentation."""
        
        class Concrete(IFoo, IBar, IFooBar):
            @implements(IFoo.foo)
            def foo_from_ifoo(self, x: int) -> str:
                return str(x)

            @implements(IBar.bar)
            def bar_from_ibar(self, y: int) -> bool:
                return y > 5

            @implements(IFooBar.foo)
            def foo_from_ifoobar(self) -> None:
                print("IFooBar.foo!")

            @implements(IFooBar.bar)
            def bar_from_ifoobar(self) -> int:
                return 42
        
        concrete = Concrete()
        
        # Test IFoo interface
        ifoo = concrete.as_interface(IFoo)
        assert ifoo.foo(100) == "100"
        
        # Test IBar interface
        ibar = concrete.as_interface(IBar)
        assert ibar.bar(10) is True
        assert ibar.bar(2) is False
        
        # Test IFooBar interface
        ifoobar = concrete.as_interface(IFooBar)
        ifoobar.foo()  # Should not raise
        assert ifoobar.bar() == 42


class TestImplementationErrors:
    """Test error cases in implementation."""
    
    def test_missing_implementation(self):
        """Test that missing implementations raise TypeError."""
        
        with pytest.raises(TypeError):
            class Concrete(IFoo, concrete=True):
                def some_method(self):
                    pass  # Missing @implements(IFoo.foo)
    
    def test_duplicate_implementation(self):
        """Test that duplicate implementations raise TypeError."""
        
        with pytest.raises(TypeError):
            class Concrete(IFoo):
                @implements(IFoo.foo)
                def foo_impl1(self, x: int) -> str:
                    return str(x)
                
                @implements(IFoo.foo)  # Duplicate!
                def foo_impl2(self, x: int) -> str:
                    return str(x)
    
    def test_accessing_unimplemented_interface(self):
        """Test accessing an interface that wasn't implemented."""
        
        class Concrete(IFoo):
            @implements(IFoo.foo)
            def foo_implementation(self, x: int) -> str:
                return str(x)
        
        concrete = Concrete()
        
        with pytest.raises(TypeError, match="does not implement interface"):
            concrete.as_interface(IBar)
    
    def test_accessing_nonexistent_method(self):
        """Test accessing a method that doesn't exist on the interface."""
        
        class Concrete(IFoo):
            @implements(IFoo.foo)
            def foo_implementation(self, x: int) -> str:
                return str(x)
        
        concrete = Concrete()
        foo_impl = concrete.as_interface(IFoo)
        
        with pytest.raises(AttributeError):
            foo_impl.nonexistent_method()


class TestInterfaceAccess:
    """Test interface access patterns."""
    
    def test_as_interface_returns_correct_type(self):
        """Test that as_interface returns an object with correct interface methods."""
        
        class Concrete(IFoo, IBar):
            @implements(IFoo.foo)
            def foo_implementation(self, x: int) -> str:
                return f"foo: {x}"
            
            @implements(IBar.bar)
            def bar_implementation(self, y: int) -> bool:
                return y % 2 == 0
        
        concrete = Concrete()
        
        foo_impl = concrete.as_interface(IFoo)
        bar_impl = concrete.as_interface(IBar)
        
        # Test that each interface only has its own methods
        assert hasattr(foo_impl, '_instance')
        assert foo_impl.foo(5) == "foo: 5"
        
        assert hasattr(bar_impl, '_instance')
        assert bar_impl.bar(4) is True
        assert bar_impl.bar(3) is False
    
    def test_interface_method_binding(self):
        """Test that interface methods are properly bound to the instance."""
        
        class Concrete(IFoo):
            def __init__(self, value: str):
                self.value = value
            
            @implements(IFoo.foo)
            def foo_implementation(self, x: int) -> str:
                return f"{self.value}: {x}"
        
        concrete1 = Concrete("first")
        concrete2 = Concrete("second")
        
        foo1 = concrete1.as_interface(IFoo)
        foo2 = concrete2.as_interface(IFoo)
        
        assert foo1.foo(1) == "first: 1"
        assert foo2.foo(2) == "second: 2"


class TestMultipleInheritance:
    """Test complex inheritance scenarios."""
    
    def test_diamond_inheritance_pattern(self):
        """Test implementation with diamond inheritance pattern.
        
        In diamond inheritance, the shared base method is the same object
        across all inheritance paths, so you can only implement it once
        for the declaring interface (IBase). Accessing it through different
        diamond branches (ILeft/IRight) is not possible because they all
        refer to the same method object.
        """
        
        class IBase(Interface):
            @abstractmethod
            def base_method(self) -> str:
                ...
        
        class ILeft(IBase):
            @abstractmethod
            def left_method(self) -> int:
                ...
        
        class IRight(IBase):
            @abstractmethod
            def right_method(self) -> bool:
                ...
        
        class Concrete(ILeft, IRight):
            # Can only implement the base method once since ILeft.base_method
            # and IRight.base_method are the same method object from IBase
            
            @implements(IBase.base_method)
            def base_implementation(self) -> str:
                return "base"
            
            @implements(ILeft.left_method)
            def left_implementation(self) -> int:
                return 42
            
            @implements(IRight.right_method)
            def right_implementation(self) -> bool:
                return True
        
        concrete = Concrete()
        
        # Can access the base method only through the base interface
        base_impl = concrete.as_interface(IBase)
        assert base_impl.base_method() == "base"
        
        # Cannot access base_method through ILeft or IRight because
        # the implementation is registered for IBase, not for ILeft/IRight
        left_impl = concrete.as_interface(ILeft)
        right_impl = concrete.as_interface(IRight)
        
        # These should work - accessing the interface-specific methods
        assert left_impl.left_method() == 42
        assert right_impl.right_method() is True
        
        # These would fail because base_method implementation is only
        # registered for IBase, not ILeft or IRight
        with pytest.raises(TypeError, match="does not provide an explicit implementation for method 'base_method'"):
            left_impl.base_method()
            
        with pytest.raises(TypeError, match="does not provide an explicit implementation for method 'base_method'"):
            right_impl.base_method()
    
    def test_partial_implementation_allowed_by_default(self):
        """Test that partial implementations are allowed by default at class definition time."""
        
        # This should work - partial implementation class definition is allowed by default
        class PartialImplementation(IFoo, IBar):
            @implements(IFoo.foo)
            def foo_implementation(self, x: int) -> str:
                return str(x)
            # Missing IBar.bar implementation - but class definition is allowed by default
        
        # However, can't instantiate due to unimplemented abstract methods
        with pytest.raises(TypeError, match="Can't instantiate abstract class"):
            PartialImplementation()
        
        # The class exists and has the right structure
        assert issubclass(PartialImplementation, IFoo)
        assert issubclass(PartialImplementation, IBar)
        assert hasattr(PartialImplementation, '__explicit__implementations__')
    
    def test_partial_implementation_not_allowed_with_concrete(self):
        """Test that partial implementations are not allowed when concrete=True."""
        
        with pytest.raises(TypeError):
            class Concrete(IFoo, IBar, concrete=True):
                @implements(IFoo.foo)
                def foo_implementation(self, x: int) -> str:
                    return str(x)
                # Missing IBar.bar implementation - should raise TypeError


class TestConcreteMethodAccess:
    """Test accessing concrete methods in interfaces directly from concrete classes."""
    
    def test_concrete_method_direct_access(self):
        """Test that concrete methods in interfaces can be accessed directly without explicit implementation."""
        
        class Concrete(IWithConcreteMethod):
            @implements(IWithConcreteMethod.abstract_method)
            def abstract_method_impl(self) -> str:
                return "abstract implementation"
        
        concrete = Concrete()
        
        # Access concrete method directly - should work without explicit implementation
        result = concrete.concrete_method()
        assert result == "concrete method result"
        
        # Access class method directly - should work without explicit implementation
        class_result = concrete.class_method()
        assert class_result == "class method result"
        
        # Also test accessing class method on the class itself
        class_result_from_class = Concrete.class_method()
        assert class_result_from_class == "class method result"
        
        # Verify that the abstract method works through interface casting
        interface_impl = concrete.as_interface(IWithConcreteMethod)
        abstract_result = interface_impl.abstract_method()
        assert abstract_result == "abstract implementation"
    
    def test_concrete_method_inheritance_behavior(self):
        """Test how concrete methods behave with inheritance and overriding."""
        
        class Concrete(IWithConcreteMethod):
            @implements(IWithConcreteMethod.abstract_method)
            def abstract_method_impl(self) -> str:
                return "abstract implementation"
            
            def concrete_method(self) -> str:
                """Override the concrete method in the concrete class."""
                return "overridden concrete method"
        
        concrete = Concrete()
        
        # Direct access should use the overridden version
        direct_result = concrete.concrete_method()
        assert direct_result == "overridden concrete method"
        
        # Class method should still work the same way since it's not overridden
        class_result = concrete.class_method()
        assert class_result == "class method result"
        
        # Concrete methods should be accessible through interface casting
        # Since there's no explicit implementation, it falls back to the concrete class's method
        interface_impl = concrete.as_interface(IWithConcreteMethod)
        interface_result = interface_impl.concrete_method()
        assert interface_result == "overridden concrete method"  # Uses the concrete class's implementation
        
        # Class methods should also be accessible through interface casting
        interface_class_result = interface_impl.class_method()
        assert interface_class_result == "class method result"
    
    def test_concrete_method_without_override(self):
        """Test concrete method access when not overridden in concrete class."""
        
        class SimpleImplementation(IWithConcreteMethod):
            @implements(IWithConcreteMethod.abstract_method)
            def abstract_method_impl(self) -> str:
                return "simple abstract implementation"
        
        concrete = SimpleImplementation()
        
        # Direct access should use the interface's concrete method
        direct_result = concrete.concrete_method()
        assert direct_result == "concrete method result"
        
        # Interface casting should also work and return the same result
        interface_impl = concrete.as_interface(IWithConcreteMethod)
        interface_result = interface_impl.concrete_method()
        assert interface_result == "concrete method result"
        
        # Both should be the same since there's no override
        assert direct_result == interface_result


class TestEdgeCases:
    """Test edge cases and boundary conditions."""
    
    def test_empty_interface(self):
        """Test interfaces with no abstract methods."""
        
        class IEmpty(Interface):
            pass
        
        class Concrete(IEmpty):
            pass
        
        concrete = Concrete()
        empty_impl = concrete.as_interface(IEmpty)
        assert empty_impl is not None
    
    def test_interface_with_multiple_methods(self):
        """Test interface with multiple abstract methods."""
        
        class IMultiple(Interface):
            @abstractmethod
            def method1(self) -> str:
                ...
            
            @abstractmethod
            def method2(self, x: int) -> int:
                ...
            
            @abstractmethod
            def method3(self, a: str, b: bool) -> float:
                ...
        
        class Concrete(IMultiple):
            @implements(IMultiple.method1)
            def method1_implementation(self) -> str:
                return "one"
            
            @implements(IMultiple.method2)
            def method2_implementation(self, x: int) -> int:
                return x * 2
            
            @implements(IMultiple.method3)
            def method3_implementation(self, a: str, b: bool) -> float:
                return len(a) if b else 0.0
        
        concrete = Concrete()
        impl = concrete.as_interface(IMultiple)
        
        assert impl.method1() == "one"
        assert impl.method2(5) == 10
        assert impl.method3("hello", True) == 5.0
        assert impl.method3("world", False) == 0.0


if __name__ == "__main__":
    pytest.main([__file__])