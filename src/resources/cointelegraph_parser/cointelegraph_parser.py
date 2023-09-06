import math
import time
from typing import List
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor

import pytz

from src.core.structures import ArticleShortInfo, ArticleInfo, ParsingErrorException
from src.core.networking import get_json_from_url, get_html_from_url
from bs4 import BeautifulSoup
import feedparser
from time import mktime
import logging


__all__ = [
    'get_one_page_links',
    'get_rss_links',
    'get_all_links',
    'get_article_info'
]


logger = logging.getLogger(__name__)
logger.addHandler(logging.StreamHandler())


def get_one_page_links(news_tag: str, num_page: int, news_on_page: int = 15) -> List[ArticleShortInfo]:
    try:
        logger.info(f'Getting news from page {num_page} for tag {news_tag}')
        json_reqv = {
            'query': 'query TagPageQuery($short: String, $slug: String!, $order: String, $offset: Int!, $length: Int!) {\n  locale(short: $short) {\n    tag(slug: $slug) {\n      cacheKey\n      id\n      slug\n      avatar\n      createdAt\n      updatedAt\n      redirectRelativeUrl\n      alternates {\n        cacheKey\n        short\n        domain\n        id\n        code\n        __typename\n      }\n      tagTranslates {\n        cacheKey\n        id\n        title\n        metaTitle\n        pageTitle\n        description\n        metaDescription\n        keywords\n        __typename\n      }\n      posts(order: $order, offset: $offset, length: $length) {\n        data {\n          cacheKey\n          id\n          slug\n          views\n          postTranslate {\n            cacheKey\n            id\n            title\n            avatar\n            published\n            publishedHumanFormat\n            leadText\n            author {\n              cacheKey\n              id\n              slug\n              authorTranslates {\n                cacheKey\n                id\n                name\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          category {\n            cacheKey\n            id\n            __typename\n          }\n          author {\n            cacheKey\n            id\n            slug\n            authorTranslates {\n              cacheKey\n              id\n              name\n              __typename\n            }\n            __typename\n          }\n          postBadge {\n            cacheKey\n            id\n            label\n            postBadgeTranslates {\n              cacheKey\n              id\n              title\n              __typename\n            }\n            __typename\n          }\n          showShares\n          showStats\n          __typename\n        }\n        postsCount\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}',
            'operationName': 'TagPageQuery',
            'variables': {
                'slug': news_tag,
                'order': 'postPublishedTime',
                'offset': news_on_page*num_page,
                'length': news_on_page,
                'short': 'en',
                'cacheTimeInMS': 300000,
            },
        }
        logger.info(f'Try to get JSON for tag {news_tag}, page {num_page} ({news_on_page} on page)')
        json_data = get_json_from_url('https://conpletus.cointelegraph.com/v1/', json=json_reqv)
        res_list = []
        for ind, val in enumerate(json_data['data']['locale']['tag']['posts']['data']):
            logger.info(f'Parsing item {ind}')
            res_list.append(ArticleShortInfo(
                val['postBadge']['postBadgeTranslates'][0]['title'],
                val['postTranslate']['title'],
                f'https://cointelegraph.com/news/{val["slug"]}',
                val['postTranslate']['leadText'],
                str.strip(val['postTranslate']['author']['authorTranslates'][0]['name']),
                datetime.fromisoformat(val['postTranslate']['published'])
            ))
    except Exception as e:
        raise ParsingErrorException(f'Error by trying parse page {num_page}({news_on_page} news on page) of tag {news_tag}',
                                    parent=e)
    return res_list


def get_one_page_last_link(news_tag: str, num_page: int, news_on_page: int = 15) -> ArticleShortInfo:
    try:
        logger.info(f'Getting last news from page {num_page} and tag {news_tag}')
        json_reqv = {
            'query': 'query TagPageQuery($short: String, $slug: String!, $order: String, $offset: Int!, $length: Int!) {\n  locale(short: $short) {\n    tag(slug: $slug) {\n      cacheKey\n      id\n      slug\n      avatar\n      createdAt\n      updatedAt\n      redirectRelativeUrl\n      alternates {\n        cacheKey\n        short\n        domain\n        id\n        code\n        __typename\n      }\n      tagTranslates {\n        cacheKey\n        id\n        title\n        metaTitle\n        pageTitle\n        description\n        metaDescription\n        keywords\n        __typename\n      }\n      posts(order: $order, offset: $offset, length: $length) {\n        data {\n          cacheKey\n          id\n          slug\n          views\n          postTranslate {\n            cacheKey\n            id\n            title\n            avatar\n            published\n            publishedHumanFormat\n            leadText\n            author {\n              cacheKey\n              id\n              slug\n              authorTranslates {\n                cacheKey\n                id\n                name\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          category {\n            cacheKey\n            id\n            __typename\n          }\n          author {\n            cacheKey\n            id\n            slug\n            authorTranslates {\n              cacheKey\n              id\n              name\n              __typename\n            }\n            __typename\n          }\n          postBadge {\n            cacheKey\n            id\n            label\n            postBadgeTranslates {\n              cacheKey\n              id\n              title\n              __typename\n            }\n            __typename\n          }\n          showShares\n          showStats\n          __typename\n        }\n        postsCount\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}',
            'operationName': 'TagPageQuery',
            'variables': {
                'slug': news_tag,
                'order': 'postPublishedTime',
                'offset': news_on_page * num_page,
                'length': news_on_page,
                'short': 'en',
                'cacheTimeInMS': 300000,
            },
        }
        json_data = get_json_from_url('https://conpletus.cointelegraph.com/v1/', json=json_reqv)
        news_obj = json_data['data']['locale']['tag']['posts']['data'][-1]
        return ArticleShortInfo(
            news_obj['postBadge']['postBadgeTranslates'][0]['title'],
            news_obj['postTranslate']['title'],
            f'https://cointelegraph.com/news/{news_obj["slug"]}',
            news_obj['postTranslate']['leadText'],
            str.strip(news_obj['postTranslate']['author']['authorTranslates'][0]['name']),
            datetime.fromisoformat(news_obj['postTranslate']['published'])
        )
    except Exception as e:
        raise ParsingErrorException(f'Short news parsing error\n'
                                    f'Page URL:https://www.cointelegraph.com{news_tag}/{num_page}', parent=e)


def get_rss_links(from_dt: datetime = datetime.now(pytz.UTC), to_dt: datetime = None) -> List[ArticleShortInfo]:
    try:
        # TODO почему не радотает rss_parser
        # rss = Parser.parse(xml_data)
        logger.info('Get links from RSS')
        rss = feedparser.parse('https://cointelegraph.com/rss')
        news_list = []
        for item in rss.entries:
            tmp_news = ArticleShortInfo(
                title=item.title,
                link=item.link,
                pub_datetime=datetime.fromtimestamp(mktime(item.published_parsed)),
                author=item.author.replace('Cointelegraph By ', ''),
                category=item.get('tags', [{'term': 'Without category'}])[0]['term'],
                description=item.summary
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
    html_info = get_html_from_url('https://cointelegraph.com/')
    try:
        logger.info(f'Searching news tags')
        soup = BeautifulSoup(html_info, "html.parser")
        return [el['href'][6:] for el in soup.select('div.header-zone > '
                'div.header-zone__menu > '
                'div.menu-desktop__row > '
                'nav > ul > '
                'li > div > '
                'span[data-gtm-locator="menubar_clickon_news"] + div > '
                'ul > li > a')]
    except Exception as e:
        raise ParsingErrorException('Getting news tags error', parent=e)


def get_start_page(tag_name: str, from_dt: datetime) -> int:
    try:
        logger.info(f'Search start page for tag {tag_name}')
        page_num = 1
        left, right = 1, page_num
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
    except Exception as e:
        raise ParsingErrorException(f'Error by searching start page for tag "{tag_name}" and date {from_dt}', parent=e)
    logger.info(f'Start page for tag {tag_name} is {page_num}')
    return page_num


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
        raise ParsingErrorException(f'Gel all news of one tag by datetime error', parent=e)
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
        raise ParsingErrorException(f'Gel all news of one tag by datetime error', parent=e)


def get_all_links(from_dt: datetime, to_dt: datetime) -> List[ArticleShortInfo]:
    start = time.time()
    articles_list = []
    try:
        logger.info(f'Get all "cointelegraph.com" links from {from_dt} to {to_dt}')
        if not from_dt:
            from_dt = datetime.now(pytz.UTC)
        if not to_dt:
            from_dt = datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        # TODO get news of any tag in a separate thread
        # №1
        # threads = list()
        # for news_tag in get_news_tags():
        #     t = threading.Thread(target=threading_get_all_one_tag_links,
        #                          args=(articles_list, news_tag, from_dt, to_dt,))
        #     threads.append(t)
        #     t.start()
        # for index, thread in enumerate(threads):
        #     thread.join()

        # №2
        # news_tags = get_news_tags()
        # with ThreadPoolExecutor(max_workers=5) as executor:
        #     futures = [executor.submit(get_all_one_tag_links, *item) for item in zip(news_tags, [from_dt]*len(news_tags), [to_dt]*len(news_tags))]
        #     for future in as_completed(futures):
        #         if future.result():
        #             articles_list.extend(future.result())

        # №3
        news_tags = get_news_tags()
        with ThreadPoolExecutor(max_workers=5) as executor:
            for result in executor.map(get_all_one_tag_links,
                                       news_tags,
                                       [from_dt]*len(news_tags),
                                       [to_dt]*len(news_tags)):
                articles_list.extend(result)

        # №4
        # for news_tag in get_news_tags():
        #     logger.info(f'Try to find all {news_tag} news')
        #     articles_list.extend(get_all_one_tag_links(news_tag, from_dt, to_dt))

    except Exception as e:
        raise ParsingErrorException(f'ERROR in getting all news by datetime', parent=e)
    logger.info(f'Escape from get_all_links. Working time is {time.time()-start}')
    logger.info(f'Articles list length is {len(articles_list)}')
    return articles_list


def get_article_info(href: str) -> ArticleInfo:
    html_info = get_html_from_url(href)

    try:
        logger.info(f'Get article info from {href}')
        soup = BeautifulSoup(html_info, "html.parser")

        header = soup.select('h1.post__title')[0].text
        content = soup.select('p.post__lead')[0].text
        # TODO брать только бездетных
        content += '\n'.join(i.text for i in soup.select(':is(div.post-content > p, div.post-content > h2)'))
        publication_dt = datetime.fromisoformat(
            soup.select_one('div.post-meta > div.post-meta__publish-date > time')['datetime'])
        parsing_dt = datetime.now(pytz.UTC)
        language = soup.select_one('header.header-desktop > '
                               'div.header-desktop__row > '
                               'div.header-side-links > '
                               'ul > '
                               'li:first-child > '
                               'div.header-side-links__select').text
        ainfo = ArticleInfo(header=header,
                            content=content,
                            publication_dt=publication_dt,
                            parsing_dt=parsing_dt,
                            language=language,
                            html=html_info,
                            href=href)
    except Exception as e:
        raise ParsingErrorException(f'cointelegraph.com article parsing error.\nURL: {href}', parent=e)

    return ainfo
