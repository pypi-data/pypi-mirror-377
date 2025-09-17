# src/pico_ioc/resolver.py
from __future__ import annotations

import inspect
from typing import Any, Annotated, Callable, get_args, get_origin, get_type_hints
from contextvars import ContextVar


_path: ContextVar[list[tuple[str, str]]] = ContextVar("pico_resolve_path", default=[])


def _get_hints(obj, owner_cls=None) -> dict:
    """Return type hints with include_extras=True, using correct globals/locals."""
    mod = inspect.getmodule(obj)
    g = getattr(mod, "__dict__", {})
    l = vars(owner_cls) if owner_cls is not None else None
    return get_type_hints(obj, globalns=g, localns=l, include_extras=True)


def _is_collection_hint(tp) -> bool:
    origin = get_origin(tp) or tp
    return origin in (list, tuple)


def _base_and_qualifiers_from_hint(tp):
    """
    Extract (base, qualifiers, container_kind) from a type hint.
    Supports list[T], tuple[T], Annotated[T, "qual1", ...].
    """
    origin = get_origin(tp) or tp
    args = get_args(tp) or ()
    container_kind = list if origin is list else tuple

    if not args:
        return (object, (), container_kind)

    inner = args[0]
    if get_origin(inner) is Annotated:
        base, *extras = get_args(inner)
        quals = tuple(a for a in extras if isinstance(a, str))
        return (base, quals, container_kind)

    return (inner, (), container_kind)


class Resolver:
    def __init__(self, container, *, prefer_name_first: bool = True):
        self.c = container
        self._prefer_name_first = bool(prefer_name_first)

    # --- core resolution ---

    def _resolve_dependencies_for_callable(self, fn: Callable, owner_cls: Any = None) -> dict:
        sig = inspect.signature(fn)
        hints = _get_hints(fn, owner_cls=owner_cls)
        kwargs = {}

        path_owner = getattr(owner_cls, "__name__", getattr(fn, "__qualname__", "callable"))
        if fn.__name__ == "__init__" and owner_cls:
            path_owner = f"{path_owner}.__init__"

        for name, param in sig.parameters.items():
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD) or name == "self":
                continue

            ann = hints.get(name, param.annotation)
            st = _path.get()
            _path.set(st + [(path_owner, name)])
            try:
                kwargs[name] = self._resolve_param(name, ann)
            except NameError as e:
                if param.default is not inspect.Parameter.empty:
                    _path.set(st)
                    continue
                if "(required by" in str(e):
                    raise
                chain = " -> ".join(f"{owner}.{param}" for owner, param in _path.get())
                raise NameError(f"{e} (required by {chain})") from e
            finally:
                cur = _path.get()
                if cur:
                    _path.set(cur[:-1])
        return kwargs

    def create_instance(self, cls: type) -> Any:
        """Instantiate a class by resolving its __init__ dependencies."""
        ctor_kwargs = self._resolve_dependencies_for_callable(cls.__init__, owner_cls=cls)
        return cls(**ctor_kwargs)

    def kwargs_for_callable(self, fn: Callable, *, owner_cls: Any = None) -> dict:
        """Resolve all keyword arguments for any callable."""
        return self._resolve_dependencies_for_callable(fn, owner_cls=owner_cls)

    # --- param resolution ---

    def _notify_resolve(self, key, ann, quals=()):
        for ci in getattr(self.c, "_container_interceptors", ()):
            try:
                ci.on_resolve(key, ann, tuple(quals) if quals else ())
            except Exception:
                pass

    def _resolve_param(self, name: str, ann: Any):
        # collections
        if _is_collection_hint(ann):
            base, quals, kind = _base_and_qualifiers_from_hint(ann)
            self._notify_resolve(base, ann, quals)
            items = self.c._resolve_all_for_base(base, qualifiers=quals)
            return list(items) if kind is list else tuple(items)

        # precedence
        if self._prefer_name_first and self.c.has(name):
            self._notify_resolve(name, ann, ())
            return self.c.get(name)

        if ann is not inspect._empty and self.c.has(ann):
            self._notify_resolve(ann, ann, ())
            return self.c.get(ann)

        if ann is not inspect._empty and isinstance(ann, type):
            for base in ann.__mro__[1:]:
                if self.c.has(base):
                    self._notify_resolve(base, ann, ())
                    return self.c.get(base)

        if self.c.has(name):
            self._notify_resolve(name, ann, ())
            return self.c.get(name)

        missing = ann if ann is not inspect._empty else name
        raise NameError(f"No provider found for key {missing!r}")

