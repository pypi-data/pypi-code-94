from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='test-acme-abnb',
    packages=['acme'],
    version='0.0.2',
    author="Kenneth Yang",
    author_email="kenneth.yang8@gmail.com",
    description='Ottr ACME Client Python Wrapper',
    url="https://github.com/yangkenneth/ottr-package",
    install_requires=[
        "boto3",
        "botocore",
        "pyOpenSSL"
    ],
    extras_require={
        "dev": [
            "pytest"
        ]
    },
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ),
    python_requires='>=3'
)
