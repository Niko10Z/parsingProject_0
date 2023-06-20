import requests

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36',
}

json_data = {
    'query': 'query TagPageQuery($short: String, $slug: String!, $order: String, $offset: Int!, $length: Int!) {\n  locale(short: $short) {\n    tag(slug: $slug) {\n      cacheKey\n      id\n      slug\n      avatar\n      createdAt\n      updatedAt\n      redirectRelativeUrl\n      alternates {\n        cacheKey\n        short\n        domain\n        id\n        code\n        __typename\n      }\n      tagTranslates {\n        cacheKey\n        id\n        title\n        metaTitle\n        pageTitle\n        description\n        metaDescription\n        keywords\n        __typename\n      }\n      posts(order: $order, offset: $offset, length: $length) {\n        data {\n          cacheKey\n          id\n          slug\n          views\n          postTranslate {\n            cacheKey\n            id\n            title\n            avatar\n            published\n            publishedHumanFormat\n            leadText\n            author {\n              cacheKey\n              id\n              slug\n              authorTranslates {\n                cacheKey\n                id\n                name\n                __typename\n              }\n              __typename\n            }\n            __typename\n          }\n          category {\n            cacheKey\n            id\n            __typename\n          }\n          author {\n            cacheKey\n            id\n            slug\n            authorTranslates {\n              cacheKey\n              id\n              name\n              __typename\n            }\n            __typename\n          }\n          postBadge {\n            cacheKey\n            id\n            label\n            postBadgeTranslates {\n              cacheKey\n              id\n              title\n              __typename\n            }\n            __typename\n          }\n          showShares\n          showStats\n          __typename\n        }\n        postsCount\n        __typename\n      }\n      __typename\n    }\n    __typename\n  }\n}',
    'operationName': 'TagPageQuery',
    'variables': {
        'slug': 'bitcoin',
        'order': 'postPublishedTime',
        'offset': 15,
        'length': 15,
        'short': 'en',
        'cacheTimeInMS': 300000,
    },
}

response = requests.post('https://conpletus.cointelegraph.com/v1/', headers=headers, json=json_data)

for i in response.json()['data']['locale']['tag']['posts']['data']:
    print(i)
    print(i['slug'])
    print(i['postTranslate']['title'])
    print(i['postTranslate']['published'])
    print(i['postTranslate']['leadText'])
    print(i['postTranslate']['author']['slug'])
    print(str.strip(i['postTranslate']['author']['authorTranslates'][0]['name']))
    print(i['category'])
    print(i['postBadge']['postBadgeTranslates'][0]['title'])
    print('\n')
