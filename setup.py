from setuptools import setup, find_packages
import peon

setup(
    name='peon',
    version=peon.__version__,
    packages=find_packages(),
    install_requires=[
        'watchdog~=2.1',
        'requests~=2.27',
        'libsass~=0.21',
        'htmlmin~=0.1',
        'cssmin~=0.2'
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
        # `ln -s /<path>/bin/peon /usr/local/bin`
        # for macos. if DOES NOT create the command line.
        # `python setup.py install --record files.txt` to find <path>
    }
)
