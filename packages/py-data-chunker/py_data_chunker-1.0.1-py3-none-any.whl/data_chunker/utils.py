#!/usr/bin/python3
# _*_ coding: utf-8 _*_
#
# Copyright (C) 2025 - 2025 anjiu, Inc. All Rights Reserved
#
# @Time    : 2025/9/18 09:07
# @Author  : anjiu
# @Email   : basui6996@gmail.com
# @File    : utils.py
# @IDE     : PyCharm
# @Description    : DataChunker工具函数

import json
import logging
from datetime import datetime


def setup_logger():
    """
    设置默认日志记录器

    :return:
    """
    logger = logging.getLogger("DataChunker")
    logger.setLevel(logging.INFO)

    # 创建控制台处理器
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # 创建格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    ch.setFormatter(formatter)

    # 添加处理器到记录器
    logger.addHandler(ch)

    return logger


def generate_sample_data(size=3000):
    """
    生成示例数据用于测试

    :param size: 生成的数据条数，默认为3000
    :return: 示例字典列表
    """
    return [{
        "id": i,
        "name": f"User_{i}",
        "email": f"user_{i}@example.com",
        "value": i * 10,
        "timestamp": datetime.now().isoformat()
    } for i in range(size)]


def json_stream_reader(file_path):
    """
    流式读取大型JSON文件

    :param file_path: JSON文件路径
    :return: 生成器，每次产生一个JSON对象
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        for line in f:
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                # 跳过无效的JSON行
                continue


def read_json_file(file_path):
    """
    读取JSON文件

    :param file_path: JSON文件路径
    :return: JSON数据
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def write_json_file(data, file_path, indent=2):
    """
    写入JSON文件

    :param data: 要写入的数据
    :param file_path: 文件路径
    :param indent: 缩进空格数，默认为2
    :return: None
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=indent)
