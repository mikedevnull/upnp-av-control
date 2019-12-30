from setuptools import setup, find_packages

setup(name='upnpavcontrol',
      description='UPNP AV control point library',
      version='0.0.1',
      url='https://github.com/mikedevnull/upnp-av-control',
      author='Michael Meier',
      author_email='michael.meier@bluesheep.de',
      license='BSD-3-Clause',
      python_requires='>=3.7',
      install_requires=['async_upnp_client', 'fastapi', 'attrs', 'lxml', 'uvicorn', 'colorlog'],
      extras_require={
          'test': ['pytest~=3.5', 'pytest-cov~=2.5', 'pytest-asyncio', 'async_asgi_testclient'],
          'dev': ['flake8~=3.5', 'flake8-print~=3.1', 'yapf'],
      },
      entry_points={
          'console_scripts': [
              'upnp-av-web-cp= upnpavcontrol.tools.web_control_point:main',
          ],
      },
      packages=find_packages())
