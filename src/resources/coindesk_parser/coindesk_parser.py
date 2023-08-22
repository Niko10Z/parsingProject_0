import math
import threading
import time

import pytz
import logging
from src.core import ArticleShortInfo, ArticleInfo
from src.core.structures.custom_exceptions import ParsingErrorException
from src.core.networking import get_html_from_url
from datetime import datetime
from typing import List
from bs4 import BeautifulSoup
import feedparser


__all__ = [
    'get_one_page_links',
    'get_rss_links',
    'get_all_links',
    'get_article_info'
    ]


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def get_one_page_links(news_tag: str, num_page: int) -> List[ArticleShortInfo]:
    page_html = get_html_from_url(f'https://www.coindesk.com{news_tag}{num_page}')
    try:
        logger.info(f'Getting news from page {num_page} by tag {news_tag}')
        soup = BeautifulSoup(page_html, "html.parser")
        short_news = soup.select('div.articleTextSection')
        news_list = []
        for ind, item in enumerate(short_news):
            logger.info(f'Parsing item {ind}')
            title = item.select_one('a.card-title')
            if title.attrs['href'].find('/video/') != -1:
                continue
            pub_date = item.select_one('div.timing-data > div.ac-publishing-date > div > span').text
            news_list.append(ArticleShortInfo(
                category=item.find('a', class_='category').text,
                title=title.text,
                link='https://coindesk.com' + title.attrs['href'],
                description=item.find('span', class_='content-text').text,
                author=item.find('a', class_='ac-author').text,
                pub_datetime=pytz.utc.localize(datetime.strptime(pub_date.replace('.', ''), '%b %d, %Y at %I:%M %p %Z'))
            ))
    except Exception as e:
        raise ParsingErrorException(f'Short news parsing error\n'
                                    f'Page URL:https://www.coindesk.com/tag/{news_tag}/{num_page}', parent=e)

    return news_list


def get_one_page_last_link(news_tag: str, num_page: int) -> ArticleShortInfo | None:
    page_html = get_html_from_url(f'https://www.coindesk.com{news_tag}{num_page}')
    try:
        logger.info(f'Getting last news from page {num_page}')
        soup = BeautifulSoup(page_html, "html.parser")
        # short_news = soup.find_all('div', class_='articleTextSection')
        short_news = soup.select('div.articleTextSection')
        last_index = len(short_news)-1
        last_news = short_news[last_index]
        # title = last_news.find('a', class_='card-title')
        title = last_news.select_one('a.card-title')
        while title.attrs['href'].find('/video/') != -1 and last_index > 0:
            last_index -= 1
            last_news = short_news[last_index]
            # title = last_news.find('a', class_='card-title')
            title = last_news.select_one('a.card-title')
        if title.attrs['href'].find('/video/') != -1:
            # raise ParsingErrorException(f'Short news parsing error\n'
            #                             f'Page URL:https://www.coindesk.com{news_tag}/{num_page}\n'
            #                             f'Last news is not parseble')
            return None
        # pub_date = last_news\
        #     .find('div', class_='timing-data')\
        #     .find('span', class_='typography__StyledTypography-owin6q-0 fUOSEs')\
        #     .text
        pub_date = last_news.select_one('div.timing-data > div.ac-publishing-date > div > span').text
        return ArticleShortInfo(
            category=last_news.find('a', class_='category').text,
            title=title.text,
            link='https://coindesk.com' + title.attrs['href'],
            description=last_news.find('span', class_='content-text').text,
            author=last_news.find('a', class_='ac-author').text,
            pub_datetime=pytz.utc.localize(datetime.strptime(pub_date.replace('.', ''), '%b %d, %Y at %I:%M %p %Z'))
        )
    except Exception as e:
        raise ParsingErrorException(f'Short news parsing error\n'
                                    f'Page URL:https://www.coindesk.com{news_tag}/{num_page}', parent=e)


def get_rss_links(from_dt: datetime = datetime.now(pytz.UTC), to_dt: datetime = None) -> List[ArticleShortInfo]:
    try:
        # TODO почему не радотает rss_parser
        # rss = Parser.parse(xml_data)
        logger.info('Get links from RSS')
        rss = feedparser.parse('https://www.coindesk.com/arc/outboundfeeds/rss/')
        news_list = []
        for item in rss.entries:
            if item.link.find('/video/') != -1:
                continue
            tmp_news = ArticleShortInfo(
                category=item.tags[0]['term'],
                title=item.title,
                link=item.link,
                description=item.summary,
                author=item.author,
                pub_datetime=datetime.fromtimestamp(time.mktime(item.published_parsed))
            )
            if to_dt:
                if to_dt <= tmp_news.pub_datetime <= from_dt:
                    news_list.append(tmp_news)
            else:
                if tmp_news.pub_datetime <= from_dt:
                    news_list.append(tmp_news)
    except Exception as e:
        raise ParsingErrorException(f'RSS parsing error', parent=e)
    return news_list


def get_news_tags() -> List[str]:
    html_info = get_html_from_url('https://coindesk.com')
    try:
        logger.info(f'Searching news tags')
        soup = BeautifulSoup(html_info, "html.parser")
        return [el['href'] for el in soup.select('header.sticky-header > '
                    'div > '
                    'div[data-module-name="main-navigation"] > '
                    'div[data-submodule-name="subrow"] > '
                    'nav > ul > '
                    'li > a[href="/web3/"] + div > div > div > div > div > ul > li > a')]
    except Exception as e:
        raise ParsingErrorException('Getting news tags error', parent=e)


def get_start_page(tag_name: str, from_dt: datetime) -> int:
    try:
        logger.info(f'Search start page for tag {tag_name}')
        page_num = 1
        left, right = 1, page_num
        news_page_article = get_one_page_last_link(tag_name, page_num)
        while not news_page_article:
            left = right = page_num = page_num + 1
            news_page_article = get_one_page_last_link(tag_name, page_num)
        # Идём вправо пока не перейдём первую (бОльшую) границу
        while news_page_article.pub_datetime > from_dt:
            page_num *= 2
            right = page_num
            news_page_article = get_one_page_last_link(tag_name, page_num)
        # Бинарным поиском ищем страницу начала
        while left < right:
            page_num = math.ceil((left + right) / 2)
            news_page_article = get_one_page_last_link(tag_name, page_num)
            if news_page_article.pub_datetime <= from_dt and right > page_num:
                right = page_num
            elif left < page_num:
                left = page_num
            else:
                page_num = right
                break
        return page_num
    except Exception as e:
        raise ParsingErrorException(f'Error by searching start page for tag "{tag_name}" and date {from_dt}', parent=e)


def get_all_one_tag_links(tag_name: str, from_dt: datetime, to_dt: datetime) -> List[ArticleShortInfo]:
    articles_list = []
    try:
        logger.info(f'Get news on tag "{tag_name}"')
        page_num = get_start_page(tag_name, from_dt)
        news_page_articles = get_one_page_links(tag_name, page_num)
        # Пока не выйдем за границу (меньшую) окна
        while news_page_articles[0].pub_datetime > to_dt:
            articles_list.extend(filter(lambda elem: from_dt >= elem.pub_datetime >= to_dt, news_page_articles))
            page_num += 1
            news_page_articles = get_one_page_links(tag_name, page_num)
    except Exception as e:
        raise ParsingErrorException(f'Get all news of one tag by datetime error', parent=e)
    return articles_list


def threading_get_all_one_tag_links(articles_list: List[ArticleShortInfo], tag_name: str, from_dt: datetime, to_dt: datetime):
    try:
        logger.info(f'Get news on tag "{tag_name}"')
        page_num = get_start_page(tag_name, from_dt)
        news_page_articles = get_one_page_links(tag_name, page_num)
        # Пока не выйдем за границу (меньшую) окна
        while news_page_articles[0].pub_datetime > to_dt:
            articles_list.extend(filter(lambda elem: from_dt >= elem.pub_datetime >= to_dt, news_page_articles))
            page_num += 1
            news_page_articles = get_one_page_links(tag_name, page_num)
    except Exception as e:
        raise ParsingErrorException(f'Get all news of one tag by datetime error', parent=e)


def get_all_links(from_dt: datetime, to_dt: datetime) -> List[ArticleShortInfo]:
    articles_list = []
    try:
        logger.info(f'Get all "coindesk.com" links from {from_dt} to {to_dt}')
        if not from_dt:
            from_dt = datetime.now(pytz.UTC)
        if not to_dt:
            from_dt = datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)

        threads = list()
        for news_tag in get_news_tags():
            t = threading.Thread(target=threading_get_all_one_tag_links,
                                 args=(articles_list, news_tag, from_dt, to_dt,))
            threads.append(t)
            t.start()
        for index, thread in enumerate(threads):
            thread.join()

        # for news_tag in get_news_tags():
        #     articles_list.extend(get_all_one_tag_links(news_tag, from_dt, to_dt))
    except Exception as e:
        raise ParsingErrorException(f'Get all news by datetime error', parent=e)
    logger.info(f'Escape from get_all_links. Working time is {time.time() - start}')
    logger.info(f'Articles list length is {len(articles_list)}')
    return articles_list


def get_article_info(href: str) -> ArticleInfo:
    html_info = get_html_from_url(href)
    try:
        logger.info(f'Get article info from {href}')
        soup = BeautifulSoup(html_info, "html.parser")

        header = soup.select_one('.at-headline').text
        content = soup.select_one('.at-subheadline').text
        content += '\n'.join(i.text for i in soup.select('.at-content-section'))
        publication_dt = pytz.utc.localize(datetime\
                      .strptime(soup
                      .select_one(':is(div.at-created > div > span, div.block-item > span > span.fUOSEs)')
                      .text
                      .replace('.', ''), "%b %d, %Y at %I:%M %p %Z"))  # %r)
        parsing_dt = datetime.now(pytz.UTC)
        language = soup.select_one('div[data-module-name="footer/footer-select"] > button').text
        ainfo = ArticleInfo(header=header,
                            content=content,
                            publication_dt=publication_dt,
                            parsing_dt=parsing_dt,
                            language=language,
                            html=html_info,
                            href=href)
    except Exception as e:
        raise ParsingErrorException(f'coindesk.com article parsing error.\nURL: {href}', parent=e)

    return ainfo
