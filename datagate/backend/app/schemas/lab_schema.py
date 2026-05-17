from pydantic import BaseModel


class NotebookEmbedUrlOut(BaseModel):
    url: str
