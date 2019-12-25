UPnP AV Control
[![Build Status](https://travis-ci.org/mikedevnull/upnp-av-control.svg?branch=master)](https://travis-ci.org/mikedevnull/upnp-av-control)
[![codecov](https://codecov.io/gh/mikedevnull/upnp-av-control/branch/master/graph/badge.svg)](https://codecov.io/gh/mikedevnull/upnp-av-control)
====

Web API to control UPnP AV devices.

Implementation of an UPnP AV ControlPoint that exposes a Web API and can be controlloed via HTTP.
It's probably most useful with its sibling project that provides a frontend application that uses this API.

## A word of warning

Please note that this project is under unfinished, under active development and probably barely useful.
It has been started to support one or more of my other side projects, which I may write about when there's actually something to tell.

Even more, this project is a wonderful playground to learn about interesting things, i.e. python async programming, fastapi, the upnp (av) stack, etc.
This essentially means that there's a good chance that this project will never be finished or useful by any means.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

A working Python 3.6+ interpreter is required.

It is also probably a good idea (though not neccessary) to create and use a [virtual environment](https://docs.python-guide.org/dev/virtualenvs/) for testing and development.

### Installing

The control point can be installed directly using `pip`:

```bash
pip install git+https://github.com/mikedevnull/upnp-av-control
```

#### Development mode

For active development it might be more reasonable to clone a local copy first

```bash
git clone git+https://github.com/mikedevnull/upnp-av-control
```

and install the software in development mode:

```bash
cd upnp-av-control
pip install -e .[dev,test]
````

The above command will also install the extra components useful for development (`dev`) and required for testing (`test`).

Please refer to the [pip documentation](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs) for more details.

## Usage

To start the control point server, simply run

```bash
upnp-av-web-cp
```

This will start a [uvicorn](https://github.com/encode/uvicorn)-based local development server with hot reloading listening on `http://127.0.0.1:8000`.

Direct your browser to `http://127.0.0.1:8000/docs` for the interactive API documentation.

Run 
```bash
upnp-av-web-cp --help
``` 

to see all available options.

## Running the tests

If the `test` extra requirements have been installed, running the tests is as simple as executing `pytest`

```bash
pytest
```

## Deployment

Due to the lack of functionality there's no deployment documentation yet.

> **WARNING**: As with UPnP services in general, exposing this web service to the public (i.e. the internal) **might pose a severe security risk** and is not the intendend use case.

> **WARNING**: The development server startet by `upnp-av-web-cp` is configured for development and **not** ready for production use.

## Built With

* [FastAPI]() - The web framework used
* [async-upnp-aclient](https://maven.apache.org/) - Async UPnP framework that does the actual heavy lifting

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks to [PurpleBooth](https://github.com/PurpleBooth) for the README template
