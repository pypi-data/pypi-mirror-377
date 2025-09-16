from pydantic import BaseModel, Field
from uuid import UUID, uuid4


class RequestIdentifier(BaseModel):
    id: UUID = Field(default_factory=uuid4, description="Request's Id.")
