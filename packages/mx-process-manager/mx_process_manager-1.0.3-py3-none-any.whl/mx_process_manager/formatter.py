# -*- coding: utf-8 -*-
from typing import Optional

def formatNumberWithUnits(number: float | int, units: list[tuple[int,str,str]], unit_limit: Optional[int] = None) -> str:
    """
    按照数字和数字的多级单位来格式化为字符串。

    参数:
        number (float | int): 要格式化的数字，可以是浮点数或整数。
        units (list[tuple[int, str, str]]): 单位列表，每个单位由一个元组表示，包含因子和单位字符串，最后是格式化，如(60, "分钟", "02d")。
        unit_limit (int, 可选): 从最大单位开始算，最多显示多少个单位。

    返回:
        str: 格式化后的字符串，包含数字和单位。

    注意:
        - 如果 `number` 是浮点数，会将其整数部分和小数部分分开处理。
        - `units` 列表中的因子为 -1 时，用于处理小数部分。
        - 格式化结果会根据单位列表依次递减处理，直到数字完全转换为单位表示。
    """
    formatted_strs = []
    decimal_part = None
    remainder = number
    if isinstance(number, float):
        if not units[0][2] or not units[0][2].startswith('.'):
           raise ValueError("The first unit must be a decimal format for float numbers, or use int() case to integer.")
        remainder = int(number)
        decimal_part = number - remainder
    
    for idx, (factor, unit, format) in enumerate(units):
        format = format if format else ""
        if not formatted_strs and decimal_part is not None:
            formatted_strs.append(f"{decimal_part:{format}}{unit}"[2:])  # 去掉前面的0.
            continue
        if remainder > factor:
            remainder, unit_num = divmod(remainder, factor)
            formatted_strs.append(f"{unit_num:{format}}{unit}")
        else:
            formatted_strs.append(f"{remainder:{format}}{unit}")
            break
    formatted_strs.reverse()
    return "".join(formatted_strs[:unit_limit] if unit_limit is not None else formatted_strs)

class Example:
    units: list[tuple[int, str, str]]
    unit_limit: Optional[int] = None

    def __init__(self, units: list[tuple[int, str, str]], unit_limit: Optional[int] = None):
        """
        初始化一个示例对象。

        参数:
            units (list[tuple[int, str, str]]): 单位列表，每个单位由一个元组表示，包含因子、单位字符串和格式化字符串。
            unit_limit (Optional[int]): 可选的单位限制，指定最多显示多少个单位。
        """
        self.units = units
        self.unit_limit = unit_limit

    def build(self, units: Optional[list[tuple[int, str, str]]] = None, unit_limit: Optional[int] = None):
        units = units or self.units
        unit_limit = unit_limit or self.unit_limit
        return Example(units, unit_limit)

def formatWithExample(number: float | int, example: Example):
    return formatNumberWithUnits(number, example.units, example.unit_limit)

EXAMPLE_DAYS_WITH_MILLISECONDS = Example([(1000, '毫秒', '.3f'), (60, '.', '02d'), (60, ':', '02d'), (60, ':', '02d'), (24, '天 ', '')], 3)
EXAMPLE_DAYS_WITH_SECONDS = Example([(60, '.', '02d'), (60, ':', '02d'), (60, ':', '02d'), (24, '天 ', '')], 3)
EXAMPLE_BYTES_SIZE = Example([(1024, 'B', ''), (1024, 'K', ''), (1024, 'M', ''), (1024, 'G', ''), (1024, 'T', '')], 2)
EXAMPLE_DURATION_TIME = Example([(60, '秒', '02d'), (60, '分', '02d'), (60, '时', '02d'), (24, '天 ', '')], 3)
