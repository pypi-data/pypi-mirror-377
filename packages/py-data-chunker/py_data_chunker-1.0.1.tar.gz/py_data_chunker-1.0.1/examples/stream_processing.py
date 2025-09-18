#!/usr/bin/python3
# _*_ coding: utf-8 _*_
#
# Copyright (C) 2025 - 2025 anjiu, Inc. All Rights Reserved
#
# @Time    : 2025/9/18 08:45
# @Author  : anjiu
# @Email   : basui6996@gmail.com
# @File    : stream_processing.py
# @IDE     : PyCharm
# @Description: DataChunker流式处理示例

import os
import json
import tempfile

from data_chunker import DataChunker


def main():
    """流式处理示例"""
    print("=== DataChunker 流式处理示例 ===")

    # 创建临时目录用于输出
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"使用临时目录: {temp_dir}")

        # 1. 创建DataChunker实例
        chunker = DataChunker(
            chunk_size=100,
            output_dir=temp_dir,
            prefix="stream_data",
            timestamp=True
        )

        # 2. 创建流式数据生成器
        def large_data_stream():
            """模拟大型数据流"""
            for i in range(2500):
                yield {
                    "id": i,
                    "name": f"Stream_Item_{i}",
                    "value": i * 2.5,
                    "timestamp": f"2025-01-{(i % 30) + 1:02d} 10:30:00"
                }
                # 模拟数据处理延迟
                if i % 500 == 0:
                    print(f"已生成 {i} 条数据")

        print("创建流式数据生成器")

        # 3. 处理流式数据
        print("开始处理流式数据...")
        results = chunker.process_stream(large_data_stream())

        # 4. 显示结果
        print(f"流式处理完成，共生成 {len(results)} 个文件")

        # 5. 验证文件内容
        if results:
            import json
            total_records = 0
            for file_path in results:
                with open(file_path, 'r', encoding='utf-8') as f:
                    file_data = json.load(f)
                    total_records += len(file_data)
                    print(f"文件 {os.path.basename(file_path)} 包含 {len(file_data)} 条记录")

            print(f"\n总共处理了 {total_records} 条记录")

            # 验证数据完整性
            expected_records = 2500
            if total_records == expected_records:
                print("✓ 数据完整性验证通过")
            else:
                print(f"✗ 数据完整性验证失败: 期望 {expected_records}, 实际 {total_records}")


if __name__ == "__main__":
    main()
