#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup, find_packages
import os

# 读取README文件
here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

# 读取版本号
def get_version():
    version_file = os.path.join(here, 'test_mypip_setup', '__init__.py')
    with open(version_file, encoding='utf-8') as f:
        for line in f:
            if line.startswith('__version__'):
                return line.split('=')[1].strip().strip('"\'')
    return '0.1.0'

setup(
    name="test_mypip_setup",
    version=get_version(),
    author="Your Name",
    author_email="your.email@example.com",
    description="一个跨平台的Python示例包",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/test1v2",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.10",
    install_requires=[
        # 在这里添加依赖包
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=6.0",
            "pytest-cov",
            "black",
            "flake8",
        ],
    },
    entry_points={
        "console_scripts": [
            "test-mypip-setup=test_mypip_setup.main:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)