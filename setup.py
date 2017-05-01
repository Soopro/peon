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
    description='''Peon is a web front-end develop assist package.
    Includes Construction and static web server,
    support Coffeescript Less and Jade''',
    license='MIT',
    keywords='web front-end coffee less jade',
    url='http://github.com/soopro/peon',
    entry_points={
        'console_scripts': [
            'peon = peon:run',
        ]
    }
)
