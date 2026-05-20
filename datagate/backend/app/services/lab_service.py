from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from sqlalchemy.orm import Session


class LabService:
    def __init__(self, db: Session):
        self.db = db

    def get_analysis_url(self) -> str:
        from app.core.config import config

        parts = urlsplit(config.notebook_url)
        query = dict(parse_qsl(parts.query, keep_blank_values=True))
        if config.notebook_token and "token" not in query:
            query["token"] = config.notebook_token

        return urlunsplit(
            (
                parts.scheme,
                parts.netloc,
                parts.path,
                urlencode(query),
                parts.fragment,
            )
        )
