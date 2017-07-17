import requests
import re
from bs4 import BeautifulSoup

RSS_STATUS_CANT_REACH = 0
RSS_STATUS_FOUND = 1
RSS_STATUS_TEXT_FOUND = 2
RSS_STATUS_NOT_FOUND = 3

__checklist = [
    'rss',
    'feed',
]


def pull(url):
    r = requests.get(url)

    if r.status_code == 200:
        found = __search(r.text)
        if found:
            # print(found)
            return RSS_STATUS_FOUND
        else:
            text_found = False
            for checker in __checklist:
                if checker in r.text:
                    text_found = True
            if text_found:
                return RSS_STATUS_TEXT_FOUND
            else:
                return RSS_STATUS_NOT_FOUND
    else:
        return RSS_STATUS_CANT_REACH


def __search(html):
    soup = BeautifulSoup(html, 'html.parser')

    result = soup.find_all('link', {'type': 'application/rss+xml'})
    # result.extend(soup.find_all('a'))
    for rss in result:
        print(rss.get('href'))

    if len(result) > 0:
        return result
    else:
        return None


def fetch_url(name):
    url_pattern = re.compile("(https?:\/\/)?([a-z0-9_\-]{2,100}\.){1,3}[a-z]{2,5}(\/)?")
    match = url_pattern.search(name.lower())
    if not match:
        return None
    return match.group(0)


class Entry:
    def __init__(self, text):
        self.text = text
        self.url = fetch_url(text)
        self.rss_filenames = []
        self.rss_in_plain_text = False
        self.request_error = False

