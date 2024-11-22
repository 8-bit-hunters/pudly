from pydantic import BaseModel


class Error(BaseModel):
    message: str
    status: int


class HttpResponse(BaseModel):
    errors: list[Error]
