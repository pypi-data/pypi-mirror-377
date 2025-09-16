"""
Author: Big Panda
Created Time: 25.04.2025 15:52
Modified Time: 25.04.2025 15:52
Description:
    
"""
__all__ = ["error_message"]

error_message = {
    "is boolean": "The input value is a boolean type",
    "not real": "The input value is not a real number",
    "is int": "The input value is an integer type",
    "not int": "The input value is not an integer",
    "int gt 0": "The input integer should be greater than 0",
    "int ge 0": "The input integer should be greater than or equal to 0",
    "not float": "The input value is not a float",
    "float gt 0": "The input float value should be greater than 0",
    "float ge 0": "The input float value should be greater than or equal to 0",
    "not number": "The input value is not a number",
    "number gt 0": "The input number should be greater than 0",
    "number ge 0": "The input number should be greater than or equal to 0",
    "not str": "The input doc is not string type",
    "not in range": "The input value is not in range",
    "not bool": "The input value is not a bool",
    "not dict": "The input value is not a dict",
    "not in range angle": "The input value should in range [0, 360]",
    "not in range fraction": "The input value should in range [0, 1]",
    # ==================================== Coordinates error message ====================================
    "Point2D one argument": """\nThe input one arguments must be:
    Point2D(Tuple(num1 : int | float, num2 : int | float))
    Point2D(List[num1 : int | float, num2 : int | float])
    Point2D(Dict({"x" : int | float, "y" : int | float}))""",
    "Point2D two arguments": """\nThe input two arguments must be:
    Point2D(num1 : int | float, num2 : int | float)        
    Point2D(Point2D, Tuple(num1 : int | float))        
    Point2D(Point2D, List[num2 : int | float])""",
    "Point2D initialize": 'The number of input arguments should only be 0, 1, 2',
    "Point2D x not rational": "x is not a rational number",
    "Point2D y not rational": "y is not a rational number",
    "Point2D index out range": 'The index of Point2D object is out of range.',
}
