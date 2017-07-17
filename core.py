import rssutils
import utils


def show_menu():
    print(f'Welcome to grab-rss v{utils.version}')
    print('Choose an option to continue:')
    print('1 or \'fetch\' :: Fetch rss by url list')
    print('0 or \'exit\' :: Quick exit from grab-rss')
    while True:
        response = input().casefold()
        if response == '1' or response == 'fetch':
            filename = input()
            entries = []
            for title in utils.load(filename):
                entries.append(rssutils.Entry(title))
            print(f'Total entries loaded: {len(entries)}')
            counter = 1
            for entry in entries:
                entry.parse()
                print(f'{counter}. {entry.url} :: {entry.rss}')
                counter += 1

        elif response == '0' or response == 'exit':
            break
        print('Enter new option, please: ')
    print('Thank you for using grab-rss! Good bye!')


def main():
    show_menu()

if __name__ == '__main__':
    main()
