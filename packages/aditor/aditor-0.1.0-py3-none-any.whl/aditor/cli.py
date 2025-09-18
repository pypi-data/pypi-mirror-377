"""
命令行接口模块

提供命令行工具功能。
"""

import argparse
import sys
from typing import List

from .core import hello_world, calculate_sum, calculate_product


def main() -> None:
    """主函数，处理命令行参数。"""
    parser = argparse.ArgumentParser(
        description="Aditor - 一个示例Python包",
        prog="aditor"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # hello 命令
    hello_parser = subparsers.add_parser("hello", help="问候功能")
    hello_parser.add_argument(
        "name", 
        nargs="?", 
        default="世界", 
        help="要问候的名字 (默认: 世界)"
    )
    
    # calc 命令
    calc_parser = subparsers.add_parser("calc", help="数学计算功能")
    calc_parser.add_argument("operation", choices=["sum", "product"], help="计算类型")
    calc_parser.add_argument("a", type=float, help="第一个数字")
    calc_parser.add_argument("b", type=float, help="第二个数字")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if args.command == "hello":
            result = hello_world(args.name)
            print(result)
        elif args.command == "calc":
            if args.operation == "sum":
                result = calculate_sum(args.a, args.b)
                print(f"{args.a} + {args.b} = {result}")
            elif args.operation == "product":
                result = calculate_product(args.a, args.b)
                print(f"{args.a} × {args.b} = {result}")
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
