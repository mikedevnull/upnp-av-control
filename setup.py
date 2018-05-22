from setuptools import setup, find_packages

setup(
    name='UpnpAVControl',
    description='UPNP AV control point library',
    version='0.0.1',

    url='https://github.com/mikedevnull/upnp-av-control',

    author='Michael Meier',
    author_email='michael.meier@bluesheep.de',
    license='BSD-3-Clause',

    install_requires=[
        'upnpclient',
    ],

    extras_require={
        'test': [
            'pytest~=3.5',
            'pytest-cov~=2.5',
        ],
        'dev': [
            'flake8~=3.5',
            'flake8-print~=3.1',
        ],
    },

    packages=find_packages()
)
