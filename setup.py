# -*- coding: utf-8 -*-
"""
软件包安装脚本
"""
from setuptools import setup, find_packages

from arptool import __author__, __version__

def get_requires():
    requires = []
    with open("./requirements.txt", "r") as f:
        line = f.readline()
        while line:
            requires.append(line.replace("\n", ""))
            line = f.readline()
    return requires

setup(
    name="arptool",
    version=__version__,
    description="arp协议的Python实现,内附小工具",
    author=__author__,
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=get_requires(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7"
    ]
)
