"""
Author: Big Panda
Created Time: 25.04.2025 14:38
Modified Time: 25.04.2025 14:38
Description:
    The structure of number:
        1. real number:
            {1}. Rational numbers: in computer, the rational number can be regarded same as real number
                [1]. Integers:
                    1). Whole numbers:
                        One. Natural / Counting Numbers:
                [2]. Float numbers(Fractional nuber)
           {2}: Irrational numbers:
        2. imaginary number: Complex number

    Real number: RealProperty
    Rational number: RationalProperty
    Integer: IntProperty
    Float: FloatProperty
"""
from __future__ import annotations
from DataRestriction.ErrorMessages import error_message
import math
import numpy as np

__all__ = ["_RationalProperty",
           "IntProperty",
           "FloatProperty",
           "StringProperty",
           "BoolProperty",
           "DictProperty",
           "LockedProperty",
           "Coord2DProperty"]


class _RealProperty:
    _value: int | float
    _doc: str

    def __init__(self: _RealProperty, default: int | float = 1.0, doc: str = "") -> None:
        self.value: int = default
        self.doc: str = doc

    @property
    def value(self: _RealProperty) -> int | float:
        return self._value

    @value.setter
    def value(self: _RealProperty, new_value: int | float) -> None:
        if isinstance(new_value, (int, float)):
            self._value = new_value
        elif isinstance(new_value, bool):
            raise ValueError(error_message["is boolean"])
        else:
            raise ValueError(error_message["not real"])

    @property
    def doc(self: _RealProperty) -> str:
        return self._doc

    @doc.setter
    def doc(self: _RealProperty, new_doc: str) -> None:
        if not isinstance(new_doc, str):
            raise ValueError(error_message["not string"])
        self._doc = new_doc

    def __repr__(self: _RealProperty) -> str:
        return str(self._value)

    def __str__(self: _RealProperty) -> str:
        return str(self._value)

    def __int__(self: _RealProperty) -> int:
        return int(self._value)

    def __float__(self: _RealProperty) -> float:
        return float(self._value)

    def __complex__(self: _RealProperty) -> complex:
        return complex(self._value)

    def __index__(self: _RealProperty) -> int | float:
        return self._value

    def __round__(self: _RealProperty, n: int) -> int | float:
        return round(self._value, n)

    def __trunc__(self: _RealProperty) -> int:
        return math.trunc(self._value)

    def __floor__(self: _RealProperty) -> int:
        return math.floor(self._value)

    def __ceil__(self: _RealProperty) -> int:
        return math.ceil(self._value)

    def __add__(self: _RealProperty, other: int | float):
        return self._value + other

    def __sub__(self: _RealProperty, other: int | float):
        return self._value - other

    def __mul__(self: _RealProperty, other: int | float):
        return self._value * other

    def __truediv__(self: _RealProperty, other: int | float):
        return self._value / other

    def __floordiv__(self: _RealProperty, other: int | float):
        return self._value // other

    def __mod__(self: _RealProperty, other: int | float):
        return self._value % other

    def __abs__(self: _RealProperty) -> int | float:
        return abs(self._value)

    def __invert__(self: _RealProperty) -> int | float:
        return ~self._value

    def __pow__(self: _RealProperty, other: int | float):
        return self._value ** other

    def __lt__(self: _RealProperty, other: int | float):
        return self._value < other

    def __le__(self: _RealProperty, other: int | float):
        return self._value <= other

    def __eq__(self: _RealProperty, other: int | float):
        return self._value == other

    def __ne__(self: _RealProperty, other: int | float):
        return self._value != other

    def __gt__(self: _RealProperty, other: int | float):
        return self._value > other

    def __ge__(self: _RealProperty, other: int | float):
        return self._value >= other

    def __hash__(self: _RealProperty) -> hash:
        return hash(self._value)

    def __iadd__(self: _RealProperty, other: int | float):
        return self._value + other

    def __isub__(self: _RealProperty, other: int | float):
        return self._value - other

    def __imul__(self: _RealProperty, other: int | float):
        return self._value * other

    def __itruediv__(self: _RealProperty, other: int | float):
        return self._value / other

    def __ifloordiv__(self: _RealProperty, other: int | float):
        return self._value / other

    def __imod__(self: _RealProperty, other: int | float):
        return self._value // other

    def __ipow__(self: _RealProperty, other: int | float):
        return self._value ** other


class _RationalProperty(_RealProperty):
    ...


class IntProperty(_RationalProperty):
    _value: int
    _doc: str

    def __init__(self: IntProperty, default: int = 1, doc: str = "") -> None:
        super().__init__(default=default, doc=doc)

    @property
    def value(self: IntProperty) -> int:
        return self._value

    @value.setter
    def value(self: IntProperty, new_value: int) -> None:
        if not self._is_integer(new_value):
            raise ValueError(error_message["not int"])
        self._value = new_value

    @staticmethod
    def _is_integer(value: int) -> bool:
        if isinstance(value, bool):
            raise ValueError(error_message["is boolean"])
        return isinstance(value, int)

        # For strict data type, we do not need to consider the situation below.
        # (isinstance(value, float) and value.is_integer() and not isinstance(value, bool)))


class FloatProperty(_RationalProperty):
    _value: float
    _doc: str

    def __init__(self: FloatProperty, default: float = 1.0, doc: str = "") -> None:
        super().__init__(default=default, doc=doc)

    @property
    def value(self: FloatProperty) -> float:
        return self._value

    @value.setter
    def value(self: FloatProperty, new_value: float) -> None:
        if isinstance(new_value, float):
            self._value = new_value
        elif isinstance(new_value, bool):
            raise ValueError(error_message["is boolean"])
        elif isinstance(new_value, int):
            raise ValueError(error_message["is int"])
        else:
            raise ValueError(error_message["not float"])


class StringProperty:
    _value: str
    _doc: str

    def __init__(self: StringProperty, default: str = "", doc: str = "") -> None:
        self.value: str = default
        self.doc: str = doc

    @property
    def value(self: StringProperty) -> str:
        return self._value

    @value.setter
    def value(self: StringProperty, new_value: str) -> None:
        if not isinstance(new_value, str):
            raise ValueError(error_message["not str"])
        self._value = new_value

    @property
    def doc(self: StringProperty) -> str:
        return self._doc

    @doc.setter
    def doc(self: StringProperty, new_doc: str) -> None:
        if not isinstance(new_doc, str):
            raise ValueError(error_message["not string"])
        self._doc = new_doc

    def __repr__(self: StringProperty) -> str:
        return str(self._value)

    def __str__(self: StringProperty) -> str:
        return str(self._value)


class BoolProperty:
    _value: bool
    _doc: str

    def __init__(self: BoolProperty, default: bool = True, doc: str = "") -> None:
        self.value: bool = default
        self.doc: str = doc

    @property
    def value(self: BoolProperty) -> bool:
        return self._value

    @value.setter
    def value(self: BoolProperty, new_value: bool) -> None:
        if not isinstance(new_value, bool):
            raise ValueError(error_message["not bool"])
        self._value = new_value

    @property
    def doc(self: BoolProperty) -> str:
        return self._doc

    @doc.setter
    def doc(self: BoolProperty, new_doc: str) -> None:
        if not isinstance(new_doc, str):
            raise ValueError(error_message["not string"])
        self._doc = new_doc

    def __repr__(self: BoolProperty) -> str:
        return str(self._value)

    def __str__(self: BoolProperty) -> str:
        return str(self._value)


class DictProperty:
    _value: dict
    _doc: str

    def __init__(self: DictProperty, default: dict | None = None, doc: str = "") -> None:
        if default is None:
            default = {1: 1}
        self.value: dict = default
        self.doc: str = doc

    @property
    def value(self: DictProperty) -> dict:
        return self._value

    @value.setter
    def value(self: DictProperty, new_value: dict) -> None:
        if not isinstance(new_value, dict):
            raise ValueError(error_message["not dict"])
        self._value = new_value

    @property
    def doc(self: DictProperty) -> str:
        return self._doc

    @doc.setter
    def doc(self: DictProperty, new_doc: str) -> None:
        if not isinstance(new_doc, str):
            raise ValueError(error_message["not string"])
        self._doc = new_doc

    def __repr__(self: DictProperty) -> str:
        return str(self._value)

    def __str__(self: DictProperty) -> str:
        return str(self._value)


class LockedProperty:
    _value: int | float | str | dict
    _doc: str

    def __init__(self: LockedProperty, default: int | float | str | dict = 1, doc: str = "") -> None:
        self._value: dict = default
        self.doc: str = doc

    @property
    def value(self: LockedProperty) -> int | float | str | dict:
        return self._value

    @property
    def doc(self: LockedProperty) -> str:
        return self._doc

    @doc.setter
    def doc(self: LockedProperty, new_doc: str) -> None:
        if not isinstance(new_doc, str):
            raise ValueError(error_message["not string"])
        self._doc = new_doc

    def __repr__(self: LockedProperty) -> str:
        return str(self._value)

    def __str__(self: LockedProperty) -> str:
        return str(self._value)


class _Point2D:
    _x: int | float = 0
    _y: int | float = 0
    _doc: str

    def __init__(self: _Point2D, *args) -> None:
        """
        Define two methods for initializing Point2D
            1. point = Points2D((x, y))
            2. point = Points2D([x, y])
            3. point = Points2D({'x' : x, 'y' : y})
            4. point = Points2D(x, y)
            5. point = Points2D(Points2D(x, y), (offset_x, offset_y))
            6. point = Points2D(Points2D(x, y), [offset_x, offset_y])
        """
        if len(args) == 0:
            pass
        elif len(args) == 1:
            arg = args[0]
            if isinstance(arg, (tuple, list)) and len(arg) == 2:
                self.x, self.y = arg
            elif isinstance(arg, dict):
                self.x = arg.get('x', 0.0)
                self.y = arg.get('y', 0.0)
            else:
                raise ValueError(error_message["Point2D one argument"])
        elif len(args) == 2:
            if isinstance(args[0], (int, float)) and isinstance(args[1], (int, float)):
                self.x, self.y = args
            elif isinstance(args[0], _Point2D) and isinstance(args[1], (tuple, list)) and len(args[1]) == 2:
                self.x, self.y = args[0].x + args[1][0], args[0].y + args[1][1]
            else:
                raise ValueError(error_message["Point2D two arguments"])
        else:
            raise ValueError(error_message["Point2D initialize"])

    @property
    def x(self):
        return self._x

    @x.setter
    def x(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(error_message["Point2D x not rational"])
        self._x = value

    @property
    def y(self):
        return self._y

    @y.setter
    def y(self, value):
        if not isinstance(value, (int, float)):
            raise TypeError(error_message["Point2D y not rational"])
        self._y = value

    # String representation of Point2D
    def __str__(self: _Point2D) -> str:
        return f"Point2D{self.x, self.y}"

    def __repr__(self: _Point2D) -> str:
        return f"Point2D{self.x, self.y}"

    # Override setitem method
    def __setitem__(self: _Point2D, key: int, value: int | float) -> None:
        if key == 0:
            self.x: int | float = value
        elif key == 1:
            self.y: int | float = value
        else:
            raise ValueError(error_message["Point2D index out range"])

    # Override getitem method
    def __getitem__(self: _Point2D, key: int) -> float:
        if key == 0:
            return self.x
        elif key == 1:
            return self.y
        else:
            raise ValueError('The index of Point2D object is out of range.')

    def __iter__(self: _Point2D) -> iter(_Point2D):
        return iter([self.x, self.y])

    def __copy__(self: _Point2D) -> _Point2D:
        return _Point2D(self.x, self.y)

    def __neg__(self: _Point2D) -> _Point2D:
        return _Point2D(-self.x, -self.y)

    def __abs__(self: _Point2D) -> _Point2D:
        """
        Get absolute point coordinates of current one. In first Quadrant.
        """
        return _Point2D(abs(self.x), abs(self.y))

    def __add__(self: _Point2D, other: _Point2D) -> _Point2D:
        """
        Point2D operation ------ Adding
        """
        return _Point2D(self.x + other.x, self.y + other.y)

    def __sub__(self: _Point2D, other: _Point2D) -> _Point2D:
        """
        Point2D operation ------ Subtraction
        """
        return _Point2D(self.x - other.x, self.y - other.y)

    # ================================================= Specific function =================================================
    def tolist(self):
        return [self.x, self.y]

    def index(self: _Point2D, num: int | float) -> int:
        """
        Return the index of coordinate equals to num
        :param num: reference number
        :return: 0 for x, 1 for y, -1 for no one
        """
        indices = [index for index, value in enumerate(self) if value == num]
        return indices[0] if indices else -1

    def index01(self: _Point2D, other: _Point2D) -> int:
        """
        Return the index of coordinate of point 1 equals to point 2
        :param other: reference point
        :return: 0 for x, 1 for y, -1 for no one
        """
        # ----------- Method 1 -----------
        # indices = [index for index, (value1, value2) in enumerate(zip(self, point)) if value1 == value2]
        # indices[0] if indices else -1
        # ----------- Method 2 -----------
        return (self - other).index(0)

    def symmetry_about_x(self: _Point2D):
        symmetry_matrix = np.array([[1, 0],
                                    [0, -1]])

        return symmetry_matrix @ self

    def symmetry_about_y(self: _Point2D):
        symmetry_matrix = np.array([[-1, 0],
                                    [0, 1]])

        return symmetry_matrix @ self

    def symmetry_about_origin(self: _Point2D):
        symmetry_matrix = np.array([[-1, 0],
                                    [0, -1]])

        return symmetry_matrix @ self

    def symmetry_about_y_equal_x(self: _Point2D):
        symmetry_matrix = np.array([[0, 1],
                                    [1, 0]])

        return symmetry_matrix @ self

    def symmetry_about_y_equal_minus_x(self: _Point2D):
        symmetry_matrix = np.array([[0, -1],
                                    [-1, 0]])

        return symmetry_matrix @ self

    def symmetry_about_x_parallel(self: _Point2D, axis: int | float = 0.0):
        """
        Symmetric about y-axis, which y does not equal to zero. Here, the value of axis ！= 0

        Steps:
        1. Subtract 1 from x-coordinates
        2. Switch sign of x-coordinates
        3. Add 1 to x-coordinates
        :param point: the point or vector we deal with, normally a 2d vector
        :param axis: the symmetric axis
        :return: point after symmetry
        """
        translate_matrix_1 = np.array([[1, 0, 0],
                                       [0, 1, -axis],
                                       [0, 0, 1]])
        symmetry_matrix = np.array([[1, 0, 0],
                                    [0, -1, 0],
                                    [0, 0, 1]])
        translate_matrix_2 = np.array([[1, 0, 0],
                                       [0, 1, axis],
                                       [0, 0, 1]])

        point_3d = np.ones((3, 1), dtype=np.float64)
        point_3d[0:-1, 0] = np.array(self.tolist())
        new_point_3d = translate_matrix_2 @ symmetry_matrix @ translate_matrix_1 @ point_3d

        return _Point2D(new_point_3d[:-1, 0].tolist())

    def symmetry_about_y_parallel(self: _Point2D, axis: int | float = 0.0):
        """
        Symmetric about y-axis, which y does not equal to zero. Here, the value of axis ！= 0
        :param point:
        :param axis:
        :return:
        """
        translate_matrix_1 = np.array([[1, 0, -axis],
                                       [0, 1, 0],
                                       [0, 0, 1]])
        symmetry_matrix = np.array([[-1, 0, 0],
                                    [0, 1, 0],
                                    [0, 0, 1]])
        translate_matrix_2 = np.array([[1, 0, axis],
                                       [0, 1, 0],
                                       [0, 0, 1]])
        point_3d = np.ones((3, 1), dtype=np.float64)
        point_3d[0:-1, 0] = np.array(self.tolist())
        new_point_3d = translate_matrix_2 @ symmetry_matrix @ translate_matrix_1 @ point_3d

        return _Point2D(new_point_3d[:-1, 0].tolist())


class Coord2DProperty(_Point2D):
    ...


if __name__ == '__main__':
    # ==================================== Test _RealProperty ====================================
    # obj = _RealProperty(default=1.0)
    # print(obj)
    # ==================================== Test IntProperty ====================================
    # obj = IntProperty(default=1)
    # print(obj)
    # ==================================== Test FloatProperty ====================================
    # obj = FloatProperty(default=1.0)
    # print(obj)
    # ==================================== Test StringProperty ====================================
    # obj = StringProperty(default="1")
    # print(obj)
    # ==================================== Test BoolProperty ====================================
    # obj = BoolProperty()
    # print(obj)
    # ==================================== Test DictProperty ====================================
    obj = DictProperty(default={1: 1, 2: 2})
    print(obj)
    # ==================================== Test Point2D ====================================
    # p = _Point2D(1, 2)
    # print(p)
    ...
