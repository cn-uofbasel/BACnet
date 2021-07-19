#!/usr/bin/python3
from logic.file_handler import get_articles
from logic.file_handler import save_article
from logic.file_handler import get_article_titles
from logic.article import Category
from logic.article import Article
from scraper.srf_scraper import getSRFArticles
from scraper.scraper_manager import get_new_articles_from_web
import threading
import datetime

class LogicInterface:
    def __init__(self):
        self.is_updating = False

    def download_new_articles(self):
        # TODO only download new articles
        if not self.is_updating:
            self.is_updating = True
            self.start_scraping()

    def start_scraping(self):
        articles = get_new_articles_from_web()
        for article in articles:
            if article is not None:
                save_article(article)
        #print("finished downloading")
        self.is_updating = False

    def get_articles(self):
        return get_articles()

    def get_article_titles(self):
        list = get_article_titles()
        titles = []
        unread_titles = []

        for article in list:
            titles.append(article.title_1)
            if not article.opened:
                unread_titles.append(article.title_1)

        # sort alphabetically
        titles.sort()
        unread_titles.sort()

        for title in titles:
            if title in unread_titles:
                unread_titles.remove(title)
                index = titles.index(title)
                titles[index] = "\u2022 " + title

        return titles

    def get_article_titles_today(self):
        dt = datetime.datetime.today()
        today = datetime.date(dt.year, dt.month, dt.day)
        filtered_lst = []
        unread_titles = []

        articles = get_article_titles()
        for article in articles:
            article_dt = datetime.datetime.fromisoformat(article.date_and_time)
            article_month = int(article_dt.strftime("%m"))
            article_day = int(article_dt.strftime("%d"))
            article_year = int(article_dt.strftime("%Y"))
            article_date = datetime.date(article_year, article_month, article_day)

            if today == article_date:
                filtered_lst.append(article.title_1)
                if not article.opened:
                    unread_titles.append(article.title_1)

            # sort alphabetically
            filtered_lst.sort()
            unread_titles.sort()

            for title in filtered_lst:
                if title in unread_titles:
                    unread_titles.remove(title)
                    index = filtered_lst.index(title)
                    filtered_lst[index] = "\u2022 " + title

        return filtered_lst

    def get_article_titles_week(self):
        today = datetime.date.today()
        filtered_lst = []
        unread_titles = []

        articles = get_article_titles()
        for article in articles:
            article_dt = datetime.datetime.fromisoformat(article.date_and_time)
            article_month = int(article_dt.strftime("%m"))
            article_day = int(article_dt.strftime("%d"))
            article_year = int(article_dt.strftime("%Y"))
            article_day = datetime.date(article_year, article_month, article_day)

            delta = today - article_day
            if delta.days <= 7:
                filtered_lst.append(article.title_1)
                if not article.opened:
                    unread_titles.append(article.title_1)

        # sort alphabetically
        filtered_lst.sort()
        unread_titles.sort()

        for title in filtered_lst:
            if title in unread_titles:
                unread_titles.remove(title)
                index = filtered_lst.index(title)
                filtered_lst[index] = "\u2022 " + title

        return filtered_lst

    def get_article_html_by_title1(self, title):
        title = self.cut_title(title)
        for article in self.get_articles():
            if article.title_1 == title:
                return article.get_html()

    def mark_as_deleted(self, article):
        article.deleted = True
        save_article(article)
    
    def mark_as_opened(self, article):
        article.opened = True
        save_article(article)

    def get_bookmarked_article_titles(self):
        lst = []
        for article in self.get_articles():
            if article.bookmarked:
                lst.append(article.title_1)
        lst.sort()
        return lst

    def bookmark_article(self, title):
        for article in self.get_articles():
            if article.title_1 == title:
                article.bookmarked = True
                save_article(article)

    def remove_bookmark_article(self, title):
        for article in self.get_articles():
            if article.title_1 == title:
                article.bookmarked = False
                save_article(article)

    def is_article_bookmarked(self, title):
        for article in self.get_articles():
            if article.title_1 == title:
                return article.bookmarked

    def mark_as_opened(self, title):
        title = self.cut_title(title)
        for article in self.get_articles():
            if article.title_1 == title:
                article.opened = True
                save_article(article)

    def cut_title(self, title):
        if title.startswith("\u2022"):
            return title[2:]
        else:
            return title

    def filter_by_category(self, titles, category):
        articles = self.prepare_titles_for_filter(titles)
        if articles == None:
            return []

        filtered = []
        for article in articles:
            if article.category == category:
                filtered.append(self.get_printing_title(article))
        return filtered

    def get_printing_title(self, article):
        title = article.title_1
        if article.opened:
            return title
        else:
            return "\u2022 " + title

    def prepare_titles_for_filter(self, titles):
        # get correct titles
        cut_titles = []
        for title in titles:
            cut_titles.append(self.cut_title(title))

        # get artciles from titles
        articles = []
        for title in cut_titles:
            articles.append(self.get_article_from_title(title))

        return articles

    def get_article_from_title(self, title):
        for article in get_articles():
            if article.title_1 == title:
                return article
        return "Not found"
