from rssutils import rssutils
import utils
import asyncio
import aiohttp
import time

parsed_count = 0


async def parse(entry, categories, session):
    global parsed_count

    if not entry.url:
        parsed_count += 1
        # print(f'{parsed_count}. {entry.entry} :: Invalid format (no url specified)')

        if entry not in categories['no_url']:
            categories['no_url'].append(entry)
        print(f'{parsed_count}. {entry.entry} :: Invalid entry format (no url specified)')
        return

    # print(f'Started parsing of {entry.url}')
    await entry.parse(session)
    if entry.request_error:
        parsed_count += 1
        if entry not in categories:
            categories['cant_reach'].append(entry)
        print(f'{parsed_count}. {entry.entry} :: {entry.url} :: Server not responding (can\'t reach) :: {entry.request_error}')
    elif len(entry.rss):
        parsed_count += 1
        if entry not in categories:
            categories['has_rss'].append(entry)
        print(f'{parsed_count}. {entry.url} :: {entry.title} :: Found {len(entry.rss)} RSS channel(s)')
        subcounter = 1
        for rss in entry.rss:
            print(f'   ∟ {subcounter}. {rss}')
            subcounter += 1
    elif entry.rss_in_text:
        if entry not in categories:
            categories['has_rss_in_text'].append(entry)
    else:
        parsed_count += 1
        if entry not in categories:
            categories['no_rss'].append(entry)
        print(f'{parsed_count}. {entry.url} :: {entry.title} :: No RSS channels found')


async def fetch(entries, categories):
    global parsed_count

    start = time.time()
    with aiohttp.ClientSession() as session:
        tasks = [asyncio.ensure_future(parse(entry, categories, session)) for entry in entries]
        await asyncio.wait(tasks)
    print("Process took: {:.2f} seconds".format(time.time() - start))


def fetch_sliced(loop, lst, categories, step):
    start = time.time()
    size = len(lst)
    for chunk in range(size // step + int(bool(size % step))):
        sliced = lst[chunk * step:chunk * step + step]
        if sliced:
            loop.run_until_complete(fetch(sliced, categories))
    print("Total time elapsed: {:.2f} seconds".format(time.time() - start))


def cleanup_doubles(lst):
    if isinstance(lst, list):
        return list(set(lst))


def menu_option_fetch():
    filename = input('Enter the name of file with url list: ')

    entries = []

    payload = utils.load(filename)
    if not payload:
        print(f'Can\'t open file {filename}')
        return

    for title in payload:
        entries.append(rssutils.Entry(title))
    print(f'Total entries loaded: {len(entries)}')

    categories = {
        'no_rss': [],
        'has_rss': [],
        'has_rss_in_text': [],
        'no_url': [],
        'cant_reach': [],
    }

    global parsed_count

    event_loop = asyncio.get_event_loop()

    fetch_sliced(event_loop, entries, categories, 50)

    parsed_count = 0

    for key, value in categories.items():
        if isinstance(value, list):
            categories[key] = cleanup_doubles(value)

    print(':::: Fetch statistics ::::')
    print(f'Total entries count: {len(entries)}')
    print(f'Entries with no RSS: {len(categories["no_rss"])}')
    print(f'Entries with RSS: {len(categories["has_rss"])}')
    print(f'Entries with RSS in text: {len(categories["has_rss_in_text"])}')
    print(f'Entries with no url: {len(categories["no_url"])}')
    print(f'Entries with url but not responding: {len(categories["cant_reach"])}')

    while len(categories['cant_reach']):
        print('\n:::: Notification :::: ')
        response = input(f'There are {len(categories["cant_reach"])} entries with no response. '
                         f'Do you want to check it again (Y/N)? ').casefold()
        if response == 'y' or response == 'yes':
            fetch_sliced(event_loop, categories['cant_reach'], categories, 20)
        else:
            break

    response = input(f'Do you want to dump results to folder \'{filename}\' (Y/N)? ').casefold()
    if response == 'y' or response == 'yes':
        utils.dump(categories['cant_reach'],
                   f'{filename}/cant_reach.txt', 'Results that were not checked due to connection refuse')
        utils.dump(categories['no_url'],
                   f'{filename}/no_url.txt', 'Results with no url in entry (invalid entry)')
        utils.dump(categories['has_rss'],
                   f'{filename}/has_rss.txt', 'Results with rss channels')
        utils.dump(categories['has_rss_in_text'],
                   f'{filename}/has_rss_in_text.txt', 'Results that probably have rss channels (found \'RSS\' in text)')
        utils.dump(categories['no_rss'],
                   f'{filename}/no_rss.txt', 'Results with no rss channels found')


def show_menu():
    print(f'Welcome to {utils.project_title} {utils.version}')
    print('Choose an option to continue:')
    print('1 or \'fetch\' :: Fetch rss by url list')
    print('0 or \'exit\' :: Quick exit from grab-rss')
    while True:
        response = input('> ').casefold()

        if response == '1' or response == 'fetch':
            menu_option_fetch()

        elif response == '0' or response == 'stop' or response == 'exit' or response == 'quit' or response == 'q':
            break
        print('\nEnter new option, please: ')
    print(f'Thank you for using {utils.project_title}! Good bye!')


def main():
    show_menu()

if __name__ == '__main__':
    main()
