from pydantic import BaseModel, Field
from typing import List, Optional


class UserClaims(BaseModel):
    sub: str
    email: Optional[str] = None
    roles: Optional[List[str]] = Field(default_factory=list)
    token: str
