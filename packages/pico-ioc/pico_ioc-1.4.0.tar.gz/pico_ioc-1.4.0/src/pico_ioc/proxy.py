# src/pico_ioc/proxy.py
from __future__ import annotations

import inspect
from functools import lru_cache
from typing import Any, Callable, Sequence

from .interceptors import Invocation, dispatch, MethodInterceptor


class ComponentProxy:
    """Proxy for lazy components. Creates the real object only when accessed."""
    def __init__(self, object_creator: Callable[[], Any]):
        object.__setattr__(self, "_object_creator", object_creator)
        object.__setattr__(self, "__real_object", None)

    def _get_real_object(self) -> Any:
        real = object.__getattribute__(self, "__real_object")
        if real is None:
            real = object.__getattribute__(self, "_object_creator")()
            object.__setattr__(self, "__real_object", real)
        return real

    @property
    def __class__(self):
        return self._get_real_object().__class__

    def __getattr__(self, name): return getattr(self._get_real_object(), name)
    def __setattr__(self, name, value): setattr(self._get_real_object(), name, value)
    def __delattr__(self, name): delattr(self._get_real_object(), name)
    def __str__(self): return str(self._get_real_object())
    def __repr__(self): return repr(self._get_real_object())
    def __dir__(self): return dir(self._get_real_object())

    # container-like behavior
    def __len__(self): return len(self._get_real_object())
    def __getitem__(self, key): return self._get_real_object()[key]
    def __setitem__(self, key, value): self._get_real_object()[key] = value
    def __delitem__(self, key): del self._get_real_object()[key]
    def __iter__(self): return iter(self._get_real_object())
    def __reversed__(self): return reversed(self._get_real_object())
    def __contains__(self, item): return item in self._get_real_object()

    # operators
    def __add__(self, other): return self._get_real_object() + other
    def __sub__(self, other): return self._get_real_object() - other
    def __mul__(self, other): return self._get_real_object() * other
    def __matmul__(self, other): return self._get_real_object() @ other
    def __truediv__(self, other): return self._get_real_object() / other
    def __floordiv__(self, other): return self._get_real_object() // other
    def __mod__(self, other): return self._get_real_object() % other
    def __divmod__(self, other): return divmod(self._get_real_object(), other)
    def __pow__(self, other, modulo=None): return pow(self._get_real_object(), other, modulo)
    def __lshift__(self, other): return self._get_real_object() << other
    def __rshift__(self, other): return self._get_real_object() >> other
    def __and__(self, other): return self._get_real_object() & other
    def __xor__(self, other): return self._get_real_object() ^ other
    def __or__(self, other): return self._get_real_object() | other

    # reflected operators
    def __radd__(self, other): return other + self._get_real_object()
    def __rsub__(self, other): return other - self._get_real_object()
    def __rmul__(self, other): return other * self._get_real_object()
    def __rmatmul__(self, other): return other @ self._get_real_object()
    def __rtruediv__(self, other): return other / self._get_real_object()
    def __rfloordiv__(self, other): return other // self._get_real_object()
    def __rmod__(self, other): return other % self._get_real_object()
    def __rdivmod__(self, other): return divmod(other, self._get_real_object())
    def __rpow__(self, other): return pow(other, self._get_real_object())
    def __rlshift__(self, other): return other << self._get_real_object()
    def __rrshift__(self, other): return other >> self._get_real_object()
    def __rand__(self, other): return other & self._get_real_object()
    def __rxor__(self, other): return other ^ self._get_real_object()
    def __ror__(self, other): return other | self._get_real_object()

    # misc
    def __neg__(self): return -self._get_real_object()
    def __pos__(self): return +self._get_real_object()
    def __abs__(self): return abs(self._get_real_object())
    def __invert__(self): return ~self._get_real_object()
    def __eq__(self, other): return self._get_real_object() == other
    def __ne__(self, other): return self._get_real_object() != other
    def __lt__(self, other): return self._get_real_object() < other
    def __le__(self, other): return self._get_real_object() <= other
    def __gt__(self, other): return self._get_real_object() > other
    def __ge__(self, other): return self._get_real_object() >= other
    def __hash__(self): return hash(self._get_real_object())
    def __bool__(self): return bool(self._get_real_object())

    # callables & context
    def __call__(self, *args, **kwargs): return self._get_real_object()(*args, **kwargs)
    def __enter__(self): return self._get_real_object().__enter__()
    def __exit__(self, exc_type, exc_val, exc_tb): return self._get_real_object().__exit__(exc_type, exc_val, exc_tb)


class IoCProxy:
    """Proxy that wraps an object and applies MethodInterceptors on method calls."""
    __slots__ = ("_target", "_interceptors")

    def __init__(self, target: object, interceptors: Sequence[MethodInterceptor]):
        self._target = target
        self._interceptors = tuple(interceptors)

    def __getattr__(self, name: str) -> Any:
        attr = getattr(self._target, name)
        if not callable(attr):
            return attr
        if hasattr(attr, "__get__"):
            bound_fn = attr.__get__(self._target, type(self._target))
        else:
            bound_fn = attr

        @lru_cache(maxsize=None)
        def _wrap(fn: Callable[..., Any]):
            if inspect.iscoroutinefunction(fn):
                async def aw(*args, **kwargs):
                    inv = Invocation(self._target, name, fn, args, kwargs)
                    return await dispatch(self._interceptors, inv)
                return aw
            else:
                def sw(*args, **kwargs):
                    inv = Invocation(self._target, name, fn, args, kwargs)
                    res = dispatch(self._interceptors, inv)
                    if inspect.isawaitable(res):
                        raise RuntimeError(f"Async interceptor on sync method: {name}")
                    return res
                return sw
        return _wrap(bound_fn)

