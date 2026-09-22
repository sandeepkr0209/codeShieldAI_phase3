"""
Pydantic schemas for the application map (WebPage / Endpoint).
"""
import uuid
from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WebPageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    url: str
    title: str | None
    status_code: int | None
    form_count: int
    link_count: int
    created_at: datetime


class EndpointRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    method: str
    url: str
    parameters_json: str | None
    response_headers_json: str | None
    cookies_json: str | None
    source: str
    created_at: datetime
