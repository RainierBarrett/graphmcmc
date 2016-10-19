#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'Click>=6.0',
    # TODO: put package requirements here
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='graphmcmc',
    version='0.1.0',
    description="This is a Markov-chain Monte Carlo simulator for graphs in Python",
    long_description=readme + '\n\n' + history,
    author="Rainier Barrett",
    author_email='rbarret8@ur.rochester.edu',
    url='https://github.com/RainierBarrett/graphmcmc',
    packages=[
        'graphmcmc',
    ],
    package_dir={'graphmcmc':
                 'graphmcmc'},
    entry_points={
        'console_scripts': [
            'graphmcmc=graphmcmc.cli:main'
        ]
    },
    include_package_data=True,
    install_requires=requirements,
    license="GNU General Public License v3",
    zip_safe=False,
    keywords='graphmcmc',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
