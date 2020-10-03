UPnP AV Control
![Build Status](https://github.com/mikedevnull/upnp-av-control/workflows/Tests/badge.svg)
[![codecov](https://codecov.io/gh/mikedevnull/upnp-av-control/branch/master/graph/badge.svg)](https://codecov.io/gh/mikedevnull/upnp-av-control)
====

Web frontend and API to control UPnP AV devices.

Implementation of an UPnP AV ControlPoint. It consists of a backend written in python that exposes a web API over HTTP, and a simple HTML/JS/CSS frontend.

## A word of warning

Please note that this project is under unfinished, under active development and probably barely useful.
It has been started to support one or more of my other side projects, which I may write about when there's actually something to tell.

Even more, this project is a wonderful playground to learn about interesting things, i.e. python async programming, fastapi, the upnp (av) stack, etc.
This essentially means that there's a good chance that this project will never be finished or useful by any means.

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites

A working Python 3.7+ interpreter is required.

It is also probably a good idea (though not neccessary) to create and use a [virtual environment](https://docs.python-guide.org/dev/virtualenvs/) for testing and development.

When building from source or for development, a reasonably recent version of [Node.js](https://nodejs.org/) (e.g. 12.x) is required for the web frontend.

### Installation and building from source

Clone a copy of the repository

```bash
git clone git+https://github.com/mikedevnull/upnp-av-control
cd upnp-av-control
```

One can choose to build the frontend, the backend or both.

#### Backend

To install the backend in development mode:
```bash
pip install -e .[dev,test]
```

The above command will also install the extra components useful for development (`dev`) and required for testing (`test`).

Please refer to the [pip documentation](https://pip.pypa.io/en/stable/reference/pip_install/#editable-installs) for more details.


#### Frontend

Install the required node modules with `npm:
```
npm install
```

#### Development server

Both the backend and frontend can be run with a development server, including (hot-)reloading and other nice features useful during development.

For active development, both development servers can be started with the `dev` npm script:

```bash
npm run dev
```

This will start a  `webpack-dev-server` on port `8080` serving the frontend, proxying all backend requests to a backend `uvicorn` server in development mode on port `8000` , both configured to work together nicely.

The result should be accessible on `http://localhost:8080`.

### Running the tests

#### Backend

If the `test` extra requirements have been installed, running the tests is as simple as executing `pytest`

```bash
pytest
```

#### Frontend

The frontend tests can be run with the npm `test` script

```bash
npm run test
```

## Usage

First, the frontend should be build
```bash
npm run build
```

If you are only interested in using the backend web API, you may obmit this step.

To start the control point server, simply run

```bash
upnp-av-web-cp
```

This will start a [uvicorn](https://github.com/encode/uvicorn)-based local  server on `http://127.0.0.1:8000`.

Direct your browser to `http://127.0.0.1:8000/docs` for the interactive API documentation.

Run 
```bash
upnp-av-web-cp --help
``` 

to see all available options.


## Deployment

Due to the lack of functionality there's no deployment documentation yet.

> **WARNING**: As with UPnP services in general, exposing this web service to the public (i.e. the internet) **might pose a severe security risk** and is not the intendend use case.

> **WARNING**: The development server startet by `upnp-av-web-cp` is configured for development and **not** ready for production use.

## Built With

* [FastAPI](https://fastapi.tiangolo.com/) - The web framework used
* [async-upnp-aclient](https://github.com/StevenLooman/async_upnp_client) - Async UPnP framework that does the actual heavy lifting
* [Vue.js](https://www.vuejs.org) - The frontend web framework

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgments

* Thanks to [PurpleBooth](https://github.com/PurpleBooth) for the README template
