from typing import List
from datetime import datetime
from src.core.structures import ArticleShortInfo, ArticleInfo, ParsingErrorException
from src.core.networking import get_json_from_url, get_html_from_url
from bs4 import BeautifulSoup
import feedparser
from time import mktime


def get_one_page_links(news_tag: str, num_page: int, news_on_page: int = 50) -> List[ArticleShortInfo]:
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
    json_data = get_json_from_url('https://conpletus.cointelegraph.com/v1/', json=json_reqv)
    res_list = []
    for i in json_data['data']['locale']['tag']['posts']['data']:
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
        
    return res_list


def get_rss_links(from_dt: datetime = datetime.now(), to_dt: datetime = None) -> List[ArticleShortInfo]:
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
            soup.select('div.post-meta > div.post-meta__publish-date > time')[0]['datetime'])
        parsing_dt = datetime.now()
        language = soup.select('header.header-desktop > '
                               'div.header-desktop__row > '
                               'div.header-side-links > '
                               'ul > '
                               'li:first-child > '
                               'div.header-side-links__select')[0].text
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


for el in get_rss_links():
    print(el)
pass
