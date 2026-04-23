from pydantic import BaseModel

class SearchRequest(BaseModel):
    query: str
    finalidade: str | None = None
