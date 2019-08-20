from typing import Any, Text, Dict, List, Tuple, Type


def _resolve_init(bases: Tuple[Type]):
    for bcls in bases:
        for rcls in bcls.mro():
            resolved_init = getattr(rcls, '__init__')
            if resolved_init and resolved_init is not object.__init__:
                return resolved_init


class FastEnum(type):
    def __new__(mcs, name, bases, namespace: Dict[Text, Any]):
        attributes: List[Text] = [k for k in namespace.keys()
                                  if (not k.startswith('_') and k.isupper())]
        attributes += [k for k, v in namespace.get('__annotations__', {}).items()
                       if (not k.startswith('_') and k.isupper() and v == name)]
        zero_valued = bool(namespace.get('_ZERO_VALUED'))
        light_val = 0 + int(not zero_valued)
        for attr in attributes:
            if attr in namespace:
                continue
            else:
                namespace[attr] = light_val
                light_val += 1

        __slots__ = set(namespace.get('__slots__', tuple()))
        __slots__.update({'name', 'value', '_value_to_instance_map'})
        namespace['__slots__'] = tuple(__slots__)
        if '__init__' not in namespace:
            resolved_init = _resolve_init(bases)
            namespace['__init__'] = resolved_init or mcs.__init
        if '__annotations__' not in namespace:
            __annotations__ = dict(name=Text, value=Any)
            for k in attributes:
                __annotations__[k] = name
            namespace['__annotations__'] = __annotations__
        typ = type.__new__(mcs, name, bases, namespace)
        if attributes:
            typ._value_to_instance_map = {}
            for s in attributes:
                val = namespace[s]
                if not isinstance(val, tuple):
                    val = (val,)
                if val[0] in typ._value_to_instance_map:
                    inst = typ._value_to_instance_map[val[0]]
                else:
                    inst = typ(*val, name=s)
                    typ._value_to_instance_map[inst.value] = inst
                setattr(typ, s, inst)

            # noinspection PyUnresolvedReferences
            typ.__call__ = typ.__new__ = typ.get
            del typ.__init__

            if f'_{name}__init_late' in namespace:
                fun = namespace[f'_{name}__init_late']
                for v in typ._value_to_instance_map.values():
                    fun(v)
                delattr(typ, f'_{name}__init_late')

            typ.__setattr__ = typ.__delattr__ = mcs.__restrict_modification
            typ.__hash__ = mcs.__hash
            typ.__eq__ = mcs.eq
            typ.__copy__ = mcs.__copy
            typ.__deepcopy__ = mcs.__deepcopy
            typ.__reduce__ = mcs.__reduce
            if '__str__' not in namespace:
                typ.__str__ = mcs.__str
            if '__repr__' not in namespace:
                typ.__repr__ = mcs.__repr
            typ._finalized = True
        return typ

    @staticmethod
    def __init(self, value: Any, name: Text):
        self.value = value
        self.name = name

    @staticmethod
    def get(typ, val=None):
        # noinspection PyProtectedMember
        return typ._value_to_instance_map[val]

    @staticmethod
    def eq(val, other):
        return isinstance(other, type(val)) and val is other

    def __hash(cls):
        # noinspection PyUnresolvedReferences
        return hash(cls.value)

    @staticmethod
    def __restrict_modification(*a, **k):
        raise TypeError(f'Enum-like classes strictly prohibit changing any attribute/property after they are once set')

    def __iter__(self):
        return iter(self._value_to_instance_map.values())

    def __setattr__(self, key, value):
        if hasattr(self, '_finalized'):
            self.__restrict_modification()
        super().__setattr__(key, value)

    def __delattr__(self, item):
        if hasattr(self, '_finalized'):
            self.__restrict_modification()
        super().__delattr__(item)

    def __getitem__(self, item):
        return getattr(self, item)

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
    def __str(cls):
        return f'{cls.__class__.__name__}.{cls.name}'

    @staticmethod
    def __repr(cls):
        return f'<{cls.__class__.__name__}.{cls.name}: {cls.value}>'
