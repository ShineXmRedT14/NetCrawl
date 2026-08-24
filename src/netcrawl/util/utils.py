import datetime
import logging

from fake_useragent import UserAgent

class NetCrawlAgent:
    def __init__(self):
        self.obj = UserAgent()
        self._accept = "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
        self._language = "en-US,en;q=0.9,es;q=0.8,de;q=0.7,fr;q=0.6"
        self.viewport = {'width': 1920, 'height': 1080}
    @property
    def accept(self) -> str:
        return self._accept
    
    @property
    def language(self) -> str:
        return self._language
    
    @property
    def user(self) -> str:
        return self.obj.random
    
    @property
    def all(self) -> dict:
        return {
            'Accept': self._accept,
            'Accept-Language': self._language,
            'User-Agent': self.obj.random
        }
    
    @property
    def view(self) -> dict:
        return self.viewport

def pather(cwd: str) -> str:
    try:
        if cwd.endswith('crawler'):
            paths = "./src"
        elif cwd.endswith('src'):
            paths = "."
        elif cwd.endswith('netcrawl'):
            paths = ".."
        elif not cwd.endswith('crawler'):
            paths = "./crawler/src"
        else: raise "Error/Path/NotFound"

        return paths
    except Exception as e:logging.error(ferr(e), exc_info=True)

def ferr(e: str) -> str:
    try:
        return f"{datetime.datetime.now().strftime('%H:%M:%S')} - {e}"
    except Exception as e:logging.error(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {e}", exc_info=True)
