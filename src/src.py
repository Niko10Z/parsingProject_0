import os
import requests
import json
import lzma
import zipfile
import tempfile
import hashlib # md5, sha1, sha224, sha256, sha384, sha512
from resources.structures import RequestErrorException, \
                                 SavingErrorException, \
                                 ArticleInfo, \
                                 ROOT_DIR, \
                                 conf_last_parsing_dt_filename,\
                                 logger
from datetime import datetime


def get_article_info(href: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36'
    }
    cookies = {}
    try:
        r = requests.get(href, headers=headers, cookies=cookies)
    except Exception as e:
        raise RequestErrorException('Invalid request', parent=e)
    # r = requests.get(href, headers=headers, cookies=cookies)
    try:
        r.raise_for_status()
    except Exception as e:
        raise RequestErrorException(f'Response error\nURL:{href}\nStatus:{r.status_code}\nReason:{r.reason}', parent=e)
    if not r.text.strip():
        raise RequestErrorException(f'Empty response body error')
    return r.text


def save_to_disk(article: ArticleInfo = None, file_name: str = '') -> None:
    try:
        if not article:
            raise SavingErrorException(f'File_name: {file_name}\nReason: Empty article')
        if not file_name:
            file_name = f'{hashlib.sha256(f"{article.href}".encode()).hexdigest()}.xz'
        if os.path.isfile(file_name):
            return
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, 'article.html'), 'wb') as f:
                f.write(lzma.compress(bytes(article.html, 'utf-8')))
            json_obj = article._asdict()
            json_obj['publication_dt'] = json_obj['publication_dt'].isoformat()
            json_obj['parsing_dt'] = json_obj['parsing_dt'].isoformat()
            with open(os.path.join(temp_dir, 'article.json'), "wb") as f:
                f.write(lzma.compress(bytes(json.dumps(json_obj, indent=4), 'utf-8')))
            with zipfile.ZipFile(os.path.join(ROOT_DIR, file_name), "w") as zpf:
                zpf.write(os.path.join(temp_dir, 'article.html'), 'article.html')
                zpf.write(os.path.join(temp_dir, 'article.json'), 'article.json')
    except Exception as e:
        raise SavingErrorException(f'File_name: {file_name}\nArticle: {article._asdict()}')


def get_last_pars_dt() -> datetime:
    try:
        with open(os.path.join(ROOT_DIR, conf_last_parsing_dt_filename), 'r') as dtf:
            return datetime.fromisoformat(dtf.read())
    except FileNotFoundError:
        logger.warning(f'Time get error.\nReason: No datetime file')
        return datetime(1970, 1, 1, 0, 0, 0)


def set_last_pars_dt():
    with open(os.path.join(ROOT_DIR, conf_last_parsing_dt_filename), 'w') as f:
        f.write(datetime.now().isoformat())
