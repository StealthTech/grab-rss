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

        categories['no_url'].append(entry)
        print(f'{parsed_count}. {entry.entry} :: Invalid entry format (no url specified)')
        return

    # print(f'Started parsing of {entry.url}')
    await entry.parse(session)
    if entry.request_error:
        parsed_count += 1
        categories['cant_reach'].append(entry)
        print(f'{parsed_count}. {entry.entry} :: {entry.url} :: Server not responding (can\'t reach) :: {entry.request_error}')
    elif len(entry.rss):
        parsed_count += 1
        categories['has_rss'].append(entry)
        print(f'{parsed_count}. {entry.url} :: {entry.title} :: Found {len(entry.rss)} RSS channel(s)')
        subcounter = 1
        for rss in entry.rss:
            print(f'   ∟ {subcounter}. {rss}')
            subcounter += 1
    elif entry.rss_in_text:
        categories['has_rss_in_text'].append(entry)
    else:
        parsed_count += 1
        categories['no_rss'].append(entry)
        print(f'{parsed_count}. {entry.url} :: {entry.title} :: No RSS channels found')

    # if len(entry.rss):
    #     parsed_count += 1
    #     print(f'{parsed_count}. {entry.url} :: {entry.title} :: Found {len(entry.rss)} RSS channel(s)')
    #     subcounter = 1
    #     for rss in entry.rss:
    #         print(f'   ∟ {subcounter}. {rss}')
    #         subcounter += 1
    # elif not entry.url:
    #     parsed_count += 1
    #     print(f'{parsed_count}. {entry.entry} :: Invalid entry format')
    # else:
    #     parsed_count += 1
    #     print(f'{parsed_count}. {entry.url} :: {entry.title} :: No RSS channels found')


# def fetch(entries, categories):
#     coroutines = [parse(entry, categories) for entry in entries]
#     event_loop = asyncio.get_event_loop()
#     event_loop.run_until_complete(asyncio.wait(coroutines))
#     event_loop.close()

async def fetch(entries, categories):
    global parsed_count

    start = time.time()
    with aiohttp.ClientSession() as session:
        tasks = [asyncio.ensure_future(parse(entry, categories, session)) for entry in entries]
        await asyncio.wait(tasks)
    print("Process took: {:.2f} seconds".format(time.time() - start))


def menu_option_fetch():
    filename = input('Enter the name of file with url list: ')

    entries = []

    payload = utils.load(filename)
    if not payload:
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

    # parse

    event_loop = asyncio.get_event_loop()
    step = 20

    start = time.time()
    for i in range(len(entries) // 10 + int(bool(len(entries) % step))):
        # print(entries[i * step:i * step + step])
        entries_sliced = entries[i * step:i * step + step]
        if entries_sliced:
            event_loop.run_until_complete(fetch(entries_sliced, categories))
    print("Total time elapsed: {:.2f} seconds".format(time.time() - start))

    global parsed_count
    parsed_count = 0

    print(':::: Fetch statistics ::::')
    print(f'Total entries count: {len(entries)}')
    print(f'Entries with no RSS: {len(categories["no_rss"])}')
    print(f'Entries with RSS: {len(categories["has_rss"])}')
    print(f'Entries with RSS in text: {len(categories["has_rss_in_text"])}')
    print(f'Entries with no url: {len(categories["no_url"])}')
    print(f'Entries with url but not responding: {len(categories["cant_reach"])}')

    response = input(f'Do you want to dump results to folder \'{filename}\' (Y/N)?')
    if response.casefold() == 'y':
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

# 20, 3 13 1 1 2
# 20, 3 12 1 1 3

def show_menu():
    print(f'Welcome to {utils.project_title} {utils.version}')
    print('Choose an option to continue:')
    print('1 or \'fetch\' :: Fetch rss by url list')
    print('0 or \'exit\' :: Quick exit from grab-rss')
    while True:
        response = input().casefold()

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
