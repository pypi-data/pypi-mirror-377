#!/usr/bin/python3
# _*_ coding: utf-8 _*_
#
# Copyright (C) 2025 - 2025 anjiu, Inc. All Rights Reserved 
#
# @Time    : 2025/9/18 09:07
# @Author  : anjiu
# @Email   : basui6996@gmail.com
# @File    : exceptions.py
# @IDE     : PyCharm
# @Description    : DataChunker异常类


class DataChunkerError(Exception):
    """ the DataChunker basic anomaly class """
    pass


class FileSaveError(DataChunkerError):
    """ the file save failed """
    pass


class ChunkSizeError(DataChunkerError):
    """ the wrong chunking size """
    pass


class InvalidDataError(DataChunkerError):
    """ the data invalid error """
    pass
