#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sqlite3
import urllib2
from urlparse import urljoin

from BeautifulSoup import *

# Create a list of words to ignore
from tqdm import tqdm

ignorewords = {'the', 'of', 'to', 'and', 'a', 'in', 'is', 'it', 'HD', '1080', '720', 'pornhub.com', 'pornhub', 'com',
               'n', 'de', 'o', 'y', 'hd', 'by', '-', '_', '&', '+', '-', '.', ';'}


class crawler:
    # Initialize the crawler with the name of database
    def __init__(self, dbname):
        self.con = sqlite3.connect(dbname)
        self.pages_crawled = 0

    def __del__(self):
        self.con.close()

    def dbcommit(self):
        self.con.commit()

    # Auxilliary function for getting an entry id and adding
    # it if it's not present
    def getentryid(self, table, field, value, createnew=True):
        cur = self.con.execute(
            "select rowid from %s where %s='%s'" % (table, field, value))
        res = cur.fetchone()
        if res == None:
            cur = self.con.execute(
                "insert into %s (%s) values ('%s')" % (table, field, value))
            return cur.lastrowid
        else:
            return res[0]

    def addtoindex(self, url, soup):
        if self.isindexed(url):
            return
        # Get the individual words
        text = self.gettextonly(soup)
        words = self.separatewords(text)
        # Get the URL id
        urlid = self.getentryid('urllist', 'url', url)

        # Link each word to this url
        print "Word inserted in wordlocation: %s" % str(len(words))
        for i in range(len(words)):
            word = words[i]
            if word in ignorewords:
                continue
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.execute("insert into wordlocation(urlid,wordid,location) values (%d,%d,%d)" % (urlid, wordid, i))

    # Extract the text from an HTML page (no tags)
    def gettextonly(self, soup):
        try:
            return ' '.join(soup.find('title').contents)
        except:
            print "Error getting the title"

    # Seperate the words by any non-whitespace character
    def separatewords(self, text):
        return [word.lower() for word in re.split('\W+', text, flags=re.UNICODE) if len(word) > 1]

        # wordlist = [s.lower() for s in text.split() if s != '']

        #
        # returnwords = list()
        # for word in wordlist:
        #     for ignorechar in skipwords:
        #         word = word.replace(ignorechar.decode('utf-8'), '')
        #     returnwords.append(word)
        # return returnwords

    # Return true if this url is already indexed
    def isindexed(self, url):
        wordcount = self.con.execute(
            "select count(wordlocation.urlid) from wordlocation JOIN urllist ON wordlocation.urlid = urllist._rowid_ WHERE urllist.url = '%s'" % url).fetchone()
        return False if wordcount[0] == 0 else True

    # Add a link between two pages
    def addlinkref(self, urlFrom, urlTo, linkText):
        words = self.separatewords(linkText)
        fromid = self.getentryid('urllist', 'url', urlFrom)
        toid = self.getentryid('urllist', 'url', urlTo)
        if fromid == toid: return
        cur = self.con.execute("insert into link(fromid,toid) values (%d,%d)" % (fromid, toid))
        linkid = cur.lastrowid
        # print "Appending " + str(len(words)) + "words"
        for word in words:
            if word in ignorewords: continue
            wordid = self.getentryid('wordlist', 'word', word)
            self.con.execute("insert into linkwords(linkid,wordid) values (%d,%d)" % (linkid, wordid))

    # Starting with a list of pages, do a breadth
    # first search to the given depth, indexing pages
    # as we go
    def crawl(self, pages, depth=4):
        crawled_pages = 0
        for j in tqdm(range(depth)):
            newpages = list()
            for page in pages:
                try:
                    c = urllib2.urlopen(page, timeout=5000)
                except:
                    continue
                try:
                    soup = BeautifulSoup(c.read())
                    self.addtoindex(page, soup)
                    crawled_pages +=1
                    print("Crawling: %s . Num of crawled: %d" % (page, crawled_pages))

                    links = remove_duplicate_url(filter(
                        lambda web: 'view_video.php' in web['href'] and 'title' in web.attrMap and web[
                                                                                                       'title'] != '',
                        soup.findAll('a', href=True)))

                    for link in links:
                        url = urljoin(page, link['href'].split('&')[0])
                        if url.find("'") != -1: continue
                        url = url.split('#')[0]  # remove location portion
                        if url[0:4] == 'http' and not self.isindexed(url):
                            newpages.append(url)

                        linkText = link['title']
                        self.addlinkref(page, url, linkText)

                    self.dbcommit()
                except:
                    continue

            pages = newpages

    # Create the database tables
    def createindextables(self):
        self.con.execute('create table urllist(url)')
        self.con.execute('create table wordlist(word)')
        self.con.execute('create table wordlocation(urlid,wordid,location)')
        self.con.execute('create table link(fromid integer,toid integer)')
        self.con.execute('create table linkwords(wordid,linkid)')
        self.con.execute('create index wordidx on wordlist(word)')
        self.con.execute('create index urlidx on urllist(url)')
        self.con.execute('create index wordurlidx on wordlocation(wordid)')
        self.con.execute('create index urltoidx on link(toid)')
        self.con.execute('create index urlfromidx on link(fromid)')
        self.dbcommit()


class searcher:
    def __init__(self, dbname):
        self.con = sqlite3.connect(dbname)

    def __del__(self):
        self.con.close()

    def getmatchrows(self, q):
        # Strings to build the query
        fieldlist = 'w0.urlid'
        tablelist = ''
        clauselist = ''
        wordids = []

        # Split the words by spaces
        words = q.split(' ')
        tablenumber = 0

        for word in words:
            # Get the word ID
            wordrow = self.con.execute(
                "select rowid from wordlist where word='%s'" % word).fetchone()
            if wordrow != None:
                wordid = wordrow[0]
                wordids.append(wordid)
                if tablenumber > 0:
                    tablelist += ','
                    clauselist += ' and '
                    clauselist += 'w%d.urlid=w%d.urlid and ' % (tablenumber - 1, tablenumber)
                fieldlist += ',w%d.location' % tablenumber
                tablelist += 'wordlocation w%d' % tablenumber
                clauselist += 'w%d.wordid=%d' % (tablenumber, wordid)
                tablenumber += 1

        # Create the query from the separate parts
        fullquery = 'select %s from %s where %s' % (fieldlist, tablelist, clauselist)
        print fullquery
        cur = self.con.execute(fullquery)
        rows = [row for row in cur]
        return rows, wordids


def remove_duplicate_url(urllist):
    toreturn = list()
    unique_urls = list()
    for url in urllist:
        if url['href'] not in unique_urls:
            unique_urls.append(url['href'])
            toreturn.append(url)

    return toreturn


page_to_crawl = 'https://es.pornhub.com'

# Get page list
c = urllib2.urlopen(page_to_crawl)
soup = BeautifulSoup(c.read())
pagelist = filter(lambda web: 'view_video.php' in web['href'] and 'title' in web.attrMap and web['title'] != '',
                  soup.findAll('a', href=True))
pageset = set([urljoin(page_to_crawl, page['href'].split('&')[0]) for page in pagelist])
craw = crawler('data.db')
craw.createindextables()
craw.crawl(pages=pageset)
