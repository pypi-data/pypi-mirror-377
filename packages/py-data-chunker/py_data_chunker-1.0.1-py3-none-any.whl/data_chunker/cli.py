#!/usr/bin/python3
# _*_ coding: utf-8 _*_
#
# Copyright (C) 2025 - 2025 anjiu, Inc. All Rights Reserved
#
# @Time    : 2025/9/18 08:45
# @Author  : anjiu
# @Email   : basui6996@gmail.com
# @File    : cli.py
# @IDE     : PyCharm
# @Description: DataChunker命令行接口

import sys
import json
import argparse

from .core import DataChunker
from .utils import read_json_file, json_stream_reader


def main():
    """
    命令行主函数

    :return:
    """
    parser = argparse.ArgumentParser(description="数据分块处理工具")

    # 添加参数
    parser.add_argument("input", help="输入JSON文件路径")
    parser.add_argument("-o", "--output", default="output", help="输出目录")
    parser.add_argument("-s", "--chunk-size", type=int, default=500, help="分块大小")
    parser.add_argument("-p", "--prefix", default="chunk", help="文件前缀")
    parser.add_argument("--no-timestamp", action="store_false", dest="timestamp",
                        help="不在文件名中添加时间戳")
    parser.add_argument("--parallel", action="store_true", help="使用并行处理")
    parser.add_argument("-w", "--workers", type=int, default=4, help="工作线程数")

    # 解析参数
    args = parser.parse_args()

    try:
        # 创建分块处理器
        chunker = DataChunker(
            chunk_size=args.chunk_size,
            output_dir=args.output,
            prefix=args.prefix,
            timestamp=args.timestamp,
            parallel=args.parallel,
            workers=args.workers
        )

        # 读取输入数据
        if args.input.endswith('.json'):
            data = read_json_file(args.input)
            results = chunker.process(data)
        else:
            # 假设是其他格式，尝试逐行读取
            results = chunker.process_stream(json_stream_reader(args.input))

        print(f"处理完成，共保存 {len(results)} 个文件")
        print(f"输出目录: {args.output}")

    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
