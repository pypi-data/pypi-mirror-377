# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['bplsdk']

package_data = \
{'': ['*']}

install_requires = \
['cobs>=1.1.4,<2.0.0',
 'crcmod>=1.7,<2.0',
 'pyserial>=3.4,<4.0']

setup_kwargs = {
    'name': 'bplsdk',
    'version': '0.5.0',
    'description': 'An SDK for a more ergonomic use of the BPL protocol',
    'long_description': None,
    'author': 'Sindre Hansen',
    'author_email': 'sindre.hansen@blueye.no',
    'maintainer': 'Sindre Hansen',
    'maintainer_email': 'sindre.hansen@blueye.no',
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.11,<4.0',
}


setup(**setup_kwargs)
