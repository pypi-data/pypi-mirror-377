"""Runtime final guard decorators & metaclass."""

# --- Utilities ---

FINAL_ATTR = "__is_final__"

def _mark_func_final(func):
    # Mark on the real function object
    setattr(func, FINAL_ATTR, True)

def _is_func_final(func):
    return getattr(func, FINAL_ATTR, False)

def final(obj):
    """
    Mark a method/property as final.
    Supports: regular function, @staticmethod, @classmethod, and @property (including fget/fset/fdel).
    """
    if isinstance(obj, staticmethod):
        _mark_func_final(obj.__func__)
        return staticmethod(obj.__func__)
    if isinstance(obj, classmethod):
        _mark_func_final(obj.__func__)
        return classmethod(obj.__func__)
    if isinstance(obj, property):
        # If any accessor is marked final, the whole property is considered final
        if obj.fget:
            _mark_func_final(obj.fget)
        if obj.fset:
            _mark_func_final(obj.fset)
        if obj.fdel:
            _mark_func_final(obj.fdel)
        return obj
    # Regular function
    _mark_func_final(obj)
    return obj


def final_class(_cls=None, *, exclude=None, include_magic=False):
    """Bulk mark methods/properties in a class as final.

    Usage:
        @final_class
        class A: ...

        @final_class(exclude={"debug"}, include_magic=True)
        class B: ...

    Args:
        exclude: Optional set/list/tuple of member names NOT to mark final.
        include_magic: When True, also mark magic methods of the form __xxx__.
    """
    if exclude is None:
        exclude_set = set()
    else:
        exclude_set = set(exclude)

    def _apply(cls):
        magic_collected = set()
        for name, value in list(vars(cls).items()):
            is_magic = name.startswith("__") and name.endswith("__")
            if name in exclude_set:
                continue
            if is_magic and not include_magic:
                continue
            if is_magic and include_magic and name in {"__dict__", "__weakref__"}:
                # Skip builtin structures
                continue
            # Mark
            if isinstance(value, (staticmethod, classmethod, property)):
                marked = final(value)
                setattr(cls, name, marked)
            elif callable(value):
                final(value)
            if is_magic and include_magic and _is_attr_final(getattr(cls, name)):
                magic_collected.add(name)
        # Update __final_names__ if present
        if hasattr(cls, "__final_names__"):
            current = set(getattr(cls, "__final_names__"))
            newly = {
                n for n, v in vars(cls).items()
                if (include_magic or not (n.startswith("__") and n.endswith("__")))
                and n not in exclude_set
                and _is_attr_final(v)
            }
            setattr(cls, "__final_names__", frozenset(current | newly))
        if magic_collected:
            existing_magic = set(getattr(cls, "__final_magic_names__", frozenset()))
            setattr(cls, "__final_magic_names__", frozenset(existing_magic | magic_collected))
        return cls

    if _cls is not None and callable(_cls):  # usage without parameters
        return _apply(_cls)
    return _apply


def _is_attr_final(value):
    """Check whether a class-level member is marked as final."""
    if isinstance(value, staticmethod) or isinstance(value, classmethod):
        return _is_func_final(value.__func__)
    if isinstance(value, property):
        return any(
            _is_func_final(f)
            for f in (value.fget, value.fset, value.fdel)
            if f is not None
        )
    # Other callables or markable descriptors
    return _is_func_final(value)


def _collect_final_names_from_bases(bases):
    """Collect names marked final across all base classes.

    - Regular methods/properties: exclude magic (unless a base stores them in __final_magic_names__).
    - Magic methods: included only when ancestors recorded them via final_class(include_magic=True).
    """
    finals = set()
    magic_finals = set()
    for base in bases:
    # Only inspect that layer's __dict__ to avoid bound descriptor results
        for name, value in vars(base).items():
            if name.startswith("__") and name.endswith("__"):
        # Treat as final only if explicitly recorded by ancestor
                if name in getattr(base, "__final_magic_names__", frozenset()) and _is_attr_final(value):
                    magic_finals.add(name)
                continue
            if _is_attr_final(value):
                finals.add(name)
    # Merge ancestor-recorded magic finals
        magic_finals.update(getattr(base, "__final_magic_names__", frozenset()))
    return finals | magic_finals


# --- Metaclass ---

class Access(type):
    """
    Prevent members marked with @final from being overridden in subclasses,
    and block dynamic overrides after the class is created.
    """
    def __new__(mcs, name, bases, class_dict):
        # 1) Collect final names across the inheritance chain
        inherited_finals = _collect_final_names_from_bases(bases)

        # 2) Check if this class attempts to override any of them
        violated = inherited_finals.intersection(class_dict.keys())
        if violated:
            raise RuntimeError(
                f"The following members are final in base classes and cannot be overridden: {sorted(violated)}"
            )

        # 3) Create the class
        cls = super().__new__(mcs, name, bases, class_dict)

        # 4) Persist the set of non-overridable names (including ancestors)
        #    New finals marked here are inherited by subclasses as well.
        own_finals = {
            n for n, v in vars(cls).items()
            if not (n.startswith("__") and n.endswith("__")) and _is_attr_final(v)
        }
        # Merge all sources
        all_finals = set(inherited_finals) | own_finals
        setattr(cls, "__final_names__", frozenset(all_finals))

        return cls

    def __setattr__(cls, name, value):
        """
        Block reassigning a final name after the class is created (monkey patch / dynamic override).
        """
        final_names = getattr(cls, "__final_names__", frozenset())
        if name in final_names:
            raise RuntimeError(f"Member '{name}' is final; reassignment/override is forbidden.")
        return super().__setattr__(name, value)