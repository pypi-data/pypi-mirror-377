#!/usr/bin/python3
# _*_ coding: utf-8 _*_
#
# Copyright (C) 2025 - 2025 anjiu, Inc. All Rights Reserved
#
# @Time    : 2025/9/18 08:45
# @Author  : anjiu
# @Email   : basui6996@gmail.com
# @File    : basic_usage.py
# @IDE     : PyCharm
# @Description: DataChunker基本使用示例

import os
import tempfile
from data_chunker import DataChunker, generate_sample_data


def main():
    """
    基本使用示例

    :return:
    """
    print("=== DataChunker 基本使用示例 ===")

    # 创建临时目录用于输出
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"使用临时目录: {temp_dir}")

        # 1. 创建DataChunker实例
        chunker = DataChunker(
            chunk_size=300,
            output_dir=temp_dir,
            prefix="data",
            timestamp=True,
            parallel=False
        )

        # 2. 生成示例数据
        data = generate_sample_data(1500)
        print(f"生成 {len(data)} 条示例数据")

        # 3. 处理数据
        print("开始处理数据...")
        results = chunker.process(data)

        # 4. 显示结果
        print(f"处理完成，共生成 {len(results)} 个文件")
        print("生成的文件:")
        for i, file_path in enumerate(results):
            print(f"  {i + 1}. {os.path.basename(file_path)}")

        # 5. 验证文件内容
        if results:
            import json
            with open(results[0], 'r', encoding='utf-8') as f:
                first_file_data = json.load(f)
                print(f"\n第一个文件包含 {len(first_file_data)} 条记录")
                print("第一条记录示例:")
                print(json.dumps(first_file_data[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
