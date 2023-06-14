from src.coindesk_parser import get_all_articles_coindeskcom,\
                                get_coindeskcom_articles_from_rss, \
                                parse_article_coindeskcom
from src.src import get_last_pars_dt, set_last_pars_dt, save_to_disk, read_from_disk, decompress_archive
from datetime import datetime


if __name__ == '__main__':
    news_list = []
    # news_list = get_all_articles_coindeskcom(datetime(2023, 6, 7, 23, 59), datetime(2023, 6, 5, 0, 0))
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
    decompress_archive('1350ca4f6883b027596b2d1e1bef2b215ccc5d5bf427c628f5dbdfd9a2b1cbee.xz')
    rd = read_from_disk('1350ca4f6883b027596b2d1e1bef2b215ccc5d5bf427c628f5dbdfd9a2b1cbee.xz')
    print(rd.href)
    print(rd.header)
    print(rd.publication_dt)
    print(rd.content)
    set_last_pars_dt()
