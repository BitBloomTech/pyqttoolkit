from setuptools import setup, find_packages
from os import path
import sys

# The build backend may execute setup.py without the source root on sys.path.
sys.path.insert(0, path.abspath(path.dirname(__file__)))
import versioneer

PACKAGE_NAME = 'pyqttoolkit'

_here = path.abspath(path.dirname(__file__))

with open(path.join(_here, 'README.md')) as fp:
    README_CONTENTS = fp.read()

install_requires = [
    'matplotlib',
    'jinja2>=3.1.6',
    'pandas',
    'appdirs'
]

tests_require = [
    'tox>=4',
    'pytest',
    'pytest-cov',
    'pytest-xvfb',
    'pytest-asyncio',
    'pytest-qt'
]

extras_require = {
    'test': tests_require,
    'publish': ['build>=1.6.1', 'twine>=7.0.0'],
    'ui': ['pyqt5']
}

setup(
    name=PACKAGE_NAME,
    install_requires=install_requires,
    extras_require=extras_require,
    packages=find_packages(exclude=('tests*',)),
    cmdclass=versioneer.get_cmdclass(),
    license='GPLv3',
    version=versioneer.get_version(),
    author='Bitbloom Ltd',
    author_email='info@bitbloom.tech',
    url='https://github.com/BitBloomTech/pyqttoolkit',
    platforms='any',
    description='A toolkit for PyQt 5',
    long_description=README_CONTENTS,
    long_description_content_type='text/markdown',
    python_requires='>=3.14'
)
