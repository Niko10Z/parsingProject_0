import time

import src.core.structures as structures
from src.const import ROOT_DIR, conf_log_filename
from src.resources import cointelegraph_parser, coindesk_parser
from src.core.local_storage import set_last_pars_dt, \
                    save_to_disk
from src.core.database import get_sqlite_session, save_article_to_db, is_parsed, SQLiteWorker
from datetime import datetime
import os
import logging
import pytz
import argparse
from typing import List


logging.basicConfig(filename=os.path.join(ROOT_DIR, conf_log_filename),
                    filemode='a',
                    format='%(asctime)s || %(name)s || %(levelname)s || %(module)s\n%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def handle_article(article: structures.ArticleShortInfo) -> None:
    try:
        if article.link.find('coindesk.com') != -1:
            local_parser = coindesk_parser
        elif article.link.find('cointelegraph.com') != -1:
            local_parser = cointelegraph_parser
        else:
            raise structures.ParsingErrorException(f'Parser for url {article.link} not found')
        sqlite_worker = SQLiteWorker('news_journal.sqlite')
        if not sqlite_worker.is_news_parsed(article.link):
            logger.info(f'Process link {article.link}')
            tmp_article = local_parser.get_article_info(article.link)
        else:
            logger.info(f'Link {article.link} already processed')
            return
    except structures.RequestErrorException as e:
        logger.error(f'\nGetting article error. href = {article.link}\n\n{e}')
        return
    logger.info(f'Save article from {article.link} to disk')
    file_full_name = save_to_disk(tmp_article)
    logger.info(f'Save info from {article.link} to DB')
    sqlite_worker.save_article_to_db(tmp_article, file_full_name)
    return


parser = argparse.ArgumentParser(description='News parsing args')
parser.add_argument('urls', help='Input urls list', nargs='*')
parsing_args = parser.parse_args()
for url_el in parsing_args.urls:
    logger.info(f'Start parsing for {url_el}')
    if url_el.find('coindesk.com') != -1:
        my_parser = coindesk_parser
    elif url_el.find('cointelegraph.com') != -1:
        my_parser = cointelegraph_parser
    else:
        raise structures.ParsingErrorException(f'Parser for url {url_el} not found')
    news_list = my_parser.get_all_links(datetime(2023, 6, 6, 23, 59, tzinfo=pytz.UTC), datetime(2023, 6, 6, 0, 0, tzinfo=pytz.UTC))
    # session = get_sqlite_session('news_journal.sqlite')
    start = time.time()
    for item in news_list:
        handle_article(item)
    logger.info(f'Processed all articles. Working time is {time.time() - start}')
    set_last_pars_dt()
