from __future__ import annotations

from pydantic import BaseModel


class DiasSemRegistro(BaseModel):
    @classmethod
    def from_xml(cls, xml: str) -> DiasSemRegistro: ...
