from typing import List
from datetime import datetime

import pytz

from src.core.structures import ArticleShortInfo, ArticleInfo, ParsingErrorException
from src.core.networking import get_json_from_url, get_html_from_url
from bs4 import BeautifulSoup
import feedparser
from time import mktime
import logging
logger = logging.getLogger(__name__)


def get_one_page_links(news_tag: str, num_page: int, news_on_page: int = 15) -> List[ArticleShortInfo]:
    try:
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
        for i in json_data['data']['locale']['tag']['posts']['data']:
            logger.info(f'Parsing {i}')
            res_list.append(ArticleShortInfo(
                i['postBadge']['postBadgeTranslates'][0]['title'],
                i['postTranslate']['title'],
                f'https://cointelegraph.com/news/{i["slug"]}',
                i['postTranslate']['leadText'],
                str.strip(i['postTranslate']['author']['authorTranslates'][0]['name']),
                datetime.fromisoformat(i['postTranslate']['published'])
            ))
            # print(i)
            # print(i['slug'])
            # print(i['postTranslate']['title'])
            # print(i['postTranslate']['published'])
            # print(i['postTranslate']['leadText'])
            # print(i['postTranslate']['author']['slug'])
            # print(str.strip(i['postTranslate']['author']['authorTranslates'][0]['name']))
            # print(i['category'])
            # print(i['postBadge']['postBadgeTranslates'][0]['title'])
            # print('\n')
    except Exception as e:
        raise ParsingErrorException(f'Error by trying parse page {num_page}({news_on_page} news on page) of tag {news_tag}',
                                    parent=e)
    return res_list


def get_one_page_last_link(news_tag: str, num_page: int, news_on_page: int = 15) -> ArticleShortInfo:
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


def get_rss_links(from_dt: datetime = datetime.now(pytz.UTC), to_dt: datetime = None) -> List[ArticleShortInfo]:
    try:
        # TODO почему не радотает rss_parser
        # rss = Parser.parse(xml_data)
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


def get_article_info(href: str) -> ArticleInfo:
    html_info = get_html_from_url(href)

    try:
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


def get_news_tags() -> List[str]:
    html_info = get_html_from_url('https://cointelegraph.com/')
    soup = BeautifulSoup(html_info, "html.parser")
    return [el['href'][6:] for el in soup.select('div.header-zone > '
                'div.header-zone__menu > '
                'div.menu-desktop__row > '
                'nav > ul > '
                'li > div > '
                'span[data-gtm-locator="menubar_clickon_news"] + div > '
                'ul > li > a')]


def get_start_page(tag_name: str, from_dt: datetime) -> int:
    try:
        page_num = 1
        left, right = 1, page_num
        news_page_article = get_one_page_last_link(tag_name, page_num)
        # Идём вправо пока не перейдём первую (бОльшую) границу
        news_page_article.pub_datetime
        while news_page_article.pub_datetime > from_dt:
            page_num *= 2
            right = page_num
            news_page_article = get_one_page_last_link(tag_name, page_num)
        # Бинарным поиском ищем страницу начала
        while left < right:
            page_num = (left + right) // 2
            news_page_article = get_one_page_last_link(tag_name, page_num)
            if news_page_article.pub_datetime <= from_dt:
                right = page_num
            elif left < page_num:
                left = page_num
            else:
                page_num = right
                break
    except Exception as e:
        raise ParsingErrorException(f'Error by searching start page for tag "{tag_name}" and date {from_dt}', parent=e)
    return page_num


def get_all_one_tag_links(tag_name: str, from_dt: datetime, to_dt: datetime) -> List[ArticleShortInfo]:
    articles_list = []
    try:
        page_num = get_start_page(tag_name, from_dt)
        news_page_articles = get_one_page_links(tag_name, page_num)
        # Пока не выйдем за границу (меньшую) окна
        while news_page_articles[0].pub_datetime > to_dt:
            news_page_articles = get_one_page_links(tag_name, page_num)
            articles_list.extend(filter(lambda elem: from_dt >= elem.pub_datetime >= to_dt, news_page_articles))
            page_num += 1
    except Exception as e:
        raise ParsingErrorException(f'Gel all news of one tag by datetime error', parent=e)
    return articles_list


def get_all_links(from_dt: datetime, to_dt: datetime) -> List[ArticleShortInfo]:
    articles_list = []
    try:
        if not from_dt:
            from_dt = datetime.now(pytz.UTC)
        if not to_dt:
            from_dt = datetime(1970, 1, 1, 0, 0, 0, tzinfo=pytz.UTC)
        for news_tag in get_news_tags():
            logger.info(f'Try to find all {news_tag} news')
            articles_list.extend(get_all_one_tag_links(news_tag, from_dt, to_dt))
    except Exception as e:
        raise ParsingErrorException(f'ERROR in getting all news by datetime', parent=e)

    return articles_list
