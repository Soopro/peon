# coding=utf-8

from setuptools import setup, find_packages
import puss

setup(
    name='puss',
    version=puss.__version__,
    packages=find_packages(),
    install_requires=[
        'watchdog>=0.8.3',
        'requests>=2.3.0'
    ],
    author='Redy',
    author_email='redy.ru@gmail.com',
    description='Puss in boots is a web front-end develop assist tool.',
    license='MIT',
    keywords='angular Web front-end coffee less compress package vue',
    url='https://github.com/soopro/puss-in-boots',
    entry_points={
        'console_scripts': [
            'puss = puss:run',
        ]
    }
)
