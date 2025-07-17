"""
Request / response schemas for documents.
"""

from typing import Dict
from pydantic import BaseModel, field_validator


class DocumentIn(BaseModel):
    """
    Payload received when the client wants to index or update a document.
    """
    identifier: str
    body: Dict[str, str]

    @field_validator("body")
    @classmethod
    def no_empty_body(cls, v: Dict[str, str]):
        if not v:
            raise ValueError("body must contain at least one language key")
        return v


class DocumentOut(DocumentIn):
    """
    DTO returned back to client – identical to DocumentIn for now.
    """
    pass
