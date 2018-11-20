#!/usr/bin/env python3
from setuptools import setup

setup(
    name='isi_bkp',
    version='0.1',
    description='Isilon backup tools',
    url='https://github.com/TST-Infra/isi-bkp-tools/',
    author='Gabriel Teles',
    author_email='gabriel.soares@tst.jus.br',
    license='GNU GENERAL PUBLIC LICENSE',
    packages=['isi_bkp'],
    scripts=['bin/isi-tools.py'],
    zip_safe=False
)