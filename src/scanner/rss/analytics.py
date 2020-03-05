import re
from bs4 import BeautifulSoup

rss_word_pattern = '([^a-z]|^)rss([^a-z]|$)'
__request_get_timeout = 20  # Request timeout in seconds


def search_rss_meta(html):
    soup = BeautifulSoup(html, 'html.parser')
    meta = soup.find_all('link', {'type': 'application/rss+xml'})

    rss_links = []
    for rss_link in meta:
        if rss_link.has_attr('href'):
            rss_links.append(normalize_link(str(rss_link['href'])))

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
                rss_links.append(normalize_link(href))
    return rss_links


def search_rss_icons(html):
    pass


def fetch_url(name):
    en_url_pattern = re.compile('(https?://)?([a-z0-9_\-]{2,100}\.){1,3}[a-z]{2,5}(/)?')
    en_match = en_url_pattern.search(name.lower())
    if en_match:
        return en_match.group(0)

    ru_url_pattern = re.compile('(https?://)?([а-я0-9_\-]{2,100}\.)рф(/)?')
    ru_match = ru_url_pattern.search(name.lower())
    if ru_match:
        return ru_match.group(0)


async def get_content(url, session):
    error = None
    r = ''
    try:
        r = await session.get(url, timeout=__request_get_timeout)
        if r.status != 200:
            error = r.status

    except Exception as e:
        # print(f'ex :: get_content :: {url} :: {e}')
        error = 'ERROR: Exception occurred'

    if not error:
        try:
            result = await r.text()
        except UnicodeError:
            return 'Invalid unicode', None, url
        else:
            return result, None, str(r.url)
    else:
        return None, error, url


async def traverse_common_links(url, session):
    if not url.endswith('/'):
        url += '/'

    link_patterns = [
        'rss',
        'rss.xml',
        'feed'
    ]

    rss = {}
    for pattern in link_patterns:
        html, error, new_url = await get_content(url + pattern, session)
        if not error:
            rss[normalize_link(new_url)] = html.strip()

    rss = remove_similar_by_content(rss)

    result = [key for key in rss.keys()]

    return result


def normalize_link(string):
    # TODO: Normalize href format, optimization
    result = string

    if result.startswith('//'):
        result = result[2:]
    if not result.startswith('http'):
        result = 'http://' + result
    if result.endswith('/'):
        result = result[:-1]

    return result


def remove_similar_by_content(entry_dictionary):
    result = {}
    for key, value in entry_dictionary.items():
        if value not in result.values():
            result[key] = value
        else:
            print(f'removed: {key}')
    return result

