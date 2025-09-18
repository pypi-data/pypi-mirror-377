#!/usr/bin/env python3
from os import path
import setuptools

import drf_keycloak_auth as meta

this_dir = path.abspath(path.dirname(__file__))
with open(path.join(this_dir, 'README.md'), mode='r') as f:
    long_description = f.read()

setuptools.setup(
    name=meta.__title__,
    version=meta.__version__,
    author=meta.__author__,
    author_email=meta.__author_email__,
    description=meta.__description__,
    long_description=long_description,
    long_description_content_type='text/markdown',
    url=meta.__url__,
    license=meta.__license__,
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.10',
    install_requires=[
        'djangorestframework>=3.15,<4',
        'python-keycloak>=5.1',
        'django>=4.1',
        'requests_oauthlib>=2.0.0',
        'urllib3<1.27,>=1.21.1',
        'pyjwt>=2.6',
        'pytz'
    ],
    keywords=[
        'drf',
        'django',
        'rest_framework',
        'djangorestframework',
        'authentication',
        'python3',
        'keycloak'
    ],
)
