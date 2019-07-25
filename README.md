# fastenum
A fast Enum implementation for Python

The purpose is to replace Python3.4+ standard library Enum.

The main objective to using standard library's Enum is that it's super slow.

Features implemented:
- as in stdlib's enums all Enum members are instances of the Enum itself
```
# >>> type(LightEnum.ONE)
# <class 'LightEnum'>
```
- all enum members have at least `name` and `value` properties; the `name` property
 is a string containing the class member's name itself; the `value` property contains the value
  assigned
 ```python
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
```
- a lightweight form of enum declaration is possible
```python
class LightEnum(metaclass=FastEnum):
    ONE: 'LightEnum'
    TWO: 'LightEnum'
    THREE: 'LightEnum'
```
 When this form is used it is strictly required that members are "type-hinted"
 as instances of the enum class. Otherwise they will remain just as property/attributes
 annotations deep inside the `cls.__annotations__`
- an enum could be accessed by value
```python
# >>> LightEnum(1)
# <LightEnum.ONE: 1>
```
- or by name
```python
# >>> LightEnum['ONE']
# <LightEnum.ONE: 1>
```
- enums are singletons
```python
from pickle import dumps, loads
o = LightEnum.ONE
r = loads(dumps(o))
id(o)
# 139649196736456
id(r)
# 139649196736456
o is r
# True
```
- enums are hashable
```python
# >>> list(LightEnum)
# [<LightEnum.ONE: 1>, <LightEnum.TWO: 2>, <LightEnum.THREE: 3>]
# >>> set(LightEnum)
# {<LightEnum.ONE: 1>, <LightEnum.TWO: 2>, <LightEnum.THREE: 3>}
```
- enums are easily extended if one needs
```python
class ExtendedEnum(metaclass=FastEnum):
    description: Text
    __slots__ = ('description',)

    def __init__(self, value, description, name):
        self.value = value
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
```
 In case an enum has extended set of fields it it must be guaranteed that the `__init__`
 method has the `name` argument in the last position. It's because enum instances are
 instantiated like `enumtype(*value, name=name)` where `value` is the right side of
 assignment in the code `RED = 'red', 'a color of blood'` (in case the right side is not
 a tuple-like object it is wrapped into tuple beforehand)
- protected from modifications
```python
>>> del LightEnum.ONE
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "fastenum.py", line 81, in __delattr__
    self.__restrict_modification()
  File "fastenum.py", line 69, in __restrict_modification
    raise TypeError(f'Enum-like classes strictly prohibit changing any attribute/property after they are once set')
TypeError: Enum-like classes strictly prohibit changing any attribute/property after they are once set
>>> del LightEnum.ONE.name
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "fastenum.py", line 69, in __restrict_modification
    raise TypeError(f'Enum-like classes strictly prohibit changing any attribute/property after they are once set')
TypeError: Enum-like classes strictly prohibit changing any attribute/property after they are once set
>>> ExtendedEnum.GREEN.description = "I've changed my mind, it's a colour of swamps"
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "fastenum.py", line 69, in __restrict_modification
    raise TypeError(f'Enum-like classes strictly prohibit changing any attribute/property after they are once set')
TypeError: Enum-like classes strictly prohibit changing any attribute/property after they are once set
```
- protected from subclassing
```python
>>> class LightAlias(LightEnum):
...     pass
...
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  File "fastenum.py", line 34, in __new__
    typ.__call__ = typ.__new__ = typ.get
  File "fastenum.py", line 76, in __setattr__
    self.__restrict_modification()
  File "fastenum.py", line 69, in __restrict_modification
    raise TypeError(f'Enum-like classes strictly prohibit changing any attribute/property after they are once set')
TypeError: Enum-like classes strictly prohibit changing any attribute/property after they are once set
```
- but extensible in superclasses
```python
class ExtEnumBase(metaclass=FastEnum):
    description: Text

    __slots__ = ('description',)

    def __init__(self, value, description, name):
        self.value = value
        self.name = name
        self.description = description


class ExtEnumOne(ExtEnumBase):
    ONE = 1, 'First positive integer'
    TWO = 2, 'Second positive integer'


class ExtEnumTwo(ExtEnumBase):
    RED = 'red', 'A sunset'
    GREEN = 'green', 'Allows to cross the road'
```
- faster than standard library's one
```
In [2]: %timeit ValuesGivenEnum.FOUR
21.4 ns ± 0.196 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)

In [3]: %timeit ValuesGivenEnum.FOUR.name
30.3 ns ± 0.121 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)

In [4]: %timeit ValuesGivenEnum.FOUR.value
30.4 ns ± 0.166 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)

In [5]: %timeit ValuesGivenEnum(4)
111 ns ± 0.599 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)

In [6]: %timeit ValuesGivenEnum['FOUR']
84.6 ns ± 0.188 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)
```
 compare that to
```python
# Classic enum
from enum import Enum
class StdEnum(Enum):
    ONE = 1
    TWO = 2
```
```
In [7]: %timeit StdEnum.ONE
69.2 ns ± 0.195 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)

In [8]: %timeit StdEnum.ONE.name
247 ns ± 0.501 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)

In [9]: %timeit StdEnum.ONE.value
249 ns ± 1.43 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)

In [10]: %timeit StdEnum(1)
380 ns ± 3.74 ns per loop (mean ± std. dev. of 7 runs, 1000000 loops each)

In [11]: %timeit StdEnum['ONE']
134 ns ± 0.246 ns per loop (mean ± std. dev. of 7 runs, 10000000 loops each)
```
  That is:
   - 3 times faster on enum's member access
   - ~20 times faster on enum's property (`name`, `value`) access
   - 3 times faster on enum's access by val (call on enum's class `MyEnum(value)`)
   - 1.5 times faster on enum's access by name (dict-like `MyEnum[name]`)
