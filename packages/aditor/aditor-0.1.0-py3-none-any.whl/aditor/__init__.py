"""
我的Python包

这是一个示例Python包，用于演示如何创建和发布Python包到PyPI。
"""

__version__ = "0.1.0"
__author__ = "您的名字"
__email__ = "your.email@example.com"

from .core import hello_world, calculate_sum

__all__ = ["hello_world", "calculate_sum"]
