import sqlite3
from utils import openYAML
from logger import log, logLevel, debug, info, warning, error, critical


class readAimlabsDB:
    def __init__(self):
        config = openYAML('userConfig')
        self.dbPath = os.path.abspath(os.path.join(os.getenv(
            "APPDATA"), os.pardir, config['dbPath']))
