import os


ROOT_DIR = os.path.dirname(os.path.abspath(__file__))[:-4]
conf_log_filename = os.path.join(ROOT_DIR, 'pars_log.txt')
conf_last_parsing_dt_filename = os.path.join(ROOT_DIR, 'last_parsing.txt')
