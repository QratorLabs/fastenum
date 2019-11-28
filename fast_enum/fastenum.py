"""
(c) 2019 Andrey Semenov
(c) 2019 Qrator Labs
A fast(er) Enum implementation with a set of features not provided by stdlib's Enum:
- an enum class can be declared in lightweight (auto-valued) mode
- a set of enum classes can have a base class providing common logic; subclassing is restricted
 only after an enum is actually generated (a class declared has at least one enum-value), until
 then an arbitrary base classes tree could be declared to provide a logic needed
- an auto-valued and value-provided form of enum declarations could be mixed
- for auto-valued enum instances a counter could be 0 or 1 based (configurable within class
 declaration)
- an enum class declaration could be after-init hooked to handle arbitrary additional setup for
 enum values (at that point the context has all the values created and initialized, additional
 properties that depend on other enum values could be calculated and set up)
"""
from typing import Any, Text, Dict, List, Tuple, Type, Optional, Callable


# pylint: disable=inconsistent-return-statements
def _resolve_init(bases: Tuple[Type]) -> Optional[Callable]:
    for bcls in bases:
        for rcls in bcls.mro():
            resolved_init = getattr(rcls, '__init__')
            if resolved_init and resolved_init is not object.__init__:
                return resolved_init


class FastEnum(type):
    """
    A metaclass that handles enum-classes creation.

    Possible options for classes using this metaclass:
    - auto-generated values (see examples.py `MixedEnum` and `LightEnum`)
    - subclassing possible until actual enum is not declared
     (see examples.py `ExtEnumOne` and `ExtEnumTwo`)
    - late init hooking (see examples.py `HookedEnum`)
    - enum modifications protection (see examples.py comment after `ExtendedEnum`)
    """
    # pylint: disable=bad-mcs-classmethod-argument,protected-access,too-many-locals
    # pylint: disable=too-many-branches
    def __new__(mcs, name, bases, namespace: Dict[Text, Any]):
        attributes: List[Text] = [k for k in namespace.keys()
                                  if (not k.startswith('_') and k.isupper())]
        attributes += [k for k, v in namespace.get('__annotations__', {}).items()
                       if (not k.startswith('_') and k.isupper() and v == name)]
        light_val = 0 + int(not bool(namespace.get('_ZERO_VALUED')))
        for attr in attributes:
            if attr in namespace:
                continue
            else:
                namespace[attr] = light_val
                light_val += 1

        __slots__ = set(namespace.get('__slots__', tuple())) | {'name', 'value',
                                                                '_value_to_instance_map'}
        namespace['__slots__'] = tuple(__slots__)
        if '__init__' not in namespace:
            namespace['__init__'] = _resolve_init(bases) or mcs.__init
        if '__annotations__' not in namespace:
            __annotations__ = dict(name=Text, value=Any)
            for k in attributes:
                __annotations__[k] = name
            namespace['__annotations__'] = __annotations__
        typ = type.__new__(mcs, name, bases, namespace)
        if attributes:
            typ._value_to_instance_map = {}
            for instance_name in attributes:
                val = namespace[instance_name]
                if not isinstance(val, tuple):
                    val = (val,)
                if val[0] in typ._value_to_instance_map:
                    inst = typ._value_to_instance_map[val[0]]
                else:
                    inst = typ(*val, name=instance_name)
                    typ._value_to_instance_map[inst.value] = inst
                setattr(typ, instance_name, inst)

            # noinspection PyUnresolvedReferences
            typ.__call__ = typ.__new__ = typ.get
            del typ.__init__
            typ.__hash__ = mcs.__hash
            typ.__eq__ = mcs.__eq
            typ.__copy__ = mcs.__copy
            typ.__deepcopy__ = mcs.__deepcopy
            typ.__reduce__ = mcs.__reduce
            if '__str__' not in namespace:
                typ.__str__ = mcs.__str
            if '__repr__' not in namespace:
                typ.__repr__ = mcs.__repr

            if f'_{name}__init_late' in namespace:
                fun = namespace[f'_{name}__init_late']
                for instance in typ._value_to_instance_map.values():
                    fun(instance)
                delattr(typ, f'_{name}__init_late')

            typ.__setattr__ = typ.__delattr__ = mcs.__restrict_modification
            typ._finalized = True
        return typ

    @staticmethod
    def __init(instance, value: Any, name: Text):
        instance.value = value
        instance.name = name

    # pylint: disable=missing-docstring
    @staticmethod
    def get(typ, val=None):
        # noinspection PyProtectedMember
        if not isinstance(typ._value_to_instance_map, dict):
            for cls in typ.mro():
                if cls is typ:
                    continue
                if hasattr(cls, '_value_to_instance_map') and isinstance(cls._value_to_instance_map, dict):
                    return cls._value_to_instance_map[val]
            raise ValueError(f'Value {val} is not found in this enum type declaration')
        # noinspection PyProtectedMember
        member = typ._value_to_instance_map.get(val)
        if member is None:
            raise ValueError(f'Value {val} is not found in this enum type declaration')
        return member

    @staticmethod
    def __eq(val, other):
        return isinstance(other, type(val)) and val is other

    def __hash(cls):
        # noinspection PyUnresolvedReferences
        return hash(cls.value)

    @staticmethod
    def __restrict_modification(*a, **k):
        raise TypeError(f'Enum-like classes strictly prohibit changing any attribute/property'
                        f' after they are once set')

    def __iter__(cls):
        return iter(cls._value_to_instance_map.values())

    def __setattr__(cls, key, value):
        if hasattr(cls, '_finalized'):
            cls.__restrict_modification()
        super().__setattr__(key, value)

    def __delattr__(cls, item):
        if hasattr(cls, '_finalized'):
            cls.__restrict_modification()
        super().__delattr__(item)

    def __getitem__(cls, item):
        return getattr(cls, item)

    def has_value(cls, value):
        return value in cls._value_to_instance_map

    # pylint: disable=unused-argument
    # noinspection PyUnusedLocal,SpellCheckingInspection
    def __deepcopy(cls, memodict=None):
        return cls

    def __copy(cls):
        return cls

    def __reduce(cls):
        typ = type(cls)
        # noinspection PyUnresolvedReferences
        return typ.get, (typ, cls.value)

    @staticmethod
    def __str(clz):
        return f'{clz.__class__.__name__}.{clz.name}'

    @staticmethod
    def __repr(clz):
        return f'<{clz.__class__.__name__}.{clz.name}: {clz.value}>'
