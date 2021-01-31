#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import codecs
from setuptools import setup


def read(fname):
    file_path = os.path.join(os.path.dirname(__file__), fname)
    return codecs.open(file_path, encoding='utf-8').read()


setup(
    name='pytest-verifun',
    version='0.1.0',
    author='Ryan J. Miller',
    author_email='rjmiller10@gmail.com',
    maintainer='Ryan J. Miller',
    maintainer_email='rjmiller10@gmail.com',
    license='MIT',
    url='https://github.com/rjmill/pytest-verifun',
    description='An alternative way to parametrize test cases',
    long_description=read('README.rst'),
    py_modules=['pytest_verifun'],
    python_requires='>=3.7',
    install_requires=['pytest>=6.0.1'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Framework :: Pytest',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Testing',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: Implementation :: CPython',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
    ],
    entry_points={
        'pytest11': [
            'verifun = pytest_verifun',
        ],
    },
)
