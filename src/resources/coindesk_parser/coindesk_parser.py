from src.core import ArticleShortInfo, ArticleInfo
from src.core.networking.custom_exceptions import ParsingErrorException
from src.core.networking import get_html_from_url
from datetime import datetime
from typing import List
from bs4 import BeautifulSoup
import feedparser
from time import mktime


def get_one_page_links(news_tag: str, num_page: int) -> List[ArticleShortInfo]:
    page_html = get_html_from_url(f'https://www.coindesk.com/tag/{news_tag}/{num_page}')
    try:
        soup = BeautifulSoup(page_html, "html.parser")
        # short_news = soup.find_all('div', class_='articleTextSection')
        short_news = soup.select('div.articleTextSection')
        news_list = []
        for item in short_news:
            title = item.find('a', class_='card-title')
            if title.attrs['href'].find('/video/') != -1:
                continue
            pub_date = item\
                .find('div', class_='timing-data')\
                .find('span', class_='typography__StyledTypography-owin6q-0 fUOSEs')\
                .text
            news_list.append(ArticleShortInfo(
                category=item.find('a', class_='category').text,
                title=title.text,
                link='https://coindesk.com' + title.attrs['href'],
                description=item.find('span', class_='content-text').text,
                author=item.find('a', class_='ac-author').text,
                pub_datetime=datetime.strptime(pub_date.replace('.', ''), '%b %d, %Y at %I:%M %p %Z')
            ))
    except Exception as e:
        raise ParsingErrorException(f'Short news parsing error\n'
                                    f'Page URL:https://www.coindesk.com/tag/{news_tag}/{num_page}', parent=e)

    return news_list


def get_rss_links(from_dt: datetime = datetime.now(), to_dt: datetime = None) -> List[ArticleShortInfo]:
    try:
        # TODO почему не радотает rss_parser
        # rss = Parser.parse(xml_data)
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
                pub_datetime=datetime.fromtimestamp(mktime(item.published_parsed))
            )
            if to_dt:
                if to_dt <= tmp_news.pub_datetime <= from_dt:
                    news_list.append(tmp_news)
            else:
                news_list.append(tmp_news)
    except Exception as e:
        raise ParsingErrorException(f'RSS parsing error', parent=e)
    return news_list


def get_all_links(from_dt: datetime, to_dt: datetime) -> List[ArticleShortInfo]:
    web3_tags = [
        'yuga-labs',
        'nfts',
        'metaverse',
        'dao',
        'gaming'
    ]
    articles_list = []
    try:
        if not from_dt:
            from_dt = datetime.now()
        if not to_dt:
            from_dt = datetime(1970, 1, 1, 0, 0, 0)
        for w3_tag in web3_tags:
            page_num = 1
            left, right = 1, page_num
            news_page_articles = get_one_page_links(w3_tag, page_num)
            # Идём вправо пока не перейдём первую (бОльшую) границу
            # TODO get_last_coindeskcom_news_from_page
            while news_page_articles[-1].pub_datetime > from_dt:
                page_num *= 2
                right = page_num
                news_page_articles = get_one_page_links(w3_tag, page_num)
            # Бинарным поиском ищем страницу начала
            while left < right:
                page_num = (left + right) // 2
                news_page_articles = get_one_page_links(w3_tag, page_num)
                if news_page_articles[-1].pub_datetime <= from_dt:
                    right = page_num
                elif left < page_num:
                    left = page_num
                else:
                    page_num = right
                    break
            # Пока не выйдем за границу (меньшую) окна
            while news_page_articles[0].pub_datetime > to_dt:
                news_page_articles = get_one_page_links(w3_tag, page_num)
                articles_list.extend(filter(lambda elem: from_dt >= elem.pub_datetime >= to_dt, news_page_articles))
                page_num += 1
    except Exception as e:
        raise ParsingErrorException(f'Gel all news by datetime error', parent=e)

    return articles_list


def get_article_info(href: str) -> ArticleInfo:
    html_info = get_html_from_url(href)
    # content_classes = [
    #     'common-textstyles__StyledWrapper-sc-18pd49k-0 eSbCkN',
    #     'headingstyles__StyledWrapper-l955mv-0 fMEozb',
    #     'liststyles__StyledWrapper-sc-13iatdm-0 eksenZ'
    # ]

    try:
        soup = BeautifulSoup(html_info, "html.parser")

        # header = soup.find('div', class_='at-headline').text
        header = soup.select('.at-headline')[0].text
        # content = soup.find('div', class_='at-subheadline').text
        content = soup.select('.at-subheadline')[0].text
        # content += '\n'\
        #     .join(i.text for i in soup
        #           .find('div', class_='at-content-wrapper')
        #           .find_all('div', class_=content_classes))
        content += '\n'.join(i.text for i in soup.select('.at-content-section'))
        # if soup.find('div', class_='at-category').text == 'Opinion':
        #     publication_dt = datetime.strptime(soup.find(publication_dt_check).text.replace('.', ''),
        #                                        "%b %d, %Y at %I:%M %p %Z")  # %r
        # else:
        #     publication_dt = datetime\
        #         .strptime(soup
        #                   .find('div', class_='at-created')
        #                   .text
        #                   .replace('.', ''), "%b %d, %Y at %I:%M %p %Z")  # %r
        publication_dt = datetime\
            .strptime(soup
                      .select(':is(div.at-created > div > span, div.block-item > span > span.fUOSEs)')[0]
                      .text
                      .replace('.', ''), "%b %d, %Y at %I:%M %p %Z")  # %r)
        parsing_dt = datetime.now()
        # language = soup.find('div', class_='footer-selectstyles__StyledRootContainer-sxto8j-0 lkWIzk').text
        language = soup.select('div.footer-selectstyles__StyledRootContainer-sxto8j-0.lkWIzk > button')[0].text
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
