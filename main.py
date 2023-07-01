from src.const import ROOT_DIR, conf_log_filename
from src.resources import coindesk_parser
from src.resources import cointelegraph_parser
from src.core.local_storage import get_last_pars_dt, \
                    set_last_pars_dt, \
                    save_to_disk
from datetime import datetime
import os
import logging


logging.basicConfig(filename=os.path.join(ROOT_DIR, conf_log_filename),
                    filemode='a',
                    format='%(asctime)s || %(name)s || %(levelname)s || %(module)s\n%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    news_list = []
    news_list = cointelegraph_parser.get_all_links(datetime(2023, 6, 7, 23, 59), datetime(2023, 6, 5, 0, 0))
    # last_pars_time = get_last_pars_dt()
    # news_list = coindesk_parser.get_rss_links()
    for item in news_list:
        tmp_article = cointelegraph_parser.get_article_info(item.link)
        if not tmp_article:
            continue
        save_to_disk(tmp_article)
    set_last_pars_dt()
