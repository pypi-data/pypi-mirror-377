#!/usr/bin/python3
# _*_ coding: utf-8 _*_
#
# Copyright (C) 2025 - 2025 anjiu, Inc. All Rights Reserved
#
# @Time    : 2025/9/18 08:45
# @Author  : anjiu
# @Email   : basui6996@gmail.com
# @File    : test_data_chunker.py
# @IDE     : PyCharm
# @Description: DataChunker测试用例

import os
import pytest
import tempfile
from data_chunker import DataChunker, generate_sample_data
from data_chunker.exceptions import ChunkSizeError, FileSaveError


class TestDataChunker:
    """DataChunker测试类"""

    def setup_method(self):
        """测试 setup"""
        self.test_dir = tempfile.mkdtemp()
        self.data = generate_sample_data(1000)

    def teardown_method(self):
        """测试 teardown"""
        # 清理测试文件
        for f in os.listdir(self.test_dir):
            os.remove(os.path.join(self.test_dir, f))
        os.rmdir(self.test_dir)

    def test_initialization(self):
        """测试初始化"""
        # 正常初始化
        chunker = DataChunker(output_dir=self.test_dir)
        assert chunker.chunk_size == 500
        assert chunker.output_dir == self.test_dir

        # 异常初始化
        with pytest.raises(ChunkSizeError):
            DataChunker(chunk_size=0, output_dir=self.test_dir)

    def test_split(self):
        """测试数据分割"""
        chunker = DataChunker(chunk_size=100, output_dir=self.test_dir)

        # 测试分割
        chunks = list(chunker.split(self.data))
        assert len(chunks) == 10  # 1000/100 = 10个分块

        # 测试每个分块的大小
        for i, chunk in enumerate(chunks):
            if i < 9:  # 前9个分块应该是100条
                assert len(chunk) == 100
            else:  # 最后一个分块应该是100条（1000能被100整除）
                assert len(chunk) == 100

    def test_process_sequential(self):
        """测试顺序处理"""
        chunker = DataChunker(chunk_size=100, output_dir=self.test_dir, parallel=False)

        # 处理数据
        results = chunker.process(self.data)

        # 验证结果
        assert len(results) == 10
        assert all(os.path.exists(path) for path in results)

        # 验证文件内容
        for i, path in enumerate(results):
            with open(path, 'r', encoding='utf-8') as f:
                import json
                chunk_data = json.load(f)
                assert len(chunk_data) == 100
                assert all('id' in item for item in chunk_data)

    def test_process_parallel(self):
        """测试并行处理"""
        chunker = DataChunker(
            chunk_size=100,
            output_dir=self.test_dir,
            parallel=True,
            workers=2
        )

        # 处理数据
        results = chunker.process(self.data)

        # 验证结果
        assert len(results) == 10
        assert all(os.path.exists(path) for path in results)

    def test_process_stream(self):
        """测试流式处理"""
        chunker = DataChunker(chunk_size=100, output_dir=self.test_dir)

        # 创建流式数据生成器
        def data_stream():
            for item in self.data:
                yield item

        # 处理流式数据
        results = chunker.process_stream(data_stream())

        # 验证结果
        assert len(results) == 10
        assert all(os.path.exists(path) for path in results)

    def test_set_config(self):
        """测试动态配置"""
        chunker = DataChunker(output_dir=self.test_dir)

        # 修改配置
        chunker.set_config(chunk_size=200, prefix="test")

        # 验证配置修改
        assert chunker.chunk_size == 200
        assert chunker.prefix == "test"

        # 处理数据验证新配置生效
        results = chunker.process(self.data)
        assert len(results) == 5  # 1000/200 = 5个分块

        # 验证文件名前缀
        assert all("test" in os.path.basename(path) for path in results)

    def test_get_file_list(self):
        """测试获取文件列表"""
        chunker = DataChunker(chunk_size=100, output_dir=self.test_dir)

        # 处理数据
        chunker.process(self.data)

        # 获取文件列表
        file_list = chunker.get_file_list()

        # 验证文件列表
        assert len(file_list) == 10
        assert all(path.endswith('.json') for path in file_list)

    def test_clear_output(self):
        """测试清空输出目录"""
        chunker = DataChunker(chunk_size=100, output_dir=self.test_dir)

        # 处理数据
        chunker.process(self.data)

        # 验证文件存在
        assert len(os.listdir(self.test_dir)) == 10

        # 清空输出目录
        removed_count = chunker.clear_output()

        # 验证清空结果
        assert removed_count == 10
        assert len(os.listdir(self.test_dir)) == 0

    def test_empty_data(self):
        """测试空数据处理"""
        chunker = DataChunker(output_dir=self.test_dir)

        # 处理空数据
        results = chunker.process([])

        # 验证结果
        assert len(results) == 0
        assert len(os.listdir(self.test_dir)) == 0

    def test_custom_logger(self):
        """测试自定义日志记录器"""
        import logging

        # 创建自定义日志记录器
        logger = logging.getLogger("TestLogger")
        logger.setLevel(logging.DEBUG)

        # 创建内存处理器用于测试
        from io import StringIO
        log_stream = StringIO()
        handler = logging.StreamHandler(log_stream)
        logger.addHandler(handler)

        # 使用自定义日志记录器
        chunker = DataChunker(output_dir=self.test_dir, logger=logger)

        # 处理数据
        chunker.process(self.data[:100])  # 只处理100条数据

        # 验证日志输出
        log_content = log_stream.getvalue()
        assert "DataChunker初始化完成" in log_content
        assert "已保存分块到" in log_content
