import requests
from bs4 import BeautifulSoup as bs
from datetime import datetime
from datetime import timedelta
import copy
import time
import re
import sys
from hashlib import md5
cookies = {'over18': '1'}
ARTICLE_SCHEMA = {
        'url': '',
        "board": "",
        "author": "",
        "title": "",
        "date": datetime.now(),
        "content": "",
        "reply": []
        }
REPLY_SCHEMA = {
        'tag': '',
        "author": "",
        "content": "",
        "date": datetime.now(),
        'hash': ''
        }
BASE_URL = 'https://www.ptt.cc'

def clean(s):
    pattern = re.compile('\s+')
    return re.sub(pattern, ' ', s)

class Article:
    def __init__(self, url, days):
        global ARTICLE_SCHEMA
        self._url = url
        self._days = days
        self._raw = ''
        self._data = copy.deepcopy(ARTICLE_SCHEMA)
        self.fetch()
        self.parse()

    def fetch(self):
        global cookies
        fail_cnt = 1
        while True:
            print('try %s %d time'%(self._url, fail_cnt))
            fail_cnt += 1
            try: r = requests.get(self._url, cookies=cookies, timeout=2)
            except:
                time.sleep(fail_cnt)
                continue
            if 400 <= r.status_code < 500 or fail_cnt > 10:
                self._raw = None
                return
            if r.status_code != 200:
                time.sleep(fail_cnt * 10)
                continue
            break
        self._raw = r.text

    def parse(self):
        if not self._raw:
            self._data = None
            return
        global REPLY_SCHEMA
        soup = bs(self._raw, 'html.parser')
        article_metaline = soup.find_all('div', class_='article-metaline')
        try: self._data['board'] = soup.find('div', class_='article-metaline-right').find('span', class_='article-meta-value').text.split()[-1]
        except:
            self._data = None
            return
        self._data['url'] = self._url
        try: self._data['author'] = article_metaline[0].find('span', class_='article-meta-value').text
        except: pass
        try: self._data['title'] = article_metaline[1].find('span', class_='article-meta-value').text
        except: pass
        try: self._data['date'] = datetime.strptime(article_metaline[2].find('span', class_='article-meta-value').text, '%a %b %d %H:%M:%S %Y')
        except: pass
        if datetime.now() - self._data['date'] > self._days:
            raise StopIteration
        content = soup.find('div', id='main-content').text.split('\n')[8:]
        content = content[:content.index('--') if '--' in content else None]
        self._data['content'] = ' '.join(clean(line) for line in content)

        for idx, reply in enumerate(soup.find_all('div', class_='push')):
            r = copy.deepcopy(REPLY_SCHEMA)
            span = reply.find_all('span')
            try: r['tag'] = span[0].text.strip()
            except: pass
            try: r['author'] = span[1].text.strip()
            except: pass
            try: r['content'] = clean(span[2].text)[1:]
            except: pass
            try: r['date'] = datetime.strptime(span[3].text.strip()+' %d'%self._data['date'].year, '%m/%d %H:%M %Y')
            except: pass
            r['hash'] = md5(('%s@%s@%s@%s@%d'%(r['author'], self._data['url'], r['date'], r['content'], idx)).encode()).hexdigest()
            self._data['reply'].append(r)


class ArticleList:
    def __init__(self, board, days):
        global BASE_URL
        self._board = board
        self._days = days
        self._url = '%s/bbs/%s/index.html'%(BASE_URL, board)
        self._next_url = None
        self._prev_url = None
        self._raw = ''
        self._article_urls = []
        self.fetch()
        self.parse()
        self._url = self._prev_url
        self.fetch()
        self.parse()

    def __iter__(self):
        return self

    def __next__(self):
        return self.get_next_post()

    def get_next_post(self):
        if len(self._article_urls) == 0:
            if not self.get_next_page():
                raise StopIteration
        article = Article(self._article_urls.pop(0), self._days)
        if not article._data:
            return self.get_next_post()
        return article

    def get_next_page(self):
        if self._prev_url is None: return False
        self._url = self._prev_url
        self.fetch()
        self.parse()
        return True

    def fetch(self):
        global cookies
        fail_cnt = 1
        while True:
            print('try %s %d time'%(self._url, fail_cnt))
            fail_cnt += 1
            try: r = requests.get(self._url, cookies=cookies, timeout=2)
            except:
                time.sleep(fail_cnt)
                continue
            if r.status_code != 200:
                time.sleep(fail_cnt)
                continue
            break
        self._raw = r.text

    def parse(self):
        global BASE_URL
        soup = bs(self._raw)
        self._article_urls = []
        for div in soup.find_all(class_='r-ent'):
            if div.find(class_='title').find('a'):
                self._article_urls.append(BASE_URL+div.find(class_='title').find('a')['href'])
        self._next_url = soup.find(class_='btn-group pull-right').find_all('a')[2].get('href')
        self._prev_url = soup.find(class_='btn-group pull-right').find_all('a')[1].get('href')
        if self._next_url: self._next_url = BASE_URL + self._next_url
        if self._prev_url: self._prev_url = BASE_URL + self._prev_url


class Board:
    def __init__(self, board):
        self._board = board

    def get_articles(self, days=timedelta(days=10**5)):
        return ArticleList(self._board, days)


if __name__ == '__main__' :
    board = sys.argv[1]
    days = timedelta(days=int(sys.argv[2]))
    for i, a in  enumerate(Board(board).get_articles(days=days)):
        print(i, a._data)
