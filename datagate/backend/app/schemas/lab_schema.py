from pydantic import BaseModel


class AnalysisEmbedUrlOut(BaseModel):
    url: str
