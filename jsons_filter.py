#!/usr/bin/env python

import json
import sys
from collections import OrderedDict

def filter_objects():
    filtered = 0
    total = 0
    for obj in parse_jsons(sys.stdin):
        total += 1
        if should_include(obj):
            print json.dumps(obj)
        else:
            filtered += 1
    print >> sys.stderr, 'Filtered out %d of %d' % (filtered, total)

def parse_jsons(fd):
    for line in fd:
        yield json.loads(line, object_pairs_hook=OrderedDict)

_prohibited = [
    'Adult',
    'Pornographic movie',
    'Pornography',
    'Hardcore pornography',
    'Gay pornography',
    'Sexploitation',
    'Exploitation',
    'Hentai',
    'Softcore Sex Film',
    'Softcore Porn',
    'Sex',
]
def should_include(obj):
    genres = obj.get('genre', tuple())
    for prohibited in _prohibited:
        if prohibited in genres:
            return False
    return True

if __name__ == '__main__':
    filter_objects()
