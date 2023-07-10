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


logging.basicConfig(filename=os.path.join(ROOT_DIR, conf_log_filename),
                    filemode='a',
                    format='%(asctime)s || %(name)s || %(levelname)s || %(module)s\n%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    news_list = []
    news_list = cointelegraph_parser.get_all_links(datetime(2023, 6, 5, 23, 59, tzinfo=pytz.UTC), datetime(2023, 6, 5, 0, 0, tzinfo=pytz.UTC))
    # news_list = coindesk_parser.get_all_links(datetime(2023, 6, 5, 23, 59, tzinfo=pytz.UTC), datetime(2023, 6, 5, 0, 0, tzinfo=pytz.UTC))
    # last_pars_time = get_last_pars_dt()
    # news_list = coindesk_parser.get_rss_links()
    session = get_sqlite_session('news_journal.sqlite')
    for item in news_list:
        try:
            if not is_parsed(session, item.link):
                tmp_article = cointelegraph_parser.get_article_info(item.link)
                # tmp_article = coindesk_parser.get_article_info(item.link)
            else:
                continue
        except src.core.structures.RequestErrorException as e:
            logger.error(f'\nGetting article error. href = {item.link}\n')
            continue
        file_full_name = save_to_disk(tmp_article)
        save_article_to_db(session, tmp_article, file_full_name)
    set_last_pars_dt()
