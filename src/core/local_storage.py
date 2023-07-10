import os
import json
import lzma
import zipfile
import tempfile
import hashlib # md5, sha1, sha224, sha256, sha384, sha512
from datetime import datetime
from src.core.structures.custom_exceptions import SavingErrorException, ReadingErrorException
from src.const import ROOT_DIR, conf_last_parsing_dt_filename
from src.core.structures import ArticleInfo
from src.conf import dir_name_archives, dir_name_html, dir_name_json
import logging


logger = logging.getLogger(__name__)


def save_to_disk(article: ArticleInfo = None, file_name: str = '') -> str:
    try:
        if not article:
            raise SavingErrorException(f'File_name: {file_name}\nReason: Empty article')
        if not file_name:
            file_name = f'{hashlib.sha256(f"{article.href}".encode()).hexdigest()}.xz'
        file_full_name = os.path.join(ROOT_DIR + dir_name_archives, file_name)
        if os.path.isfile(file_full_name):
            logger.warning(f'File {file_name} already exists')
            return file_full_name
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(temp_dir, 'article.html'), 'wb') as f:
                f.write(bytes(article.html, 'utf-8'))
            json_obj = article._asdict()
            json_obj['publication_dt'] = json_obj['publication_dt'].isoformat()
            json_obj['parsing_dt'] = json_obj['parsing_dt'].isoformat()
            with open(os.path.join(temp_dir, 'article.json'), "wb") as f:
                f.write(bytes(json.dumps(json_obj, indent=4), 'utf-8'))
            with zipfile.ZipFile(os.path.join(temp_dir, file_name), "w") as zpf:
                zpf.write(os.path.join(temp_dir, 'article.html'), 'article.html')
                zpf.write(os.path.join(temp_dir, 'article.json'), 'article.json')
            with open(os.path.join(temp_dir, file_name), "rb") as arch, \
                 open(file_full_name, "wb") as lzout:
                lzout.write(lzma.compress(arch.read()))
        return file_full_name
    except Exception as e:
        raise SavingErrorException(f'File_name: {file_name}\nArticle: {article._asdict()}', parent=e)


def decompress_archive(file_name):
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(ROOT_DIR + dir_name_archives, file_name), 'rb') as compressed, \
                    open(os.path.join(temp_dir, file_name), 'wb') as decompressed:
                decompressed.write(lzma.decompress(compressed.read()))
            with zipfile.ZipFile(os.path.join(temp_dir, file_name), "r") as fp:
                with open(os.path.join(ROOT_DIR + dir_name_html, f'{file_name[:-3]}_article.html'), 'wb') as html_file, \
                        open(os.path.join(ROOT_DIR + dir_name_json, f'{file_name[:-3]}_article.json'), 'wb') as json_file:
                    html_file.write(fp.read('article.html'))
                    json_file.write(fp.read('article.json'))
    except Exception as e:
        raise ReadingErrorException(f'Decompress error\nFile_name: {file_name}', parent=e)


def read_from_disk(file_name: str = '') -> ArticleInfo:
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            with open(os.path.join(ROOT_DIR + dir_name_archives, file_name), 'rb') as compressed, \
                    open(os.path.join(temp_dir, file_name), 'wb') as decompressed:
                decompressed.write(lzma.decompress(compressed.read()))
            with zipfile.ZipFile(os.path.join(temp_dir, file_name), "r") as fp:
                jsn = json.loads(fp.read('article.json').decode('utf8'))
                return ArticleInfo(
                    header=jsn['header'],
                    content=jsn['content'],
                    publication_dt=datetime.fromisoformat(jsn['publication_dt']),
                    parsing_dt=datetime.fromisoformat(jsn['parsing_dt']),
                    html=jsn['html'],
                    href=jsn['href'],
                    language=jsn['language']
                )
    except Exception as e:
        raise ReadingErrorException(f'Read from file error\nFile_name: {file_name}', parent=e)


def get_last_pars_dt() -> datetime:
    try:
        with open(conf_last_parsing_dt_filename, 'r') as dtf:
            return datetime.fromisoformat(dtf.read())
    except FileNotFoundError:
        logger.warning(f'Time get error.\nReason: No datetime file')
        return datetime(1970, 1, 1, 0, 0, 0)


def set_last_pars_dt():
    with open(conf_last_parsing_dt_filename, 'w') as f:
        f.write(datetime.now().isoformat())
