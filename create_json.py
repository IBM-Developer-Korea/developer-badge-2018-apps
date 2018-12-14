#!/usr/bin/env python

import json
import os.path


def get_json(appdir):
    try:
        with open('{}/app.json'.format(appdir)) as fp:
            return json.load(fp)
    except IOError as e:
        print('Error: Cannot open app.json from: {}'.format(appdir))
        raise e
    except ValueError as e:
        print('Error: Cannot parse app.json from: {}'.format(appdir))
        raise e
    except Exception as e:
        raise e

def main(jsonfile):
    app_list = {}
    for app in os.listdir('.'):
        data = get_json(app)
        app_list[app] = data
    with open(jsonfile, 'w') as fp:
        json.dump(app_list, fp, indent=2)

if __name__ == '__main__':
    import sys
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        print('Usage: {} <output.json>'.format(sys.argv[0]))
