#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""upversion - update version numbers
"""
import sys
from setuptools import setup, find_packages


classifiers = """\
Development Status :: 5 - Production/Stable
Intended Audience :: Developers
Programming Language :: Python
Programming Language :: Python :: 3
Topic :: Software Development :: Libraries
"""

version = '0.0.1'


setup(
    name='upversion',
    version=version,
    install_requires=[
    ],
    author='Bjorn Pettersen',
    author_email='bp@datakortet.no',
    url='https://github.com/thebjorn/upversion',
    description=__doc__.strip(),
    classifiers=[line for line in classifiers.split('\n') if line],
    long_description=open('README.rst').read(),
    entry_points={
        'console_scripts': [
            'upversion = upversion.upversion:upversion_cmd',
        ]
    },
    packages=find_packages(exclude=['tests']),
    zip_safe=False,
)
