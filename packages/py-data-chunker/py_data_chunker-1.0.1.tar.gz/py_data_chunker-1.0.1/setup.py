#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os
import re


# 读取README.md作为长描述
def read_readme():
    try:
        with open("README.md", "r", encoding="utf-8") as fh:
            return fh.read()
    except FileNotFoundError:
        return "高效数据分块处理模块"


long_description = read_readme()


# 安全地读取版本信息
def read_version():
    version_file = os.path.join("src", "data_chunker", "__init__.py")

    # 使用正则表达式提取版本号
    version_pattern = r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]'

    try:
        with open(version_file, "r", encoding="utf-8") as f:
            for line in f:
                match = re.search(version_pattern, line)
                if match:
                    return match.group(1)
    except (FileNotFoundError, UnicodeDecodeError) as e:
        print(f"读取版本信息时出错: {e}")

    return "0.1.0"


# 安全地读取作者信息
def read_author_info():
    author_file = os.path.join("src", "data_chunker", "__init__.py")

    author_pattern = r'^__author__\s*=\s*[\'"]([^\'"]*)[\'"]'
    email_pattern = r'^__email__\s*=\s*[\'"]([^\'"]*)[\'"]'

    author = "Unknown"
    email = "unknown@example.com"

    try:
        with open(author_file, "r", encoding="utf-8") as f:
            for line in f:
                author_match = re.search(author_pattern, line)
                if author_match:
                    author = author_match.group(1)

                email_match = re.search(email_pattern, line)
                if email_match:
                    email = email_match.group(1)
    except (FileNotFoundError, UnicodeDecodeError) as e:
        print(f"读取作者信息时出错: {e}")

    return author, email


# 安全地读取依赖
def read_requirements():
    requirements = []
    if os.path.exists("requirements.txt"):
        try:
            with open("requirements.txt", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        requirements.append(line)
        except (FileNotFoundError, UnicodeDecodeError) as e:
            print(f"读取依赖时出错: {e}")

    return requirements


# 获取版本和作者信息
version = read_version()
author, author_email = read_author_info()
requirements = read_requirements()

setup(
    name="py-data-chunker",
    version=version,
    author=author,
    author_email=author_email,
    description="高效数据分块处理模块，用于将大型字典列表数据分割成固定大小的块",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitee.com/ugly-xue/data_chunker",
    # 使用 SPDX 许可证表达式
    license="MIT",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    python_requires=">=3.6",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov>=2.0",
            "black>=21.5b2",
            "flake8>=3.9",
            "mypy>=0.9",
            "sphinx>=4.0",
            "twine>=3.0",
            "wheel>=0.36",
        ],
        "docs": [
            "sphinx>=4.0",
            "sphinx-rtd-theme>=0.5",
        ],
    },
    entry_points={
        "console_scripts": [
            "data_chunker=data_chunker.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
    keywords=["data", "chunk", "split", "json", "processing"],
    project_urls={
        "Documentation": "https://gitee.com/ugly-xue/data_chunker/docs",
        "Source": "https://gitee.com/ugly-xue/data_chunker",
        "Tracker": "https://gitee.com/ugly-xue/data_chunker/issues",
    },
)
