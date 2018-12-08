#!/usr/bin/env python
from setuptools import setup, find_packages

with open("README.rst") as rm_file:
    long_description = rm_file.read()


def get_requirements():
    with open('requirements.txt') as obj:
        lines = [dep for dep in obj.read().split('\n') if dep]
        return lines


setup(
    name='memfs',
    version='0.0.1',
    description="Fun little in-memory file system for Python",
    long_description=long_description,
    author='David Woodruff',
    author_email='dswoodruff88@gmail.com',
    url='https://github.com/dsw88/memfs',
    packages=find_packages(),
    license="MIT",
    install_requires=get_requirements()
)