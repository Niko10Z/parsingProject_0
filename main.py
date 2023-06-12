from src.coindesk_parser import get_all_articles_coindeskcom,\
                                get_coindeskcom_articles_from_rss, \
                                parse_article_coindeskcom
from src.src import get_last_pars_dt, set_last_pars_dt, save_to_disk
from datetime import datetime


if __name__ == '__main__':
    news_list = get_all_articles_coindeskcom(datetime(2023, 6, 7, 23, 59), datetime(2023, 6, 1, 0, 0))
    last_pars_time = get_last_pars_dt()
    # news_list = get_coindeskcom_articles_from_rss(from_dt=datetime.now(), to_dt=last_pars_time)
    # news_list = get_coindeskcom_articles_from_rss(from_dt=datetime.now())
    for item in news_list:
        if item.link.find('/video/') != -1:
            continue
        tmp_article = parse_article_coindeskcom(item.link)
        if not tmp_article:
            continue
        save_to_disk(tmp_article)

    set_last_pars_dt()
