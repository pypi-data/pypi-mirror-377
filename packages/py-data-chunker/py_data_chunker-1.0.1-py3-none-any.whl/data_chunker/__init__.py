#!/usr/bin/python3
# _*_ coding: utf-8 _*_
#
# Copyright (C) 2025 - 2025 anjiu, Inc. All Rights Reserved 
#
# @Time    : 2025/9/18 09:06
# @Author  : anjiu
# @Email   : basui6996@gmail.com
# @File    : __init__.py.py
# @IDE     : PyCharm
# @Description    : DataChunker - 高效数据分块处理模块

"""
DataChunker - 高效数据分块处理模块

该模块提供将大型字典列表数据分割成固定大小的块，
并将每个块保存为JSON文件的功能。
"""

from .core import DataChunker
from .utils import generate_sample_data, json_stream_reader
from .exceptions import DataChunkerError, FileSaveError, ChunkSizeError

__version__ = "1.0.1"
__author__ = "anjiu"
__email__ = "basui6996@gmail.com"

__all__ = [
    'DataChunker',
    'generate_sample_data',
    'json_stream_reader',
    'DataChunkerError',
    'FileSaveError',
    'ChunkSizeError'
]
