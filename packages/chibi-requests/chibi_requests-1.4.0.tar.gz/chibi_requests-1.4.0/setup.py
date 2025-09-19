#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'chibi>=0.10.0', 'requests>=2.22.0', 'beautifulsoup4>=4.8.0',
    'marshmallow>=3.26.0' ]

setup(
    author="Dem4ply",
    author_email='dem4ply@gmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: Public Domain',
        'Natural Language :: English',
        'Natural Language :: Spanish',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: Python :: 3.14',
        'Topic :: Utilities',
    ],
    description="handle urls in a more easy and human way",
    install_requires=requirements,
    long_description=readme + '\n\n' + history,
    include_package_data=True,
    keywords='chibi_requests',
    name='chibi_requests',
    packages=find_packages(include=['chibi_requests', 'chibi_requests.*']),
    url='https://github.com/dem4ply/chibi_requests',
    version='1.4.0',
    zip_safe=False,
)
