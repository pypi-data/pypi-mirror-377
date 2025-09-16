"""
Author: Big Panda
Created Time: 25.04.2025 14:09
Modified Time: 25.04.2025 14:09
Description:
    
"""


class Logger:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args, **kwargs):
        print(args)
        print(kwargs)
        print(f"调用函数 {self.func.__name__}")
        result = self.func(*args, **kwargs)
        print(f"函数 {self.func.__name__} 执行完毕")
        return result


@Logger
def add(a, b):
    return a + b


print(add(2, 3))

# class Repeat:
#     def __init__(self, times):
#         self.times = times
#
#     def __call__(self, func):
#         def hhhh(*args, **kwargs):
#             for _ in range(self.times):
#                 result = func(*args, **kwargs)
#             return result
#
#         return hhhh
#
#
# @Repeat(times=3)
# def greet(name):
#     print(f"Hello, {name}!")

