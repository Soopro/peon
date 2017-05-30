# coding=utf-8

from setuptools import setup, find_packages
import peon

setup(
    name='peon',
    version=peon.__version__,
    packages=find_packages(),
    install_requires=[
        'watchdog>=0.8.3',
        'requests>=2.3.0'
    ],
    author='Redy',
    author_email='redy.ru@gmail.com',
    description='Peon is a web front-end develop assist tool.',
    license='MIT',
    keywords='angular Web front-end coffee less compress package vue',
    url='https://github.com/soopro/peon',
    entry_points={
        'console_scripts': [
            'peon = peon:run',
        ]
    }
)
