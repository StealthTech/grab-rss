import requests
import re
from bs4 import BeautifulSoup

__checklist = [
    'rss',
    'feed',
]


def search_rss_meta(html):
    soup = BeautifulSoup(html, 'html.parser')
    meta = soup.find_all('link', {'type': 'application/rss+xml'})

    rss_links = []
    for rss_link in meta:
        if rss_link.has_attr('href'):
            rss_links.append(str(rss_link['href']))

    return rss_links


def search_rss_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    all_links = soup.find_all('a')

    rss_links = []
    for link in all_links:
        if link.has_attr('href'):
            has_rss = False
            href = link.get('href')
            for checker in __checklist:
                if checker in href:
                    has_rss = True
            if has_rss:
                rss_links.append(href)

    return rss_links


def search_rss_icons(html):
    pass


def fetch_url(name):
    url_pattern = re.compile("(https?:\/\/)?([a-z0-9_\-]{2,100}\.){1,3}[a-z]{2,5}(\/)?")
    match = url_pattern.search(name.lower())
    if not match:
        return None
    return match.group(0)


def get_content(url):
    error = None
    r = ''
    try:
        r = requests.get(url)
        if r.status_code != 200:
            error = r.status_code
    except:
        error = 'ERROR: Exception occurred'

    if not error:
        return r.text, None
    else:
        return None, error


class Entry:
    rss_finders = [
        search_rss_meta,
        search_rss_links,
    ]

    def __init__(self, entry):
        self.entry = entry
        self.url = fetch_url(entry)

        if self.url and not self.url.startswith('http'):
            self.url = 'http://' + self.url

        self.html = ''
        self.title = ''

        self.rss = []
        self.request_error = False

    def parse(self):
        html, error = get_content(self.url)
        if error:
            self.request_error = True
            return None

        self.html = html
        soup = BeautifulSoup(self.html, 'html.parser')
        self.title = soup.find('title').text

        for handler in Entry.rss_finders:
            result = handler(html)
            if result:
                self.rss = result
                break
