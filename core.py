from rss import utils
from rss.entries import Entry, EntryManager


def menu_option_fetch():
    filename = input('Enter the name of file with url list: ')

    entry_manager = EntryManager()

    entry_manager.load_file(filename)

    entry_manager.fetch_sliced(50)

    response = input(f'Do you want to dump results to folder \'{filename}\' (Y/N)? ').casefold()
    if response == 'y' or response == 'yes':
        entry_manager.dump(filename)


def show_menu():
    options = {
        'fetch': ['1', 'fetch'],
        'quit': ['0', 'stop', 'exit', 'quit', 'q'],
    }

    print(f'Welcome to {utils.project_title} {utils.version}')
    print('Choose an option to continue:')
    print('1 or \'fetch\' :: Fetch rss channels from url list')
    print('0 or \'exit\' :: Quick exit from grab-rss')
    while True:
        response = input('> ').casefold()

        if response in options['fetch']:
            menu_option_fetch()
        elif response in options['quit']:
            break
        print('\nEnter new option, please: ')
    print(f'Thank you for using {utils.project_title}! Good bye!')


def main():
    show_menu()

if __name__ == '__main__':
    main()
