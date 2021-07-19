from bs4 import BeautifulSoup
import requests
import re
from logic.article import Article
from logic.article import Category
import time
from datetime import datetime

# old_articles_infos are the titles, published- and modified dates from the articles that already have been saved before
def getURLsfromRSS(old_article_infos):
    src = requests.get("https://www.srf.ch/news/bnf/rss/1646")

    #html content stored in scr
    html = src.content

    items = BeautifulSoup(html, 'html.parser').find_all('item')

    rss_titles = list()
    urls = list()
    numberNew = 0
    numberNew2 = 0
    numberArticles = 0
    for item in items:
        numberArticles = numberArticles + 1
        title = item.contents[0]
        if title not in rss_titles: # not a duplicate title in rss feed
            rss_titles.append(title)
            numberNew = numberNew + 1
            if title.text not in old_article_infos[0]: # a new title, not an article that has been saved before
                #for art in old_article_infos[0]:
                    #print("title: " + str(title) + "old: " + art)
                #print(title)
                url = item.contents[2]
                urls.append(url)
                numberNew2 = numberNew2 + 1
            else:
                pass    # TODO? would be implemented when updating articles is considered (currently not working with published- and modified date, would have to scrap whole html for this)
        #else:
        #    print(title)

    print("#Articles found: " + str(numberArticles) + ", no duplicate: "  + str(numberNew) + ", not already saved: " + str(numberNew2))

    return urls

# get the one article found at the given url (only working for srf articles)
def getArticleFromURL(url):
    #try:
    src = requests.get(url)
    html = src.content

    #parse src (often called soup)
    htmlParsed = BeautifulSoup(html, 'html.parser')

    main_category_pattern = 'ch/(.+?)/'
    second_category_pattern = 'ch/(.+?)/(.+?)/'
    mainCategory = re.search(main_category_pattern, url).group(1) # get 2 categories, for example 'news' and 'schweiz' or 'sport' and 'fussball'
    if re.search(second_category_pattern, url) is None: #no second title, e.g. "Kultur" has none
        secondaryCategory = ""
    else:
        secondaryCategory = re.search(second_category_pattern, url).group(2)

    try:
        overtitle = htmlParsed.find('span', class_='article-title__overline').text   # overline title of article
        title = htmlParsed.find('span', class_='article-title__text').text   # title of article
    except:
        overtitle = "title not found"
        title = "title not found"
        
    article_lead = htmlParsed.find('p', class_='article-lead')  # look for the text before the actual article (the article lead)
    if article_lead is not None:
        article_lead = article_lead.text
    else:
        article_lead = ""

    content = htmlParsed.find('section', class_='article-content')  # all the content of the article-content class
    if content is None:
        print(url) # can be removed after bugfixing
        content = htmlParsed.find('div', class_='article-content')
        if content is None:
            print("if you have no new articles, the program needs an update, bacause SRF changed something")
            return None
        
    if content.find(class_ = "ticker-item") is None:    # only take article if it has no live ticker, otherwise ignore it

        # get the date the article got published and last modified (if there, otherwise let it be empty strings)
        publishedDate = None
        modifiedDate = None
        try: # maybe the date format gets changed, then it cannot find group(1) and group(2)
            if htmlParsed.find(class_='article-author__date') is not None:
                dates = str(htmlParsed.find(class_='article-author__date'))
                datePattern = '(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d).*(\d\d\d\d-\d\d-\d\dT\d\d:\d\d:\d\d)'
                publishedDate = re.search(datePattern, dates).group(1)
                modifiedDate = re.search(datePattern, dates).group(2)
        except:
            pass

        if publishedDate is None:
            publishedDate = datetime.fromtimestamp(time.time()).isoformat() #"0000-01-01T01:01:00+02.00"
        if modifiedDate is None:
            modifiedDate = datetime.fromtimestamp(time.time()).isoformat() #"0000-01-01T01:01:00+02.00"
            
        # get rid of polls
        try:
            if content.find(class_="poll__title") is not None:
                content.find(class_="poll__title").decompose()
                pollAnswer = content.find(class_="poll-option poll-option--poll")
                while pollAnswer is not None:
                    content.find(class_="poll-option poll-option--poll").decompose()
                    pollAnswer = content.find(class_="poll-option poll-option--poll")
                if content.find(class_="js-poll_taken_text h-element--hide") is not None:
                    content.find(class_="js-poll_taken_text h-element--hide").decompose()
        except:
            pass
        
        # details of a person in the article, is removed
        if content.find('p', class_='person-details__name') is not None:
            content.find('p', class_='person-details__name').decompose()
        if content.find('p', class_='person-details__function') is not None:
            content.find('p', class_='person-details__function').decompose()
        
        if content.find_all('h2', class_='related-items-list__heading') is not None:
            for element in content.find_all('h2', class_='related-items-list__heading'):
                element.decompose()
        if content.find_all(class_="related-items-list__item") is not None:
            for rel in content.find_all(class_="related-items-list__item"):
                rel.parent.decompose()

        for a in content.find_all('a'):
            a.replaceWithChildren().text

        for span in content.find_all('span'):
                span.decompose()
        
        if content.find_all('div', class_='expandable-box') is not None:
            for element in content.find_all('div', class_='expandable-box'):
                element.decompose()

        if content.find_all('div', class_='linkbox') is not None:
            for element in content.find_all('div', class_='linkbox'):
                element.decompose()

        content = content.find_all(['p', 'h2', 'h3', 'li']) # take all <p>, <h2>, <h3> and <li> tags in the article-content class (all the relevant text in the article)

        newArticle = Article("SRF") #make a new article and fill it with the important informations
        newArticle.set_title_0(overtitle)
        newArticle.set_title_1(title)
        newArticle.set_date_and_time(publishedDate)
        newArticle.set_lead(article_lead)

        if mainCategory == "news":
            if secondaryCategory == "schweiz":
                newArticle.set_category(Category.SWITZERLAND)
            elif secondaryCategory == "international":
                newArticle.set_category(Category.INTERNATIONAL)
            elif secondaryCategory == "panorama":
                newArticle.set_category(Category.PANORAMA)
            elif secondaryCategory == "wirtschaft":
                newArticle.set_category(Category.ECONOMICS)
            else:
                newArticle.set_category(Category.OTHER)
        elif mainCategory == "sport":
            newArticle.set_category(Category.SPORTS)
        elif mainCategory == "meteo":
            newArticle.set_category(Category.METEO)
        elif mainCategory == "kultur":
            newArticle.set_category(Category.CULTURE)
        # else do nothing

        #newArticle.set_date_and_time_updated(modifiedDate) not yet available
        
        for text in content:
            strText = str(text)
            if re.search("<li>", strText):
                newArticle.add_list_elem(text.text)
            elif re.search("<p>", strText):
                newArticle.add_paragraph(text.text)
            elif re.search("<h2>", strText):
                newArticle.add_tagline(text.text)
            elif re.search("<h3>", strText):
                newArticle.add_tagline(text.text)

        return newArticle

    else:
        #print(title)
        return None
    #except Exception:
        #print("article could not be downloaded: " + url)
        #return None
       
# old_articles are the articles saved before (with the last time articles got downloaded)
def getSRFArticles(old_articles):
    articleList = list()
    infos = get_article_infos(old_articles)
    #for art in old_articles:
        #print(art.title_1)
    urls = getURLsfromRSS(infos)
    
    for url in urls:
        if url is not None:
            article = getArticleFromURL(url)
            if article is not None:
                articleList.append(article)

    return articleList

def get_article_infos(articles): # articles is a list of articles
    infos = [[], [], []] # save title, published- and modified date of articles
    for article in articles:
        title = article.title_1
        published_date = article.date_and_time
        modified_date = article.date_and_time_modified
        if title is not None and published_date is not None and modified_date is not None:
            infos[0].append(title)
            infos[1].append(published_date)
            infos[2].append(modified_date)

    return infos    
    
def main():
    
    start = time.time()
    articles = getSRFArticles([])

if __name__ == "__main__":
    main()