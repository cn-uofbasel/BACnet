import threading
from scraper.srf_scraper import getSRFArticles
from logic.article import Article
from logic.interface import LogicInterface

class Interface:

    def __init__(self, window):
        self.window = window
        self.logic_interface = LogicInterface()
        self.article_list = self.logic_interface.get_articles()
        self.article_titles = self.get_downloaded_articles()
        self.is_downloading = False

    # returns a list of all downloaded article files
    def get_downloaded_articles(self):
        #if self.article_titles == None:
        #    return []
        #return self.article_titles
        titles = []
        for article in self.logic_interface.get_articles():
            titles.append(article.title_1)
        return titles

    def threaded_download(self):
        if not self.is_downloading:
            self.window.switch_to_loading()
            thread = threading.Thread(target=self.download)
            thread.start()
        else:
            print("already downloading")

    def download(self):
        self.is_downloading = True
        self.logic_interface.download_new_articles()
        articles = self.logic_interface.get_articles()
        self.article_list = articles
        titles = []

        for article in articles:
            if article is not None:
                titles.append(article.title_1)

        self.article_titles = titles
        self.is_downloading = False
        print("finished downloading")

    def get_article_html_by_title(self, title):
        if self.article_titles == None:
            return ""

        for article in self.article_list:
            if article != None and article.title_1 == title:
                return article.get_html()
