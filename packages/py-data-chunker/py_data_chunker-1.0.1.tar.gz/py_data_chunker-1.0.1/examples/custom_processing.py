#!/usr/bin/python3
# _*_ coding: utf-8 _*_
#
# Copyright (C) 2025 - 2025 anjiu, Inc. All Rights Reserved
#
# @Time    : 2025/9/18 08:45
# @Author  : anjiu
# @Email   : basui6996@gmail.com
# @File    : custom_processing.py
# @IDE     : PyCharm
# @Description: DataChunker自定义处理示例

import os
import tempfile
from datetime import datetime
from data_chunker import DataChunker


class CustomDataChunker(DataChunker):
    """自定义DataChunker，添加数据处理逻辑"""

    def _process_chunk(self, chunk, chunk_index):
        """
        重写处理分块方法，添加自定义逻辑

        :param chunk: 数据分块
        :param chunk_index: 分块索引
        :return: 保存的文件路径
        """
        # 1. 数据增强：添加处理时间和状态
        process_time = datetime.now().isoformat()
        for item in chunk:
            item["processed"] = True
            item["process_time"] = process_time
            item["process_id"] = f"PID_{chunk_index:04d}"

            # 2. 数据验证：确保必要字段存在
            if "id" not in item:
                item["id"] = f"auto_{chunk_index}_{hash(str(item))}"

            # 3. 数据转换：将数值字段转换为特定格式
            if "value" in item and isinstance(item["value"], (int, float)):
                item["value_formatted"] = f"${item['value']:,.2f}"

        # 4. 调用父类方法保存处理后的数据
        return super()._process_chunk(chunk, chunk_index)


def main():
    """自定义处理示例"""
    print("=== DataChunker 自定义处理示例 ===")

    # 创建临时目录用于输出
    with tempfile.TemporaryDirectory() as temp_dir:
        print(f"使用临时目录: {temp_dir}")

        # 1. 创建自定义DataChunker实例
        chunker = CustomDataChunker(
            chunk_size=150,
            output_dir=temp_dir,
            prefix="custom_data",
            timestamp=True
        )

        # 2. 创建测试数据（包含一些不完整的数据）
        test_data = []
        for i in range(800):
            if i % 10 == 0:
                # 每10条数据中有一条缺少id字段
                test_data.append({
                    "name": f"Partial_Item_{i}",
                    "value": i * 7.3
                })
            else:
                test_data.append({
                    "id": i,
                    "name": f"Complete_Item_{i}",
                    "value": i * 7.3,
                    "category": f"Cat_{i % 5}"
                })

        print(f"创建 {len(test_data)} 条测试数据（包含不完整数据）")

        # 3. 处理数据
        print("开始处理数据（包含自定义处理逻辑）...")
        results = chunker.process(test_data)

        # 4. 显示结果
        print(f"处理完成，共生成 {len(results)} 个文件")

        # 5. 验证自定义处理效果
        if results:
            import json
            with open(results[0], 'r', encoding='utf-8') as f:
                first_chunk = json.load(f)

                print("\n自定义处理效果验证:")

                # 检查处理时间字段
                has_process_time = all("process_time" in item for item in first_chunk)
                print(f"所有记录都添加了处理时间: {has_process_time}")

                # 检查自动生成的ID
                auto_id_items = [item for item in first_chunk if item["id"].startswith("auto_")]
                print(f"自动生成了 {len(auto_id_items)} 个ID")

                # 检查格式化的数值
                has_formatted_value = all("value_formatted" in item for item in first_chunk if "value" in item)
                print(f"所有数值字段都已格式化: {has_formatted_value}")

                # 显示一条处理后的记录
                print("\n处理后的记录示例:")
                print(json.dumps(first_chunk[0], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
