"""
核心功能模块

包含包的主要功能函数。
"""


def hello_world(name: str = "世界") -> str:
    """
    返回一个问候语。
    
    Args:
        name (str): 要问候的名字，默认为"世界"
        
    Returns:
        str: 问候语字符串
        
    Example:
        >>> hello_world("Python")
        '你好, Python!'
    """
    return f"你好, {name}!"


def calculate_sum(a: float, b: float) -> float:
    """
    计算两个数字的和。
    
    Args:
        a (float): 第一个数字
        b (float): 第二个数字
        
    Returns:
        float: 两个数字的和
        
    Example:
        >>> calculate_sum(1.5, 2.5)
        4.0
    """
    return a + b


def calculate_product(a: float, b: float) -> float:
    """
    计算两个数字的乘积。
    
    Args:
        a (float): 第一个数字
        b (float): 第二个数字
        
    Returns:
        float: 两个数字的乘积
        
    Example:
        >>> calculate_product(3, 4)
        12.0
    """
    return a * b
