import rssutils
import utils


def menu_option_fetch():
    filename = input('Enter the name of file with url list: ')
    entries = []
    for title in utils.load(filename):
        entries.append(rssutils.Entry(title))
    print(f'Total entries loaded: {len(entries)}')
    counter = 1
    for entry in entries:
        entry.parse()
        if len(entry.rss):
            print(f'{counter}. {entry.url} :: {entry.title} :: Found {len(entry.rss)} RSS channel(s)')
            for rss in entry.rss:
                print(f'∟ {rss}')
        else:
            print(f'{counter}. {entry.url} :: {entry.title} :: No RSS channels found')

        counter += 1


def show_menu():
    print(f'Welcome to grab-rss v{utils.version}')
    print('Choose an option to continue:')
    print('1 or \'fetch\' :: Fetch rss by url list')
    print('0 or \'exit\' :: Quick exit from grab-rss')
    while True:
        response = input().casefold()

        if response == '1' or response == 'fetch':
            menu_option_fetch()

        elif response == '0' or response == 'stop' or response == 'exit' or response == 'quit' or response == 'q':
            break
        print('Enter new option, please: ')
    print('Thank you for using grab-rss! Good bye!')


def main():
    show_menu()

if __name__ == '__main__':
    main()
