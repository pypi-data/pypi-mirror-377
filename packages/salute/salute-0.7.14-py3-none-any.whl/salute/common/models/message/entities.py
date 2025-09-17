from typing import Any

from pydantic import BaseModel


class Entities(BaseModel):
    NUM_TOKEN: list[dict[str, Any]] = []
