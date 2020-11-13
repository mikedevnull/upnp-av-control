from setuptools import setup, find_packages

setup(name='upnpavcontrol',
      description='UPNP AV control point library',
      version='0.0.1',
      url='https://github.com/mikedevnull/upnp-av-control',
      author='Michael Meier',
      author_email='michael.meier@bluesheep.de',
      license='BSD-3-Clause',
      python_requires='>=3.7',
      install_requires=['async_upnp_client', 'fastapi', 'defusedxml', 'uvicorn', 'colorlog', 'itsdangerous'],
      extras_require={
          'test': ['pytest', 'pytest-cov', 'pytest-asyncio', 'async_asgi_testclient'],
          'dev': ['flake8', 'flake8-print', 'yapf'],
      },
      entry_points={
          'console_scripts': [
              'upnp-av-web-cp= upnpavcontrol.tools.web_control_point:main',
          ],
      },
      packages=find_packages())
