from typing import Text

from fastenum_meta import FastEnum


class LightEnum(metaclass=FastEnum):
    ONE: 'LightEnum'
    TWO: 'LightEnum'
    THREE: 'LightEnum'
# >>> LightEnum.ONE
# <LightEnum.ONE: 1>
# >>> str(LightEnum.ONE)
# 'LightEnum.ONE'
# >>> LightEnum.ONE.name
# 'ONE'
# >>> LightEnum.ONE.value
# 1
# >>> LightEnum(1)
# <LightEnum.ONE: 1>
# >>> LightEnum['ONE']
# <LightEnum.ONE: 1>
# >>> list(LightEnum)
# [<LightEnum.ONE: 1>, <LightEnum.TWO: 2>, <LightEnum.THREE: 3>]
# >>> set(LightEnum)
# {<LightEnum.ONE: 1>, <LightEnum.TWO: 2>, <LightEnum.THREE: 3>}
# >>> type(LightEnum.ONE)
# <class 'LightEnum'>


class ValuesGivenEnum(metaclass=FastEnum):
    ONE: 'ValuesGivenEnum' = 1
    FOUR: 'ValuesGivenEnum' = 4
    ELEVEN: 'ValuesGivenEnum' = 11
# >>> ValuesGivenEnum.FOUR
# <ValuesGivenEnum.FOUR: 4>
# >>> ValuesGivenEnum.FOUR.value
# 4
# >>> ValuesGivenEnum.FOUR.name
# 'FOUR'
# >>> ValuesGivenEnum.ELEVEN
# <ValuesGivenEnum.ELEVEN: 11>
# >>> list(ValuesGivenEnum)
# [<ValuesGivenEnum.ONE: 1>, <ValuesGivenEnum.FOUR: 4>, <ValuesGivenEnum.ELEVEN: 11>]


class ExtendedEnum(metaclass=FastEnum):
    description: Text
    __slots__ = ('description',)

    def __init__(self, value, description, name):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        self.value = value
        # noinspection PyDunderSlots,PyUnresolvedReferences
        self.name = name
        self.description = description

    def describe(self):
        return self.description

    RED = 'red', 'a color of blood'
    GREEN = 'green', 'a color of grass in the spring'
# >>> ExtendedEnum.GREEN
# <ExtendedEnum.GREEN: green>
# >>> str(ExtendedEnum.GREEN)
# 'ExtendedEnum.GREEN'
# >>> ExtendedEnum.GREEN.name
# 'GREEN'
# >>> ExtendedEnum.GREEN.value
# 'green'
# >>> ExtendedEnum.GREEN.description
# 'a color of grass in the spring'
# >>> ExtendedEnum.GREEN.describe()
# 'a color of grass in the spring'

# PROTECTION
# >>> ExtendedEnum.GREEN.description = "I've changed my mind, it's a colour of swamps"
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "fastenum.py", line 69, in __restrict_modification
#     raise TypeError(f'Enum-like classes strictly prohibit changing any attribute/property after they are once set')
# TypeError: Enum-like classes strictly prohibit changing any attribute/property after they are once set
# >>> class LightAlias(LightEnum):
# ...     pass
# ...
# Traceback (most recent call last):
#   File "<stdin>", line 1, in <module>
#   File "fastenum.py", line 34, in __new__
#     typ.__call__ = typ.__new__ = typ.get
#   File "fastenum.py", line 76, in __setattr__
#     self.__restrict_modification()
#   File "fastenum.py", line 69, in __restrict_modification
#     raise TypeError(f'Enum-like classes strictly prohibit changing any attribute/property after they are once set')
# TypeError: Enum-like classes strictly prohibit changing any attribute/property after they are once set


class ExtEnumBase(metaclass=FastEnum):
    description: Text

    __slots__ = ('description',)

    def __init__(self, value, description, name):
        # noinspection PyDunderSlots,PyUnresolvedReferences
        self.value = value
        # noinspection PyDunderSlots,PyUnresolvedReferences
        self.name = name
        self.description = description


class ExtEnumOne(ExtEnumBase):
    ONE = 1, 'First positive integer'
    TWO = 2, 'Second positive integer'


class ExtEnumTwo(ExtEnumBase):
    RED = 'red', 'A sunset'
    GREEN = 'green', 'Allows to cross the road'


class MixedEnum(metaclass=FastEnum):
    _ZERO_VALUED = True
    AUTO_ZERO: 'MixedEnum'
    ONE: 'MixedEnum' = 1
    AUTO_ONE: 'MixedEnum'
    TWO: 'MixedEnum' = 2

# >>> MixedEnum(1)
# <MixedEnum.ONE: 1>
# >>> MixedEnum.AUTO_ZERO
# <MixedEnum.AUTO_ZERO: 0>
# >>> MixedEnum.AUTO_ONE
# <MixedEnum.ONE: 1>


class HookedEnum(metaclass=FastEnum):
    halved_value: 'HookedEnum'

    __slots__ = ('halved_value',)

    def __init_late(self):
        # noinspection PyTypeChecker
        self.halved_value: 'HookedEnum' = self.__class__(self.value // 2)

    ZERO: 'HookedEnum' = 0
    ONE: 'HookedEnum' = 1
    TWO: 'HookedEnum' = 2
    THREE: 'HookedEnum' = 3

# >>> HookedEnum.ZERO.halved_value
# <HookedEnum.ZERO: 0>
# >>> HookedEnum.ONE.halved_value
# <HookedEnum.ZERO: 0>
# >>> HookedEnum.TWO.halved_value
# <HookedEnum.ONE: 1>
# >>> HookedEnum.THREE.halved_value
# <HookedEnum.ONE: 1>
