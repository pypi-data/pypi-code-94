#!/usr/bin/env python
# coding: utf-8

from setuptools import setup,find_packages

setup(
    name='py-pcqq',
    version='0.2.4',
    author='DawnNights',
    author_email='2224825532@qq.com',
    url='https://github.com/DawnNights/py-pcqq',
    description=u'一个使用pcqq协议的简易python qqbot库',
    long_description = open("README.rst", encoding='utf-8').read(),
    # long_description_content_type='text/markdown',
    packages=find_packages(),
    install_requires=[],
    entry_points={},
    data_files=["README.md"]
)
