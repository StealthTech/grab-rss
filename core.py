import asyncio

from rss import utils
from rss.entries import Entry, EntryManager


def menu_option_fetch():
    filename = input('Enter the name of file with url list: ')

    entry_manager = EntryManager()

    payload = utils.load(filename)
    if not payload:
        print(f'Can\'t open file {filename}')
        return

    for title in payload:
        entry_manager.add_entry(Entry(title))

    print(f'Total entries loaded: {entry_manager.count}')

    event_loop = asyncio.get_event_loop()

    entry_manager.fetch_sliced(event_loop, 50)

    response = input(f'Do you want to dump results to folder \'{filename}\' (Y/N)? ').casefold()
    if response == 'y' or response == 'yes':
        utils.dump(entry_manager.cant_reach,
                   f'{filename}/cant_reach.txt', 'Results that were not checked due to connection refuse')
        utils.dump(entry_manager.no_url,
                   f'{filename}/no_url.txt', 'Results with no url in entry (invalid entry)')
        utils.dump(entry_manager.has_rss,
                   f'{filename}/has_rss.txt', 'Results with rss channels')
        utils.dump(entry_manager.has_rss_in_text,
                   f'{filename}/has_rss_in_text.txt', 'Results that probably have rss channels (found \'RSS\' in text)')
        utils.dump(entry_manager.no_rss,
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
