# -*- coding: utf-8 -*-
#
# setup.py
#
# Copyright 2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

"""
Parse DBR (Detailed Billing Records) and send resulting data direct to
Elasticsearch or dump formatted as JSON.
"""

import io
import os
import re

from setuptools import find_packages, setup


def read(*filenames, **kwargs):
    encoding = kwargs.get('encoding', 'utf-8')
    sep = kwargs.get('sep', os.linesep)
    buf = []
    for filename in filenames:
        with io.open(filename, encoding=encoding) as f:
            buf.append(f.read())
    return sep.join(buf)


def read_version():
    content = read(os.path.join(
        os.path.dirname(__file__), 'awsdbrparser', '__init__.py'))
    return re.search(r"__version__ = '([^']+)'", content).group(1)


def read_requirements():
    content = read(os.path.join('requirements', 'base.txt'))
    return [line for line in content.split(os.linesep)
            if not line.strip().startswith('#')]


setup(
    name='awsdbrparser',
    version=read_version(),
    url='http://github.com/awslabs/aws-detailed-billing-parser',
    license='Apache Software License',
    author='Rafael M. Koike',
    author_email='koiker@amazon.com',
    description='Parse DBR and send to Elasticsearch or dumps to JSON',
    long_description=read('README.rst'),
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=read_requirements(),
    entry_points={
        'console_scripts': [
            'dbrparser = awsdbrparser.cli:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'Environment :: Other Environment',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ]
)
