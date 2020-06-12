from setuptools import setup, find_packages
from os import path

import versioneer

PACKAGE_NAME = 'pyqttoolkit'

_here = path.abspath(path.dirname(__file__))

with open(path.join(_here, 'README.md')) as fp:
    README_CONTENTS = fp.read()

install_requires = [
    'jinja2',
    'pandas',
    'appdirs'
]

tests_require = [
    'tox',
    'pytest',
    'pytest-cov',
    'pytest-xvfb',
    'pytest-asyncio',
    'pytest-qt',
    'licensify'
]

extras_require = {
    'test': tests_require,
    'publish': ['twine']
}

setup(
    name=PACKAGE_NAME,
    install_requires=install_requires,
    tests_require=tests_require,
    extras_require=extras_require,
    packages=find_packages(exclude=('tests*',)),
    cmdclass=versioneer.get_cmdclass(),
    license='GPLv3',
    version=versioneer.get_version(),
    author='Simmovation Ltd',
    author_email='info@simmovation.tech',
    url='https://github.com/Simmovation/pyqttoolkit',
    platforms='any',
    description='A toolkit for PyQt 5',
    long_description=README_CONTENTS,
    long_description_content_type='text/markdown',
    python_requires='>=3.6'
)
