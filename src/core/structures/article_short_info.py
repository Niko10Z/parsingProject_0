from typing import NamedTuple
from datetime import datetime


class ArticleShortInfo(NamedTuple):
    category: str
    title: str
    link: str
    description: str
    author: str
    pub_datetime: datetime
