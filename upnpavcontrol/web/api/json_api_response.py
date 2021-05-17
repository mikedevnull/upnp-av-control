from fastapi.responses import JSONResponse


class JsonApiResponse(JSONResponse):
    media_type = 'application/vnd.api+json'