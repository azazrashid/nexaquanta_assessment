from pydantic import BaseModel


class BlogCreate(BaseModel):
    title: str
    content: str
    author_id: int


class BlogUpdate(BaseModel):
    title: str | None = None
    content: str | None = None


class BlogResponse(BaseModel):
    id: int
    title: str
    content: str
    author_id: int
