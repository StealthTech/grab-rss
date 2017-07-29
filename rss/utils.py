import os

echo = True

version = '0.2'
project_title = 'RSS Grabber'

__data_dir = 'data/'
__input_dir = __data_dir + 'input/'
__output_dir = __data_dir + 'output/'

__ext_url_list = 'urls'
__ext_report = 'repr'


def cast_exception(exception):
    prefix = 'ERROR :: '
    print(f'{prefix}{exception}')


def load(filename):
    if not filename.startswith(__input_dir):
        filepath = __input_dir + filename
    else:
        filepath = filename

    if not os.path.isdir(filepath):
        filedir = os.path.dirname(os.path.abspath(filepath))

        if not os.path.exists(filedir):
            os.makedirs(filedir)

    result = None
    try:
        with open(filepath, 'r') as f:
            result = f.read().strip().split('\n')
    except IsADirectoryError as e:
        cast_exception(e)
    except FileNotFoundError as e:
        cast_exception(e)

    return result


def dump(entries, filename, heading=None):
    filepath = __output_dir + filename
    filedir = os.path.dirname(os.path.abspath(filepath))

    if not os.path.exists(filedir):
        os.makedirs(filedir)

    if os.path.exists(filepath) and not os.path.isdir(filepath):
        response = input(f'File \'{filepath}\' already exists. '
                         f'Are you sure you want to overwrite it (Y/N)?  ').casefold()
        if not (response == 'yes' or response == 'y'):
            print('Dump aborted. No changes were saved')
            return

    try:
        with open(filepath, 'w') as f:
            if heading:
                f.write(f'::: {heading} :::\n')
                f.write(f'::: Number of matching entries: {len(entries)} :::\n\n')
            if len(entries):
                for number, entry in enumerate(entries):
                    f.write(f'= = = = = = = = = = {number} = = = = = = = = = =\n')
                    f.write(f'Entry: {entry.entry}\n')
                    if entry.title:
                        f.write(f'Title: {entry.title}\n')
                    if entry.url:
                        f.write(f'URL: {entry.url}\n')

                    if len(entry.rss):
                        counter = 1
                        for rss_link in entry.rss:
                            f.write(f'RSS{counter}: {rss_link}\n')
                            counter += 1
                    f.write('\n')
            else:
                f.write('There\'s no matching results.\n')
    except IsADirectoryError as e:
        cast_exception(e)
    print(f'Dumped successfully to \'{filepath}\'')
