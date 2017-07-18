from rssutils import rssutils
import utils


def menu_option_fetch():
    filename = input('Enter the name of file with url list: ')

    entries = []

    payload = utils.load(filename)
    if not payload:
        return

    for title in payload:
        entries.append(rssutils.Entry(title))
    print(f'Total entries loaded: {len(entries)}')

    entries_no_rss = []
    entries_has_rss = []
    entries_has_rss_in_text = []
    entries_no_url = []
    entries_cant_reach = []

    counter = 1
    for entry in entries:
        entry.parse()

        if entry.request_error:
            entries_cant_reach.append(entry)
        elif entry.url == '':
            entries_no_url.append(entry)
        elif len(entry.rss):
            entries_has_rss.append(entry)
        elif entry.rss_in_text:
            entries_has_rss_in_text.append(entry)
        else:
            entries_no_rss.append(entry)

        if len(entry.rss):
            print(f'{counter}. {entry.url} :: {entry.title} :: Found {len(entry.rss)} RSS channel(s)')
            subcounter = 1
            for rss in entry.rss:
                print(f'   ∟ {subcounter}. {rss}')
                subcounter += 1
        else:
            print(f'{counter}. {entry.url} :: {entry.title} :: No RSS channels found')

        counter += 1

    utils.dump(entries_cant_reach, f'{filename}/cant_reach.txt', 'Results that were not checked due to connection refuse')
    utils.dump(entries_no_url, f'{filename}/no_url.txt', 'Results with no url in entry (invalid entry)')
    utils.dump(entries_has_rss, f'{filename}/has_rss.txt', 'Results with rss channels')
    utils.dump(entries_has_rss_in_text, f'{filename}/has_rss_in_text.txt', 'Results that probably have rss channels '
                                                                           '(found no meta but \'RSS\' in text)')
    utils.dump(entries_no_rss, f'{filename}/no_rss.txt', 'Results with no rss channels found')


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
