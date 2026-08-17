from typing import Generic, TypeVar

from fastapi import Request
from pydantic import BaseModel

T = TypeVar("T")


class ResponseMeta(BaseModel):
    request_id: str


class PageMeta(ResponseMeta):
    limit: int
    next_cursor: str | None = None


class ApiResponse(BaseModel, Generic[T]):
    data: T
    meta: ResponseMeta


class ApiPageResponse(BaseModel, Generic[T]):
    data: list[T]
    meta: PageMeta


class ErrorDetail(BaseModel):
    code: str
    message: str
    details: object | None = None


class ErrorResponse(BaseModel):
    error: ErrorDetail
    meta: ResponseMeta


def response_meta(request: Request) -> ResponseMeta:
    return ResponseMeta(request_id=getattr(request.state, "request_id", "unknown"))


def page_meta(request: Request, *, limit: int, next_cursor: str | None) -> PageMeta:
    return PageMeta(
        request_id=getattr(request.state, "request_id", "unknown"),
        limit=limit,
        next_cursor=next_cursor,
    )
