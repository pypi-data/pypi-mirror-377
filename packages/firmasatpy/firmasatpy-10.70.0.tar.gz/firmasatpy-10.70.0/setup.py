import os
from setuptools import setup


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


readme = read('README.rst')
changelog = read('CHANGELOG.rst')

setup(name='firmasatpy',
      version='10.70.0',
      description='Python interface to FirmaSAT',
      long_description=readme + '\n\n' + changelog,
      author='David Ireland',
      url='https://cryptosys.net/firmasat/',
      platforms=['Windows'],
      py_modules=['firmasat'],
      )
