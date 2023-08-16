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
    try:
        response = requests.post(href, headers=headers, cookies=cookies, json=json)
        return response.json()
    except Exception as e:
        raise RequestErrorException('Error in getting JSON\n'
                                    f'Headers = {headers}\n'
                                    f'Cookies = {cookies}\n'
                                    f'JSON = {json}\n', parent=e)
