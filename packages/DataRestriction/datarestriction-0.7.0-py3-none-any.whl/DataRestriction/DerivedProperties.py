"""
Author: Big Panda
Created Time: 24.04.2025 17:49
Modified Time: 24.04.2025 17:49
Description:
    
"""
from __future__ import annotations
from DataRestriction.BaseProperties import *
from DataRestriction.ErrorMessages import error_message

__all__ = ["PositiveIntProperty",
           "NonNegativeIntProperty",
           "PositiveFloatProperty",
           "NonNegativeFloatProperty",
           "NumberProperty",
           "PositiveNumberProperty",
           "NonNegativeNumberProperty",
           "AngleProperty",
           "FractionProperty",
           "WavelengthProperty",
           "FrequencyProperty"]


class PositiveIntProperty(IntProperty):
    def __init__(self: PositiveIntProperty, default: int = 1, doc: str = "") -> None:
        super().__init__(default=default, doc=doc)

    @IntProperty.value.setter
    def value(self: PositiveIntProperty, new_value: int) -> None:
        if not self._is_integer(new_value):
            raise ValueError(error_message["not int"])
        elif new_value > 0:
            self._value = new_value
        else:
            raise ValueError(error_message["int gt 0"])


class NonNegativeIntProperty(IntProperty):
    def __init__(self: NonNegativeIntProperty, default: int = 1, doc: str = "") -> None:
        super().__init__(default=default, doc=doc)

    @IntProperty.value.setter
    def value(self: NonNegativeIntProperty, new_value: int) -> None:
        if not self._is_integer(new_value):
            raise ValueError(error_message["not int"])
        elif new_value >= 0:
            self._value = new_value
        else:
            raise ValueError(error_message["int ge 0"])


class PositiveFloatProperty(FloatProperty):
    def __init__(self: PositiveFloatProperty, default: float = 1, doc: str = "") -> None:
        super().__init__(default=default, doc=doc)

    @FloatProperty.value.setter
    def value(self: PositiveFloatProperty, new_value: float) -> None:
        if isinstance(new_value, float):
            if new_value > 0:
                self._value = new_value
            else:
                raise ValueError(error_message["float gt 0"])
        elif isinstance(new_value, bool):
            raise ValueError(error_message["is boolean"])
        elif isinstance(new_value, int):
            raise ValueError(error_message["is int"])
        else:
            raise ValueError(error_message["not float"])


class NonNegativeFloatProperty(FloatProperty):
    def __init__(self: NonNegativeIntProperty, default: float = 1, doc: str = "") -> None:
        super().__init__(default=default, doc=doc)

    @FloatProperty.value.setter
    def value(self: NonNegativeFloatProperty, new_value: float) -> None:
        if isinstance(new_value, float):
            if new_value >= 0:
                self._value = new_value
            else:
                raise ValueError(error_message["float ge 0"])
        elif isinstance(new_value, bool):
            raise ValueError(error_message["is boolean"])
        elif isinstance(new_value, int):
            raise ValueError(error_message["is int"])
        else:
            raise ValueError(error_message["not float"])


class NumberProperty(_RationalProperty):
    ...


class PositiveNumberProperty(NumberProperty):
    def __init__(self: PositiveNumberProperty, default: int | float = 1, doc: str = "") -> None:
        super().__init__(default=default, doc=doc)

    @NumberProperty.value.setter
    def value(self: PositiveFloatProperty, new_value: int | float) -> None:
        if isinstance(new_value, (int, float)):
            if new_value > 0:
                self._value = new_value
            else:
                raise ValueError(error_message["number gt 0"])
        elif isinstance(new_value, bool):
            raise ValueError(error_message["is boolean"])
        else:
            raise ValueError(error_message["not number"])


class NonNegativeNumberProperty(NumberProperty):
    def __init__(self: NonNegativeNumberProperty, default: int | float = 1, doc: str = "") -> None:
        super().__init__(default=default, doc=doc)

    @NumberProperty.value.setter
    def value(self: NonNegativeNumberProperty, new_value: int | float) -> None:
        if isinstance(new_value, (int, float)):
            if new_value >= 0:
                self._value = new_value
            else:
                raise ValueError(error_message["number ge 0"])
        elif isinstance(new_value, bool):
            raise ValueError(error_message["is boolean"])
        else:
            raise ValueError(error_message["not number"])


class AngleProperty(_RationalProperty):
    def __init__(self: AngleProperty, default: int | float = 10, doc: str = "") -> None:
        super().__init__(default=default, doc=doc)

    @_RationalProperty.value.setter
    def value(self: AngleProperty, new_value: int | float) -> None:
        if isinstance(new_value, (float, int)):
            if 0 <= new_value <= 360:
                self._value = new_value
            else:
                raise ValueError(error_message["not in range angle"])
        elif isinstance(new_value, bool):
            raise ValueError(error_message["is boolean"])
        else:
            raise ValueError(error_message["not number"])


class FractionProperty(_RationalProperty):
    def __init__(self: FractionProperty, default: int | float = 0.5, doc: str = "") -> None:
        super().__init__(default=default, doc=doc)

    @_RationalProperty.value.setter
    def value(self: FractionProperty, new_value: int | float) -> None:
        if isinstance(new_value, (float, int)):
            if 0 <= new_value <= 1:
                self._value = new_value
            else:
                raise ValueError(error_message["not in range fraction"])
        elif isinstance(new_value, bool):
            raise ValueError(error_message["is boolean"])
        else:
            raise ValueError(error_message["not number"])


class WavelengthProperty(PositiveNumberProperty):
    ...


class FrequencyProperty(PositiveNumberProperty):
    ...


if __name__ == '__main__':
    # ==================================== Test PositiveIntProperty ====================================
    # num = PositiveIntProperty(default=1, doc="Test")
    # print(num)
    # ==================================== Test NonNegativeIntProperty ====================================
    # num = NonNegativeIntProperty(default=0, doc="Test")
    # print(num)
    # ==================================== Test NonNegativeFloatProperty ====================================
    # num = NonNegativeFloatProperty(default=-1.0, doc="Test")
    # print(num)
    # ==================================== Test NumberProperty ====================================
    # num = NumberProperty(default=1, doc="Test")
    # print(num)
    # ==================================== Test PositiveNumberProperty ====================================
    # num = PositiveNumberProperty(default=1, doc="Test")
    # print(num)
    # ==================================== Test NonNegativeNumberProperty ====================================
    # num = NonNegativeNumberProperty(default=1, doc="Test")
    # print(num)
    # ==================================== Test AngleProperty ====================================
    # num = AngleProperty(default=360, doc="Test")
    # print(num)
    # ==================================== Test FractionProperty ====================================
    # num = FractionProperty(default=1, doc="Test")
    # print(num)
    ...
