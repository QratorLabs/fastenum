import pickle
from typing import Text
from unittest import TestCase

from fast_enum import FastEnum


class FastEnumTestCase(TestCase):
    def test_01_value_provided_enum(self):
        """
        Test standard (value-provided) functionality
        """
        global StdEnum
        class StdEnum(metaclass=FastEnum):
            ONE = 1
            TWO = 2
            THREE = 3
            ALIAS_THREE = 3

        self.assertIsInstance(StdEnum.ONE, StdEnum)
        self.assertIsInstance(StdEnum.TWO, StdEnum)
        self.assertIsInstance(StdEnum.THREE, StdEnum)
        self.assertIs(StdEnum.ALIAS_THREE, StdEnum.THREE)

        one = pickle.loads(pickle.dumps(StdEnum.ONE))
        self.assertIs(one, StdEnum.ONE)

        self.assertEqual(StdEnum.ONE.name, 'ONE')
        self.assertEqual(StdEnum.ONE.value, 1)
        self.assertEqual(StdEnum.TWO.name, 'TWO')
        self.assertEqual(StdEnum.TWO.value, 2)
        self.assertEqual(StdEnum.THREE.name, 'THREE')
        self.assertEqual(StdEnum.THREE.value, 3)
        self.assertEqual(StdEnum.ALIAS_THREE.name, 'THREE')
        self.assertEqual(StdEnum.ALIAS_THREE.value, 3)

        self.assertIs(StdEnum(1), StdEnum.ONE)
        self.assertIs(StdEnum(2), StdEnum.TWO)
        self.assertIs(StdEnum(3), StdEnum.THREE)

        self.assertIs(StdEnum['ONE'], StdEnum.ONE)
        self.assertIs(StdEnum['TWO'], StdEnum.TWO)
        self.assertIs(StdEnum['THREE'], StdEnum.THREE)
        self.assertIs(StdEnum['ALIAS_THREE'], StdEnum.THREE)

        self.assertListEqual(list(StdEnum), [StdEnum.ONE, StdEnum.TWO, StdEnum.THREE])

        self.assertSetEqual(set(StdEnum), {StdEnum.ONE, StdEnum.TWO, StdEnum.THREE})

    def test_02_lightweight(self):
        """
        Test lightweight (auto-valued) form
        """
        class LightEnumOne(metaclass=FastEnum):
            ONE: 'LightEnumOne'
            TWO: 'LightEnumOne'

        class LightEnumZero(metaclass=FastEnum):
            _ZERO_VALUED = True
            ZERO: 'LightEnumZero'
            ONE: 'LightEnumZero'

        self.assertEqual(LightEnumOne.ONE.value, 1)
        self.assertEqual(LightEnumOne.TWO.value, 2)

        self.assertEqual(LightEnumZero.ZERO.value, 0)
        self.assertEqual(LightEnumZero.ONE.value, 1)

    def test_03_mixed(self):
        """
        Test a mixed (auto-valued and value-provided) forms mixed in the same class
        """
        class MixedEnum(metaclass=FastEnum):
            _ZERO_VALUED = True

            ONE = 1
            AUTO_ZERO: 'MixedEnum'
            TWO = 2
            AUTO_ONE: 'MixedEnum'

        self.assertEqual(MixedEnum.ONE.value, 1)
        self.assertEqual(MixedEnum.TWO.value, 2)
        self.assertEqual(MixedEnum.AUTO_ZERO.value, 0)
        self.assertEqual(MixedEnum.AUTO_ONE.value, 1)
        self.assertIs(MixedEnum.AUTO_ONE, MixedEnum.ONE)
        self.assertIs(MixedEnum['AUTO_ONE'], MixedEnum.ONE)

    def test_04_baseclass(self):
        """
        Test functionality of subclassed enums
        """
        class EnumBase(metaclass=FastEnum):
            __slots__ = ('desc',)
            desc: 'Text'
            def __init__(self, value, desc, name):
                self.value = value
                self.name = name
                self.desc = desc

        class SubEnumOrder(EnumBase):
            ONE = 1, 'First'
            TWO = 2, 'Second'

        class SubEnumCount(EnumBase):
            ONE = 1, 'One'
            TWO = 2, 'Two'

        self.assertEqual(SubEnumOrder.ONE.desc, 'First')
        self.assertEqual(SubEnumOrder.TWO.desc, 'Second')

        self.assertEqual(SubEnumCount.ONE.desc, 'One')
        self.assertEqual(SubEnumCount.TWO.desc, 'Two')

    def test_05_late_init(self):
        """
        Test late-init hooking
        """
        class HookedEnum(metaclass=FastEnum):
            halved_value: 'HookedEnum'
            __slots__ = ('halved_value',)
            def __init_late(self):
                self.halved_value: 'HookedEnum' = self.__class__(self.value // 2)

            ZERO: 'HookedEnum' = 0
            ONE: 'HookedEnum' = 1
            TWO: 'HookedEnum' = 2
            THREE: 'HookedEnum' = 3

        self.assertIs(HookedEnum.ZERO.halved_value, HookedEnum.ZERO)
        self.assertIs(HookedEnum.ONE.halved_value, HookedEnum.ZERO)
        self.assertIs(HookedEnum.TWO.halved_value, HookedEnum.ONE)
        self.assertIs(HookedEnum.THREE.halved_value, HookedEnum.ONE)

    def test_06_restrict_subclassing(self):
        """
        Test if subclassing is restricted
        """
        with self.assertRaises(TypeError):
            class SuperEnum(metaclass=FastEnum):
                ONE: 'SuperEnum'
                TWO: 'SuperEnum'

            class SubEnum(SuperEnum):
                FOUR = 4

    def test_07_restrict_modifications(self):
        """
        Test if enum is protected from any modification
        """
        class RestrictEnum(metaclass=FastEnum):
            ONE = 1
            TWO = 2

        with self.assertRaises(TypeError):
            setattr(RestrictEnum.ONE, 'value', 5)
        with self.assertRaises(TypeError):
            delattr(RestrictEnum.TWO, 'name')
