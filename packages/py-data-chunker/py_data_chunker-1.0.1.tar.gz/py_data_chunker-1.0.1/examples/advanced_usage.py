#!/usr/bin/python3
# _*_ coding: utf-8 _*_
#
# Copyright (C) 2025 - 2025 anjiu, Inc. All Rights Reserved
#
# @Time    : 2025/9/18 08:45
# @Author  : anjiu
# @Email   : basui6996@gmail.com
# @File    : advanced_usage.py
# @IDE     : PyCharm
# @Description: DataChunker高级使用示例

import os
import json
import tempfile

from data_chunker import DataChunker


def main():
    """高级使用示例"""
    print("=== DataChunker 高级使用示例 ===")

    # 创建临时目录用于输出
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"使用临时目录: {temp_dir}")

        # 1. 创建支持并行处理的DataChunker实例
        chunker = DataChunker(
            chunk_size=200,
            output_dir=temp_dir,
            prefix="parallel_data",
            timestamp=True,
            parallel=True,
            workers=4
        )

        # 2. 创建大型数据集
        large_data = []
        for i in range(5000):
            large_data.append({
                "id": i,
                "name": f"Item_{i}",
                "category": f"Category_{i % 10}",
                "value": i * 1.5,
                "tags": [f"tag_{j}" for j in range(i % 5)]
            })

        print(f"创建 {len(large_data)} 条大型数据集")

        # 3. 处理数据
        print("开始并行处理数据...")
        results = chunker.process(large_data)

        # 4. 显示结果
        print(f"处理完成，共生成 {len(results)} 个文件")

        # 5. 动态修改配置
        print("\n动态修改配置...")
        chunker.set_config(
            chunk_size=500,
            prefix="modified_data",
            parallel=False
        )

        # 6. 使用新配置处理数据
        print("使用新配置处理数据...")
        new_results = chunker.process(large_data[:1000])  # 只处理部分数据

        print(f"新配置处理完成，生成 {len(new_results)} 个文件")

        # 7. 文件管理功能演示
        print("\n文件管理功能演示:")
        file_list = chunker.get_file_list()
        print(f"输出目录中共有 {len(file_list)} 个文件")

        # 8. 清空输出目录
        removed_count = chunker.clear_output()
        print(f"已清除 {removed_count} 个文件")
        print(f"现在输出目录中有 {len(os.listdir(temp_dir))} 个文件")


if __name__ == "__main__":
    main()
