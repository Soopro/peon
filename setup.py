#coding=utf-8

from setuptools import setup, find_packages
import peon

setup(
    name = "peon",
    version = peon.__version__,
    packages = find_packages(),
    install_requires = [
        'CoffeeScript>=1.0.10',
        'lesscpy>=0.10.2',
        'pyjade>=3.0.0'
    ],
    author = "Redy",
    author_email = "redy.ru@gmail.com",
    description = "Peon is a web front-end develop assist package. "+\
                  "Includes Construction and static web server, "+\
                  "support Coffeescript Less and Jade",
    license = "MIT",
    keywords = "web front-end coffee less jade",
    url = "http://github.com/soopro/peon",
    entry_points={
        'console_scripts' : [
            'peon = peon.peon_construct:construct',
            'peon_server = peon.peon_server:server',
        ]
    }
)