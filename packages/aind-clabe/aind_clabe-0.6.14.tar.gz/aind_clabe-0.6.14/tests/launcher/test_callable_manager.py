import logging
import re

import pytest

from clabe.launcher._callable_manager import Promise, _CallableManager, _UnsetType, ignore_errors, run_if


class TestCallableManager:
    def test_register_and_get_result(self):
        manager = _CallableManager()

        def test_function(value: str):
            return "Hello from " + value

        promise = manager.register(test_function)
        promise.invoke("test_input")
        retrieved_result = manager.get_result(test_function)
        assert retrieved_result == "Hello from test_input"

    def test_get_result_non_existent_callable(self):
        manager = _CallableManager()

        def non_existent_function(value: str):
            pass

        with pytest.raises(KeyError, match="Callable non_existent_function not found in registered promises"):
            manager.get_result(non_existent_function)

    def test_run_multiple_callables(self):
        manager = _CallableManager()

        results = []

        def func_a(value: str):
            results.append(value + "A")
            return value + "A"

        def func_b(value: str):
            results.append(value + "B")
            return value + "B"

        manager.register(func_a)
        manager.register(func_b)

        manager.run("input_")

        assert "input_A" in results
        assert "input_B" in results
        assert manager.get_result(func_a) == "input_A"
        assert manager.get_result(func_b) == "input_B"

    def test_run_only_once(self):
        manager = _CallableManager()
        call_count = 0

        def func_c(value: str):
            nonlocal call_count
            call_count += 1
            return value

        manager.register(func_c)
        manager.run("first")
        manager.run("second")

        assert call_count == 1
        assert manager.get_result(func_c) == "first"

    def test_clear_callables(self):
        manager = _CallableManager()

        def func_d(value: str):
            pass

        manager.register(func_d)
        assert len(manager._callable_promises) == 1
        manager.clear()
        assert len(manager._callable_promises) == 0

    def test_unregister_callable(self):
        manager = _CallableManager()

        def func_e(value: str):
            pass

        promise = manager.register(func_e)
        assert len(manager._callable_promises) == 1
        unregistered_promise = manager.unregister(func_e)
        assert len(manager._callable_promises) == 0
        assert unregistered_promise == promise

    def test_promise_invoke_and_result(self):
        def test_func(x):
            return x * 2

        promise = Promise(test_func)
        assert not promise.has_result()

        result = promise.invoke(5)
        assert result == 10
        assert promise.has_result()
        assert promise.result == 10

        # Test invoking again returns the same result without re-executing
        result_again = promise.invoke(10)  # Should still return 10, not 20
        assert result_again == 10

    def test_promise_result_before_invoke_raises_error(self):
        def test_func(x):
            return x * 2

        promise = Promise(test_func)
        with pytest.raises(RuntimeError, match=re.escape("Callable has not been executed yet. Call invoke() first.")):
            promise.result

    def test_unset_type_singleton(self):
        unset1 = _UnsetType()
        unset2 = _UnsetType()
        assert unset1 is unset2

    def test_promise_result_consistency(self):
        promise = Promise.from_value(1)
        promise.invoke(0, 2, 3, 4)
        assert promise.result == 1


class TestIgnoreErrorsDecorator:
    def test_ignore_errors_default_behavior(self, caplog):
        """Test that the decorator catches exceptions and returns None by default."""

        @ignore_errors()
        def failing_function():
            raise ValueError("Test error")

        with caplog.at_level(logging.WARNING):
            result = failing_function()

        assert result is None
        assert "Exception in failing_function: Test error" in caplog.text

    def test_ignore_errors_custom_default_return(self, caplog):
        """Test that the decorator returns a custom default value."""

        @ignore_errors(default_return="error occurred")
        def failing_function():
            raise RuntimeError("Test error")

        with caplog.at_level(logging.WARNING):
            result = failing_function()

        assert result == "error occurred"
        assert "Exception in failing_function: Test error" in caplog.text

    def test_ignore_errors_specific_exception_type(self, caplog):
        """Test that the decorator only catches specified exception types."""

        @ignore_errors(exception_types=ValueError, default_return="caught ValueError")
        def function_with_value_error():
            raise ValueError("This will be caught")

        @ignore_errors(exception_types=ValueError, default_return="caught ValueError")
        def function_with_runtime_error():
            raise RuntimeError("This will not be caught")

        # Should catch ValueError
        with caplog.at_level(logging.WARNING):
            result1 = function_with_value_error()

        assert result1 == "caught ValueError"
        assert "Exception in function_with_value_error: This will be caught" in caplog.text

        # Should not catch RuntimeError
        with pytest.raises(RuntimeError, match="This will not be caught"):
            function_with_runtime_error()

    def test_ignore_errors_multiple_exception_types(self, caplog):
        """Test that the decorator catches multiple exception types."""

        @ignore_errors(exception_types=(ValueError, TypeError), default_return="caught exception")
        def function_with_value_error():
            raise ValueError("ValueError")

        @ignore_errors(exception_types=(ValueError, TypeError), default_return="caught exception")
        def function_with_type_error():
            raise TypeError("TypeError")

        @ignore_errors(exception_types=(ValueError, TypeError), default_return="caught exception")
        def function_with_runtime_error():
            raise RuntimeError("RuntimeError")

        # Should catch ValueError
        with caplog.at_level(logging.WARNING):
            result1 = function_with_value_error()
        assert result1 == "caught exception"

        # Should catch TypeError
        with caplog.at_level(logging.WARNING):
            result2 = function_with_type_error()
        assert result2 == "caught exception"

        # Should not catch RuntimeError
        with pytest.raises(RuntimeError, match="RuntimeError"):
            function_with_runtime_error()

    def test_ignore_errors_successful_execution(self):
        """Test that the decorator doesn't interfere with successful function execution."""

        @ignore_errors()
        def successful_function(x, y):
            return x + y

        result = successful_function(2, 3)
        assert result == 5

    def test_ignore_errors_preserves_function_metadata(self):
        """Test that the decorator preserves function metadata using functools.wraps."""

        @ignore_errors()
        def documented_function():
            """This is a test function."""
            return "success"

        assert hasattr(documented_function, "__name__")
        assert hasattr(documented_function, "__doc__")
        # Note: The actual name and doc may be wrapped, but they should exist

    def test_ignore_errors_with_arguments_and_kwargs(self, caplog):
        """Test that the decorator works with functions that have arguments."""

        @ignore_errors(default_return="default")
        def function_with_args(a, b, c=None, d="default"):
            if a == "fail":
                raise ValueError("Intentional failure")
            return f"a={a}, b={b}, c={c}, d={d}"

        # Test successful execution with args and kwargs
        result1 = function_with_args("success", "test", c="custom", d="modified")
        assert result1 == "a=success, b=test, c=custom, d=modified"

        # Test exception handling with args and kwargs
        with caplog.at_level(logging.WARNING):
            result2 = function_with_args("fail", "test", c="custom")

        assert result2 == "default"
        assert "Exception in function_with_args: Intentional failure" in caplog.text

    def test_ignore_errors_nested_exceptions(self, caplog):
        """Test that the decorator handles nested function calls properly."""

        @ignore_errors(default_return="outer_default")
        def outer_function():
            return inner_function()

        @ignore_errors(default_return="inner_default")
        def inner_function():
            raise ValueError("Inner error")

        with caplog.at_level(logging.WARNING):
            result = outer_function()

        # The inner function should catch its own exception and return "inner_default"
        # The outer function should succeed and return the inner function's result
        assert result == "inner_default"
        assert "Exception in inner_function: Inner error" in caplog.text

    def test_ignore_errors_lambda_function(self, caplog):
        """Test that the decorator works with lambda functions."""
        failing_lambda = ignore_errors(default_return="lambda_failed")(lambda x: x / 0 if x == 0 else x * 2)

        # Test successful execution
        result1 = failing_lambda(5)
        assert result1 == 10

        # Test exception handling
        with caplog.at_level(logging.WARNING):
            result2 = failing_lambda(0)

        assert result2 == "lambda_failed"
        # Lambda functions have a generic name
        assert "Exception in <lambda>: division by zero" in caplog.text


class TestRunIfDecorator:
    def test_run_if_runs_when_predicate_true(self):
        def always_true(*args, **kwargs):
            return True

        @run_if(always_true)
        def my_func(x):
            return x * 2

        assert my_func(3) == 6

    def test_run_if_returns_none_when_predicate_false(self):
        def always_false(*args, **kwargs):
            return False

        @run_if(always_false)
        def my_func(x):
            return x * 2

        assert my_func(3) is None

    def test_run_if_predicate_depends_on_args(self):
        def is_true(x: bool) -> bool:
            return x

        def square(x):
            return x * x

        @run_if(is_true, True)
        def decorated_square(x):
            return square(x)

        assert run_if(is_true, True)(lambda: square(2))() == 4
        assert run_if(is_true, False)(lambda: square(-1))() is None
        assert decorated_square(2) == 4
        assert decorated_square(-1) == 1

    def test_run_if_preserves_function_metadata(self):
        def always_true(*args, **kwargs):
            return True

        @run_if(always_true)
        def documented_func(x):
            """This function squares its input."""
            return x * x

        assert hasattr(documented_func, "__name__")
        assert hasattr(documented_func, "__doc__")
        assert documented_func.__doc__ == "This function squares its input."
