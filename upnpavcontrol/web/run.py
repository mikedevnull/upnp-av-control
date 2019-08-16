import uvicorn


def run_web_api(av_control_point):
    from .application import app as web_app
    from . import application
    application._av_control_point_instance = av_control_point

    config = uvicorn.Config(web_app,
                            debug=True,
                            reload=True,
                            host='127.0.0.1',
                            port=8000)
    server = uvicorn.Server(config)

    return server.serve()
