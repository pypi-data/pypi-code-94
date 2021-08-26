import os
from setuptools import setup, find_packages


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name='krules-dev-support',
    version="0.9.1",
    author="Alberto Degli Esposti",
    author_email="alberto@arispot.tech",
    description="KRules dev utilities",
    license="Apache Licence 2.0",
    keywords="krules rules engine sane-build",
    url="https://github.com/airspot-dev/krules",
    packages=find_packages(),
    long_description=read('README.md'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "License :: OSI Approved :: Apache Software License",
    ],
    python_requires='>3.8',
    install_requires=[
        'Jinja2==3.0.1',
        'sane-build==7.2',
        'python-dotenv==0.19.0',
        'PyYAML==5.4.1',
        'MarkupSafe==2.0.1',
    ],
    setup_requires=[
        'pytest-runner',
    ],
    tests_require=[
        'pytest',
    ],
)