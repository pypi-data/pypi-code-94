# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['paloalto_env']

package_data = \
{'': ['*']}

install_requires = \
['python-dotenv']

setup_kwargs = {
    'name': 'paloalto-env',
    'version': '0.1.6',
    'description': 'Palo Alto Env wrapper',
    'long_description': None,
    'author': 'Thomas Christory',
    'author_email': None,
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
