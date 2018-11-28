from setuptools import setup, find_packages
from os import path
import re

here = path.abspath(path.dirname(__file__))

def find_version():
    with open(path.join(here, 'pyqttoolkit', '__init__.py')) as fp:
        version_file = fp.read()
    version_match = re.search(r"__version__ = ['\"]([^'\"]*)['\"]", version_file, re.M)
    if version_match:
        return version_match.group(1)
    raise RuntimeError("Unable to find version string.")

setup(
    name='pyqttoolkit',
    version=find_version(),
    packages=find_packages(),
    install_requires=[
        'pyqt5==5.9.2',
        'matplotlib',
        'jinja2',
        'pandas',
        'fonttools==3.32.0'
    ],
    extras_require={
        'dev': [
            'tox',
            'pytest',
            'pytest-asyncio',
            'pytest-qt'
        ]
    }
)