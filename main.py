from resources import coindesk_parser
from src.main import get_last_pars_dt, \
                    set_last_pars_dt, \
                    save_to_disk, \
                    read_from_disk, \
                    decompress_archive
from datetime import datetime
import os
import logging


logging.basicConfig(filename=os.path.join(ROOT_DIR, conf_log_filename),
                    filemode='a',
                    format='%(asctime)s %(name)s %(levelname)s \n%(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S',
                    level=logging.DEBUG)
logger = logging.getLogger(__name__)


if __name__ == '__main__':
    news_list = []
    # news_list = get_all_articles_coindeskcom(datetime(2023, 6, 7, 23, 59), datetime(2023, 6, 5, 0, 0))
    last_pars_time = get_last_pars_dt()
    # news_list = get_coindeskcom_articles_from_rss(from_dt=datetime.now(), to_dt=last_pars_time)
    # news_list = get_coindeskcom_articles_from_rss(from_dt=datetime.now())
    for item in news_list:
        if item.link.find('/video/') != -1:
            continue
        tmp_article = coindesk_parser.parse_article(item.link)
        if not tmp_article:
            continue
        save_to_disk(tmp_article)
    set_last_pars_dt()
