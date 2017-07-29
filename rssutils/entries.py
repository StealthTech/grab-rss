import time
import asyncio
import aiohttp

from rssutils.rssutils import *


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
        self.rss_in_text = bool(re.search(rss_word_pattern, html.casefold()))
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
                if link.casefold().startswith('http'):  # other website
                    continue
                link = self.url + link
            normalized.append(link.lower())

        self.rss = list(set(normalized))


class EntryManager():
    def __init__(self):
        self.entry_buffer = []
        self.categories = {
            'no_rss': [],
            'has_rss': [],
            'has_rss_in_text': [],
            'no_url': [],
            'cant_reach': [],
        }
        self.parsed_count = 0

    def add_entry(self, entry):
        if isinstance(entry, Entry):
            self.entry_buffer.append(entry)

    def remove_entry(self, entry):
        if entry in self.entry_buffer:
            self.entry_buffer.remove(entry)

    @property
    def entries(self):
        return self.entry_buffer

    @property
    def count(self):
        return len(self.entry_buffer)

    @property
    def no_rss(self):
        return self.categories['no_rss']

    @property
    def has_rss(self):
        return self.categories['has_rss']

    @property
    def has_rss_in_text(self):
        return self.categories['has_rss_in_text']

    @property
    def no_url(self):
        return self.categories['no_url']

    @property
    def cant_reach(self):
        return self.categories['cant_reach']

    async def parse(self, entry, session):
        if not entry.url:
            self.parsed_count += 1
            # print(f'{parsed_count}. {entry.entry} :: Invalid format (no url specified)')

            if entry not in self.categories['no_url']:
                self.categories['no_url'].append(entry)
            print(f'{self.parsed_count}. {entry.entry} :: Invalid entry format (no url specified)')
            return

        # print(f'Started parsing of {entry.url}')
        await entry.parse(session)
        if entry.request_error:
            self.parsed_count += 1
            if entry not in self.categories:
                self.categories['cant_reach'].append(entry)
            print(
                f'{self.parsed_count}. {entry.entry} :: {entry.url} :: Server not responding (can\'t reach) :: {entry.request_error}')
        elif len(entry.rss):
            self.parsed_count += 1
            if entry not in self.categories:
                self.categories['has_rss'].append(entry)
            print(f'{self.parsed_count}. {entry.url} :: {entry.title} :: Found {len(entry.rss)} RSS channel(s)')
            subcounter = 1
            for rss in entry.rss:
                print(f'   ∟ {subcounter}. {rss}')
                subcounter += 1
        elif entry.rss_in_text:
            if entry not in self.categories:
                self.categories['has_rss_in_text'].append(entry)
        else:
            self.parsed_count += 1
            if entry not in self.categories:
                self.categories['no_rss'].append(entry)
            print(f'{self.parsed_count}. {entry.url} :: {entry.title} :: No RSS channels found')

    async def fetch(self, entries):
        start = time.time()
        with aiohttp.ClientSession() as session:
            tasks = [asyncio.ensure_future(self.parse(entry, session)) for entry in entries]
            await asyncio.wait(tasks)
        print("Process took: {:.2f} seconds".format(time.time() - start))

    def fetch_sliced(self, loop, entries, step):
        start = time.time()
        size = len(entries)
        for chunk in range(size // step + int(bool(size % step))):
            sliced = entries[chunk * step:chunk * step + step]
            if sliced:
                loop.run_until_complete(self.fetch(sliced))
        self.cleanup_categories()
        print("Total time elapsed: {:.2f} seconds".format(time.time() - start))


    def __fetch_sliced_impl(self, loop, entries, step):
        pass

    def cleanup_categories(self):
        for key, value in self.categories.items():
            if isinstance(value, list):
                self.categories[key] = list(set(value))