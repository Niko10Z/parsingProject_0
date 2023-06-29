import requests
from src.core.structures.custom_exceptions import RequestErrorException


def get_html_from_url(href: str, headers: dict = None, cookies: dict = None) -> str:
    if not headers:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
        }
    if not cookies:
        cookies = {}
    try:
        r = requests.get(href, headers=headers, cookies=cookies)
    except Exception as e:
        raise RequestErrorException('Invalid request', parent=e)
    try:
        r.raise_for_status()
    except Exception as e:
        raise RequestErrorException(f'Response error\nURL:{href}\nStatus:{r.status_code}\nReason:{r.reason}', parent=e)
    if not r.text.strip():
        raise RequestErrorException(f'Empty response body error')
    return r.text


def get_json_from_url(href: str, headers: dict = None, cookies: dict = None, json: dict = None) -> dict:
    if not headers:
        headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
        }
    if not cookies:
        cookies = {}

    # json_data = {
    #     'query': 'query TagPageQuery($short: String, $slug: String!, $order: String, $offset: Int!, $length: Int!) {\n  locale(short: $short) {\n    tag(slug: $slug) {\n      cacheKey\n      id\n      slug\n      avatar\n      createdAt\n      updatedAt\n      redirectRelativeUrl\n      alternates {\n        cacheKey\n        short\n        domain\n        id\n        code\n        __typename\n      }\n      tagTranslates {\n        cacheKey\n        id\n        title\n        metaTitle\n        pageTitle\n        description\n        metaDescription\n        keywords\n        __typename\n      }\n      posts(order: $order, offset: $offset, length: $length) {\n        data {\n          cacheKey\n          id\n          slug\n          views\n          postTranslate {\n            cacheKey\n            id\n            title\n            avatar\n            published\n            publishedHumanFormat\n            leadText\n            author {\n              cacheKey\n              id\n              slug\n              authorTranslates {\n                cacheKey\n                id\n                name\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          category {\n            cacheKey\n            id\n            __typename\n          }\n          author {\n            cacheKey\n            id\n            slug\n            authorTranslates {\n              cacheKey\n              id\n              name\n              __typename\n            }\n            __typename\n          }\n          postBadge {\n            cacheKey\n            id\n            label\n            postBadgeTranslates {\n              cacheKey\n              id\n              title\n              __typename\n            }\n            __typename\n          }\n          showShares\n          showStats\n          __typename\n        }\n        postsCount\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}',
    #     'operationName': 'TagPageQuery',
    #     'variables': {
    #         'slug': 'bitcoin',
    #         'order': 'postPublishedTime',
    #         'offset': 15,
    #         'length': 15,
    #         'short': 'en',
    #         'cacheTimeInMS': 300000,
    #     },
    # }

    response = requests.post(href, headers=headers, cookies=cookies, json=json)
    return response.json()
