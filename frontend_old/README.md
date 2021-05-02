UPnP AV Control Frontend
[![Build Status](https://travis-ci.com/mikedevnull/upnp-av-control-frontend.svg?branch=master)](https://travis-ci.com/mikedevnull/upnp-av-control-frontend)
[![codecov](https://codecov.io/gh/mikedevnull/upnp-av-control-frontend/branch/master/graph/badge.svg)](https://codecov.io/gh/mikedevnull/upnp-av-control-frontend)
====

Web frontend to [upnp-av-control](https://github.com/mikedevnull/upnp-av-control), a web-based API to control UPnP AV devices.

A simple web application to provide a user interface for the upnp av control backend.

## A word of warning

As with the upnp-av-control backend project, please note that this project is unfinished, under active development and probably barely useful. It has been started to support one or more of my other side projects, which I may write about when there's actually something to tell.

In it's current state, it's probably not too useful for anybody else.

## Getting Started

### Prerequisites
A reasonably recent version of [Node.js](https://nodejs.org) is required.

In addition, a running version of the backend is required.
Please follow the instructions of the [upnp-av-control backend](https://github.com/mikedevnull/upnp-av-control). 

### Development setup

First install dependencies:

```sh
npm install
```

To run the development webpack dev server:

```sh
npm run dev
```

Finally, start the upnp av control backend (probably in another shell/terminal):

```sh
upnp-av-control -v -d
```

The webpack development server is configured to proxy all requests to the backend API listening on port 8080.

The verbose `-v` and debug `-d` flags can be omitted, but the additional information is very usefull during development.


### Building 

First install dependencies:

```sh
npm install
```

To create a production build:

```sh
npm run build
```

The final files can be found in the `./dist` folder.


## Deployment

Due to its active development state, there's no deployment documentation yet.

In essence, you may need to setup a webserver like [nginx](http://www.nginx.com) to serve the static files.

It needs to be configured to proxy all requests to the `/api` endpoint to the backend.
Additionally, you need to configure it to support HTML5 history mode used by ´vue-router`.
The [vue router documentation](https://router.vuejs.org/guide/essentials/history-mode.html) and the [Vue CLI deployment guide](https://cli.vuejs.org/guide/deployment.html) offers some useful information here


## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details
