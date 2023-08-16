import src.core.structures
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
        raise src.core.structures.ParsingErrorException(f'Parser for url {url_el} not found')
    news_list = my_parser.get_all_links(datetime(2023, 6, 6, 23, 59, tzinfo=pytz.UTC), datetime(2023, 6, 6, 0, 0, tzinfo=pytz.UTC))
    # session = get_sqlite_session('news_journal.sqlite')
    sqlite_worker = SQLiteWorker('news_journal.sqlite')
    for item in news_list:
        try:
            if not sqlite_worker.is_news_parsed(item.link):
                logger.info(f'Process link {item.link}')
                tmp_article = my_parser.get_article_info(item.link)
            else:
                logger.info(f'Link {item.link} already processed')
                continue
        except src.core.structures.RequestErrorException as e:
            logger.error(f'\nGetting article error. href = {item.link}\n')
            continue
        logger.info(f'Save to disk')
        file_full_name = save_to_disk(tmp_article)
        logger.info(f'Save info to DB')
        sqlite_worker.save_article_to_db(tmp_article, file_full_name)
    set_last_pars_dt()
