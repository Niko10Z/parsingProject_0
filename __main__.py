import src.core.structures
from src.const import ROOT_DIR, conf_log_filename
from src.resources import cointelegraph_parser, coindesk_parser
from src.core.local_storage import set_last_pars_dt, \
                    save_to_disk
from src.core.database import get_sqlite_session, save_article_to_db, is_parsed
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


parser = argparse.ArgumentParser(description='urls to parse news')
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

    news_list = my_parser.get_all_links(datetime(2023, 6, 5, 23, 59, tzinfo=pytz.UTC), datetime(2023, 6, 5, 0, 0, tzinfo=pytz.UTC))
    session = get_sqlite_session('news_journal.sqlite')
    for item in news_list:
        try:
            if not is_parsed(session, item.link):
                tmp_article = my_parser.get_article_info(item.link)
            else:
                continue
        except src.core.structures.RequestErrorException as e:
            logger.error(f'\nGetting article error. href = {item.link}\n')
            continue
        file_full_name = save_to_disk(tmp_article)
        save_article_to_db(session, tmp_article, file_full_name)
    set_last_pars_dt()
