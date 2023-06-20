from typing import NamedTuple
from datetime import datetime


class ArticleInfo(NamedTuple):
    header: str
    content: str
    publication_dt: datetime
    parsing_dt: datetime
    html: str
    href: str
    language: str
