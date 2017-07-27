import requests
import aiohttp
import re
from bs4 import BeautifulSoup

_rss_word_pattern = '([^a-z]|^)rss([^a-z]|$)'
__request_get_timeout = 5 # Request timeout in seconds


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
            href = link.get('href').casefold()
            text = link.get_text().casefold()
            href_match = re.search(_rss_word_pattern, href)
            text_match = re.search(_rss_word_pattern, text)
            if href_match or text_match:
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


async def get_content(url, session):
    error = None
    r = ''
    try:
        # r = requests.get(url, timeout=__request_get_timeout)

        r = await session.get(url, timeout=15)

        # aiohttp.request('GET', url)
        if r.status != 200:
            error = r.status
        # print('>' * 10, url, r.status, error)

    except Exception as e:
        print(f'ex :: get_content :: {url} :: {e}')
        error = 'ERROR: Exception occurred'

    if not error:
        try:
            result = await r.text()
        except UnicodeError:
            return 'Invalid unicode', None
        else:
            return result, None
        # return await r.text(), None
    else:
        return None, error


async def traverse_common_links(url, session):
    links = [
        'rss',
        'rss.xml',
        'feed'
    ]

    if not url.endswith('/'):
        url += '/'

    pages_found = []
    for link in links:
        html, error = await get_content(url + link, session)
        if not error:
            pages_found.append(url + link)
    return pages_found


class Entry:
    rss_finders = [
        search_rss_meta,
        search_rss_links,
    ]

    next_id = 1

    def __init__(self, entry):
        self.id = Entry.next_id
        Entry.next_id += 1

        self.entry = entry
        self.url = fetch_url(entry)

        if self.url and not self.url.startswith('http'):
            self.url = 'http://' + self.url

        self.html = ''
        self.title = ''

        self.rss = []
        self.request_error = False
        self.rss_in_text = False

    async def parse(self, session):
        html, error = await get_content(self.url, session)
        # print(error)
        if error:
            self.request_error = True
            return None
        self.rss_in_text = bool(re.search(_rss_word_pattern, html.casefold()))
        self.html = html
        soup = BeautifulSoup(self.html, 'html.parser')

        title = soup.find('title')
        if title is None or title.text is None:
            self.title = '[ Page title is missing ]'
        else:
            self.title = str(title.text).strip()

        for handler in Entry.rss_finders:
            result = handler(html)
            if result:
                self.rss = result
                break

        self.rss.extend(await traverse_common_links(self.url, session))

        self._normalize_rss()

    def _normalize_rss(self):
        site_name = '.'.join(self.url.split('://')[-1].split('.')[-2:])
        if not site_name.endswith('/'):
            site_name += '/'
            
        normalized = []
        for link in self.rss:
            if not site_name.casefold() in link.casefold():
                if link.casefold().startswith('http'): #other website
                    continue
                link = self.url + link
            normalized.append(link.lower())
            
        self.rss = list(set(normalized))
