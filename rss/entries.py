import time
import asyncio
import aiohttp

from rss.analytics import *
from rss import utils


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
        self.event_loop = asyncio.get_event_loop()

    def load_file(self, filename):
        file = utils.load(filename)
        if file:
            for line in file:
                self.add_entry(Entry(line))
        print(f'Entries loaded from \'{filename}\': {len(file)}')

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
    def count(self, category=None):
        if category in self.categories:
            if isinstance(self.categories[category], list):
                return len(self.categories[category])
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

            if entry not in self.categories['no_url']:
                self.categories['no_url'].append(entry)
            print(f'{self.parsed_count}. {entry.entry} :: Invalid entry format (no url specified)')
            return

        await entry.parse(session)
        if entry.request_error:
            self.parsed_count += 1
            if entry not in self.categories:
                self.categories['cant_reach'].append(entry)
            print(
                f'{self.parsed_count}. {entry.entry} :: {entry.url} :: Server not responding (can\'t reach)')
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

    def fetch_sliced(self, step):
        self.__fetch_sliced_impl(self.event_loop, self.entry_buffer, step)

        print('\n:::: Fetch statistics ::::')
        print(f'Total entries count: {len(self.entry_buffer)}')
        print(f'Entries with no RSS: {len(self.no_rss)}')
        print(f'Entries with RSS: {len(self.has_rss)}')
        print(f'Entries with RSS in text: {len(self.has_rss_in_text)}')
        print(f'Entries with no url: {len(self.no_url)}')
        print(f'Entries with url but not responding: {len(self.cant_reach)}')

        while len(self.categories["cant_reach"]):
            print('\n:::: Notification :::: ')
            response = input(f'There are {len(self.categories["cant_reach"])} entries with no response. '
                             f'Do you want to check it again (Y/N)? ').casefold()
            if response == 'y' or response == 'yes':
                self.__fetch_sliced_impl(self.event_loop, self.categories["cant_reach"], 20)
            else:
                break

    def __fetch_sliced_impl(self, loop, entries, step):
        start = time.time()
        size = len(entries)
        for chunk in range(size // step + int(bool(size % step))):
            sliced = entries[chunk * step:chunk * step + step]
            if sliced:
                loop.run_until_complete(self.fetch(sliced))
        self.cleanup_categories()
        print("Total time elapsed: {:.2f} seconds".format(time.time() - start))

    def cleanup_categories(self):
        for key, value in self.categories.items():
            if isinstance(value, list):
                self.categories[key] = list(set(value))

    def dump(self, folder):
        utils.dump(self.cant_reach,
                   f'{folder}/cant_reach.txt', 'Results that were not checked due to connection refuse')
        utils.dump(self.no_url,
                   f'{folder}/no_url.txt', 'Results with no url in entry (invalid entry)')
        utils.dump(self.has_rss,
                   f'{folder}/has_rss.txt', 'Results with rss channels')
        utils.dump(self.has_rss_in_text,
                   f'{folder}/has_rss_in_text.txt', 'Results that probably have rss channels (found \'RSS\' in text)')
        utils.dump(self.no_rss,
                   f'{folder}/no_rss.txt', 'Results with no rss channels found')
