#!/usr/bin/env python
import os
from setuptools import setup

setup(
    name='hcbot',
    version='1.0',
    packages=['hcbot'],
    author='cn',
    author_email='lolexplode@gmail.com',
    license='MIT',
    install_requires=[
        'opencv-python',
        'mss',
        'pywin32',
        'numpy'
    ]
)
