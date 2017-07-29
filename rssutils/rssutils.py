import requests
import aiohttp
import re
from bs4 import BeautifulSoup

rss_word_pattern = '([^a-z]|^)rss([^a-z]|$)'
__request_get_timeout = 5  # Request timeout in seconds


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
            href_match = re.search(rss_word_pattern, href)
            text_match = re.search(rss_word_pattern, text)
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

        r = await session.get(url, timeout=20)

        # aiohttp.request('GET', url)
        if r.status != 200:
            error = r.status
        # print('>' * 10, url, r.status, error)

    except Exception as e:
        # print(f'ex :: get_content :: {url} :: {e}')
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


