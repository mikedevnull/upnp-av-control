from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(name='upnpavcontrol',
      description='UPNP AV control point library',
      version='0.0.1',
      url='https://github.com/mikedevnull/upnp-av-control',
      author='Michael Meier',
      author_email='michael-meier@bluesheep.de',
      long_description=long_description,
      long_description_content_type="text/markdown",
      license='MIT License',
      python_requires='>=3.7',
      classifiers=[
          "Programming Language :: Python :: 3", "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent", "Development Status :: 2 - Pre-Alpha",
          "Topic :: Multimedia :: Sound/Audio :: Players"
      ],
      install_requires=[
          'async_upnp_client', 'fastapi', 'websockets', 'defusedxml', 'uvicorn', 'colorlog', 'itsdangerous',
          'typing_extensions; python_version < "3.8"', 'PyYAML', 'aiofiles'
      ],
      extras_require={
          'test': ['pytest', 'pytest-cov', 'pytest-asyncio', 'pytest-bdd', 'async_asgi_testclient'],
          'dev': ['flake8', 'flake8-print', 'yapf'],
      },
      entry_points={
          'console_scripts': [
              'upnp-av-web-cp= upnpavcontrol.tools.web_control_point:main',
          ],
      },
      packages=find_packages(),
      include_package_data=True,
      zip_safe=False)
