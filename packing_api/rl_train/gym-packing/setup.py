#!usr/bin/env python
from setuptools import setup

VERSION = '0.21.0'

setup(
    name='gym_packing',
    version=VERSION,
    description='Gym environment for 4D VM Packing',
    author='Prathamesh Saraf',
    license='MIT',
    install_requires=[
        'gym >= 0.21',
        'numpy>=1.16.1',
		'pandas>=1.2',
		'scipy>=1.0',
		'matplotlib>=3.1',
		'networkx>=2.3',
    ],
    zip_safe=False,
	python_requires='>=3.7',
	classifiers=[
		'Development Status :: 3 - Alpha',
		'Intended Audience :: Developers',
		'Programming Language :: Python :: 3.7',
		'Programming Language :: Python :: 3.8',
		'Programming Language :: Python :: 3.9',
	]
)