#!/usr/bin/python3
# _*_ coding: utf-8 _*_
#
# Copyright (C) 2025 - 2025 anjiu, Inc. All Rights Reserved 
#
# @Time    : 2025/9/18 09:06
# @Author  : anjiu
# @Email   : basui6996@gmail.com
# @File    : core.py.py
# @IDE     : PyCharm
# @Description    : DataChunker核心类实现

import os
import json
from itertools import islice
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

from .utils import setup_logger
from .exceptions import ChunkSizeError, FileSaveError


class DataChunker:
    """
    高效数据分块处理类

    用于将大型字典列表数据分割成固定大小的块，
    并将每个块保存为json文件。
    """

    def __init__(self, chunk_size=500, output_dir="output", prefix="chunk",
                 timestamp=True, parallel=False, workers=4, logger=None):
        """
        初始化数据分块处理器

        :param chunk_size: 每个分块的大小，默认为500
        :param output_dir: 输出目录，默认为"output"
        :param prefix: 文件名前缀，默认为"chunk"
        :param timestamp: 是否在文件名中添加时间戳，默认为True
        :param parallel: 是否使用并行处理，默认为False
        :param workers: 并行工作线程数，默认为4
        :param logger: 自定义日志记录器，默认为None
        """
        # 参数验证
        if chunk_size <= 0:
            raise ChunkSizeError("chunk_size必须大于0")

        self.chunk_size = chunk_size
        self.output_dir = output_dir
        self.prefix = prefix
        self.timestamp = timestamp
        self.parallel = parallel
        self.workers = workers

        # 设置日志记录器
        self.logger = logger or setup_logger()

        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)

        self.logger.info(f"DataChunker初始化完成: chunk_size={chunk_size}, "
                         f"output_dir={output_dir}, parallel={parallel}, workers={workers}")

    def set_config(self, **kwargs):
        """
        动态更新配置参数

        :param kwargs: 配置参数键值对
        :return: None
        """
        valid_params = ['chunk_size', 'output_dir', 'prefix', 'timestamp', 'parallel', 'workers']

        for key, value in kwargs.items():
            if key in valid_params:
                setattr(self, key, value)
                self.logger.info(f"配置更新: {key} = {value}")
            else:
                self.logger.warning(f"忽略无效配置参数: {key}")

        # 如果更新了输出目录，确保目录存在
        if 'output_dir' in kwargs:
            os.makedirs(self.output_dir, exist_ok=True)

    def split(self, data):
        """
        将数据分割成多个固定大小的块

        :param data: 字典列表数据
        :return: 生成器，每次产生一个数据分块
        """
        if not data:
            self.logger.warning("输入数据为空")
            return

        it = iter(data)
        chunk_count = 0

        while True:
            chunk = list(islice(it, self.chunk_size))
            if not chunk:
                break

            chunk_count += 1
            self.logger.debug(f"生成分块 #{chunk_count}, 大小: {len(chunk)}")
            yield chunk

        self.logger.info(f"数据分割完成，共生成 {chunk_count} 个分块")

    def _process_chunk(self, chunk, chunk_index):
        """
        处理单个数据分块并保存为JSON文件（内部方法）

        :param chunk: 数据分块
        :param chunk_index: 分块索引
        :return: 保存的文件路径
        :raises FileSaveError: 文件保存失败时抛出
        """
        try:
            # 生成文件名
            timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S") if self.timestamp else ""
            file_name = f"{self.prefix}_{chunk_index:04d}_{len(chunk)}_{timestamp_str}.json"
            file_path = os.path.join(self.output_dir, file_name)

            # 保存为JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(chunk, f, ensure_ascii=False, indent=2)

            self.logger.info(f"已保存分块到: {file_path} ({len(chunk)}条记录)")
            return file_path

        except Exception as e:
            error_msg = f"保存分块 #{chunk_index} 失败: {str(e)}"
            self.logger.error(error_msg)
            raise FileSaveError(error_msg)

    def process(self, data):
        """
        处理数据并将其分割保存为JSON文件

        :param data: 字典列表数据
        :return: 所有保存的文件路径列表
        """
        if not data:
            self.logger.warning("输入数据为空，没有文件被保存")
            return []

        self.logger.info(f"开始处理数据，总大小: {len(data)} 条记录")

        # 创建分块生成器
        chunks = self.split(data)

        if self.parallel:
            return self._process_parallel(chunks)
        else:
            return self._process_sequential(chunks)

    def _process_sequential(self, chunks):
        """
        顺序处理分块（内部方法）

        :param chunks: 分块生成器
        :return: 所有保存的文件路径列表
        """
        results = []

        for i, chunk in enumerate(chunks):
            try:
                result = self._process_chunk(chunk, i + 1)
                results.append(result)
            except FileSaveError:
                # 记录错误但继续处理其他分块
                chunk_index = i + 1
                self.logger.error(f"第 {chunk_index} 个分块处理失败，已忽略")
                continue

        self.logger.info(f"顺序处理完成，共保存 {len(results)} 个文件")
        return results

    def _process_parallel(self, chunks):
        """
        并行处理分块（内部方法）

        :param chunks: 分块生成器
        :return: 所有保存的文件路径列表
        """
        results = []
        futures = {}

        with ThreadPoolExecutor(max_workers=self.workers) as executor:
            # 提交所有分块处理任务
            for i, chunk in enumerate(chunks):
                future = executor.submit(self._process_chunk, chunk, i + 1)
                futures[future] = i + 1

            # 等待所有任务完成并收集结果
            for future in as_completed(futures):
                try:
                    result = future.result()
                    results.append(result)
                except FileSaveError:
                    # 记录错误但继续处理其他分块
                    chunk_index = futures[future]
                    self.logger.error(f"分块 #{chunk_index} 处理失败")

        self.logger.info(f"并行处理完成，共保存 {len(results)} 个文件")
        return results

    def process_stream(self, stream_generator):
        """
        处理流式数据并将其分割保存为JSON文件

        :param stream_generator: 生成字典数据的生成器
        :return: 所有保存的文件路径列表
        """
        self.logger.info("开始处理流式数据")

        results = []
        chunk_index = 1
        current_chunk = []

        for item in stream_generator:
            current_chunk.append(item)

            # 当达到分块大小时处理当前分块
            if len(current_chunk) >= self.chunk_size:
                try:
                    result = self._process_chunk(current_chunk, chunk_index)
                    results.append(result)

                    # 重置当前分块和索引
                    current_chunk = []
                    chunk_index += 1
                except FileSaveError:
                    # 记录错误但继续处理其他分块
                    current_chunk = []
                    chunk_index += 1
                    self.logger.error(f"分块 #{chunk_index} 处理失败，已忽略")

        # 处理剩余的数据
        if current_chunk:
            try:
                result = self._process_chunk(current_chunk, chunk_index)
                results.append(result)
            except FileSaveError:
                # 记录错误
                self.logger.error(f"分块 #{chunk_index} 处理失败")

        self.logger.info(f"流式处理完成，共保存 {len(results)} 个文件")
        return results

    def get_file_list(self):
        """
        获取已保存的文件列表

        :return: 输出目录中的所有JSON文件路径
        """
        try:
            files = [os.path.join(self.output_dir, f)
                     for f in os.listdir(self.output_dir)
                     if f.endswith('.json')]
            files.sort()  # 按文件名排序
            return files
        except Exception as e:
            self.logger.error(f"获取文件列表失败: {str(e)}")
            return []

    def clear_output(self):
        """
        清空输出目录中的所有JSON文件

        :return: 删除的文件数量
        """
        try:
            files = self.get_file_list()
            for file_path in files:
                os.remove(file_path)

            self.logger.info(f"已清除 {len(files)} 个文件")
            return len(files)
        except Exception as e:
            self.logger.error(f"清空输出目录失败: {str(e)}")
            return 0
