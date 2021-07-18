from scraper.srf_scraper import getSRFArticles
from logic.file_handler import get_articles

import time

def get_new_articles_from_web():
    start = time.time()
    srf_articles = getSRFArticles(get_articles())
    print(time.time() - start)
    return srf_articles