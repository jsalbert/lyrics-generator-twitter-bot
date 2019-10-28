#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='lyrics-generation-bot-gpt2',
    version='1.0.0',
    description='Lyrics Generation Bot',
    author='Albert Jimenez Sanfiz',
    author_email='jsalbert.me@gmail.com',
    url='https://www.albertjimenez.xyz/',
    packages=find_packages(exclude=['tests', '.cache', '.venv', '.git', 'dist']),
    install_requires=[
        'regex',
        'tweepy',
        'numpy',
        'Pillow',
        'tqdm',
        'jupyter'
        ]
)
