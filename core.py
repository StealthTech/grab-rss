import rssutils
import utils

VERSION = '0.1'


def menu():
    print(f'Welcome to grab-rss v{VERSION}')
    print('Choose an option to continue:')
    print('1 or \'fetch\' :: Fetch rss by url list')
    while True:
        response = input().casefold()
        if response == '1' or response == 'fetch':
            filename = input()
            urls = []
            for title in utils.load(filename):
                urls.append(rssutils.fetch_url(title))
            for url in urls:
                print('res', rssutils.pull(url))
        elif response == '0' or response == 'stop':
            break
        print('Enter new option, please: ')
    print('Thank you for using grab-rss! Good bye!')


def main():
    menu()

if __name__ == '__main__':
    main()