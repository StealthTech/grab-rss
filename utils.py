import os


def load(filename):
    result = []
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            result = f.readlines()
    else:
        print('ERROR: File does not exist')
    return result
