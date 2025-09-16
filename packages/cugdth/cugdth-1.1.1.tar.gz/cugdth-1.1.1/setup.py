#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages  # 这个包没有的可以pip一下

setup(
    name="cugdt",  # 这里是pip项目发布的名称
    version="1.1.1",  # 版本号，数值大的会优先被pip
    keywords=["pip", "tiff", "cugdt"],  # 关键字
    description="Tiff文件读取，写入，压缩",  # 描述
    license="MIT Licence",  # 许可证

    url="https://gitee.com/HaixuHe/cugdt",  # 项目相关文件地址，一般是github项目地址即可
    author="HaixuHe",  # 作者
    author_email="20161001925@cug.edu.cn",
    packages=find_packages(),
    include_package_data=True,
    platforms="any",
    install_requires=[],  # 这个项目依赖的第三方库
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Natural Language :: Chinese (Simplified)',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries'
    ],
)
