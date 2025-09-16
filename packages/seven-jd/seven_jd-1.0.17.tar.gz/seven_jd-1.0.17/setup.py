# -*- coding: utf-8 -*-
"""
@Author: HuangJingCan
@Date: 2020-04-22 21:25:59
:LastEditTime: 2025-09-16 11:17:20
:LastEditors: HuangJingCan
@Description: 
"""
from __future__ import print_function
from setuptools import setup, find_packages

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name="seven_jd",
    version="1.0.17",
    author="seven",
    author_email="tech@gao7.com",
    description="seven jd",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="http://gitlab.tdtech.gao7.com/TaoBaoCloud/seven_jd.git",
    packages=find_packages(),
    install_requires=[],
    classifiers=[
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
    ],
    python_requires='~=3.4',
)
