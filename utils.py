version = '0.1'
project_title = 'RSS Grabber'


def cast_exception(exception):
    prefix = 'ERROR :: '
    print(f'{prefix}{exception}')


def load(filename):
    if not filename.startswith('data/'):
        filename = 'data/' + filename

    result = []
    try:
        with open(filename, 'r') as f:
            result = f.readlines()
    except IsADirectoryError as e:
        cast_exception(e)
    except FileNotFoundError as e:
        cast_exception(e)

    return result
