import hashlib
import logging
from sqlalchemy import create_engine, Connection
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlalchemy.exc import OperationalError
from sqlalchemy_utils import database_exists, create_database
from datetime import datetime
from src.const import ROOT_DIR
from src.conf import dir_name_database
from src.core.structures import ArticleInfo
from src.core.structures import DataBaseErrorException


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


Base = declarative_base()
metadata = Base.metadata


class BaseModel(Base):
    __abstract__ = True

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    #
    # def __repr__(self):
    #     return "<{0.__class__.__name__}(id={0.id!r})>".format(self)


class ArticleLink(BaseModel):
    __tablename__ = 'article_links'

    def __init__(self, href, slug, published_dt, parsed_dt, article_parser_version, article_archive_file_path):
        self.href = href
        self.slug = slug
        self.published_dt = published_dt
        self.parsed_dt = parsed_dt
        self.article_parser_version = article_parser_version
        self.article_archive_file_path = article_archive_file_path

    href = Column(String(3000), nullable=False)
    slug = Column(String(255), nullable=False)
    published_dt = Column(DateTime, nullable=True)
    # article_resource_id
    parsed_dt = Column(DateTime, nullable=True)
    article_parser_version = Column(Integer)
    article_archive_file_path = Column(String(1000))


def get_sqlite_session(db_name: str) -> Session:
    engine = create_engine(f"sqlite:///{ROOT_DIR}{dir_name_database}/{db_name}")
    if not database_exists(engine.url):
        create_database(engine.url)
        # В метадате будут схемы всех наследников Base
        # создаём все схемы(таблицы) в базу ассоциированную с engine
        metadata.create_all(bind=engine)
    # Создаём КЛАСС для создания сессий к КОНКРЕТНОЙ БД(фабрику)
    return sessionmaker(bind=engine)()


def save_article_to_db(session: Session, article_info: ArticleInfo, file_full_name: str):
    try:
        if article_link := session.query(ArticleLink).filter_by(href=article_info.href).first():
            article_link.article_archive_file_path = file_full_name
            article_link.published_dt = article_info.publication_dt
            article_link.parsed_dt = article_info.parsing_dt
        else:
            session.add(ArticleLink(article_info.href,
                                    hashlib.sha256(article_info.href.encode()).hexdigest(),
                                    article_info.publication_dt,
                                    article_info.parsing_dt,
                                    0,
                                    file_full_name))
        session.commit()
    except Exception as e:
        raise DataBaseErrorException(f'Save article to DB error', parent=e)


def get_article_from_db(session: Session, href: str) -> ArticleLink | None:
    return session.query(ArticleLink).filter_by(href=href).first()


def is_parsed(session: Session, href: str) -> bool:
    try:
        if session.query(ArticleLink).filter_by(href=href).first().article_archive_file_path:
            return True
        return False
    except AttributeError:
        return False
    except Exception as e:
        raise DataBaseErrorException(f'Searching ArticleLink object error', parent=e)


def set_archive_path(session: Session, href: str, path: str) -> None:
    try:
        session.query(ArticleLink).filter_by(href=href).first().article_archive_file_path = path
        return
    except AttributeError:
        raise DataBaseErrorException(f'Set archive path error. Record not found')
    except Exception as e:
        raise DataBaseErrorException(f'Set archive path error.', parent=e)


def get_db_connection(db_name: str = 'news_journal.sqlite') -> Connection:
    engine = create_engine(f"sqlite:///{ROOT_DIR}{dir_name_database}/{db_name}")
    if not database_exists(engine.url):
        create_database(engine.url)
    return engine.connect()


class SQLiteWorker:

    session: Session

    def __init__(self, db_name: str):
        if not db_name:
            raise DataBaseErrorException('Empty DB name')
        try:
            engine = create_engine(f"sqlite:///{ROOT_DIR}{dir_name_database}/{db_name}")
            if not database_exists(engine.url):
                try:
                    create_database(engine.url)
                    metadata.create_all(bind=engine)
                except OperationalError as e:
                    logger.warning(e)
            # if not database_exists(engine.url):
            #     create_database(engine.url)
            #     # В метадате будут схемы всех наследников Base
            #     # создаём все схемы(таблицы) в базу ассоциированную с engine
            #     metadata.create_all(bind=engine)
            # Создаём КЛАСС для создания сессий к КОНКРЕТНОЙ БД(фабрику) и вызываем его
            self.session = sessionmaker(bind=engine)()
        except Exception as e:
            raise DataBaseErrorException('Creating SQLite worker error', parent=e)

    def is_news_parsed(self, href: str) -> bool:
        try:
            if self.session.query(ArticleLink).filter_by(href=href).first().article_archive_file_path:
                return True
            return False
        except AttributeError:
            return False
        except Exception as e:
            raise DataBaseErrorException(f'Searching ArticleLink object error', parent=e)

    def save_article_to_db(self, article_info: ArticleInfo, file_full_name: str):
        try:
            if article_link := self.session.query(ArticleLink).filter_by(href=article_info.href).first():
                article_link.article_archive_file_path = file_full_name
                article_link.published_dt = article_info.publication_dt
                article_link.parsed_dt = article_info.parsing_dt
            else:
                self.session.add(ArticleLink(
                    article_info.href,
                    hashlib.sha256(article_info.href.encode()).hexdigest(),
                    article_info.publication_dt,
                    article_info.parsing_dt,
                    0,
                    file_full_name))
            self.session.commit()
            self.session.flush()
        except Exception as e:
            raise DataBaseErrorException(f'Save article to DB error', parent=e)
