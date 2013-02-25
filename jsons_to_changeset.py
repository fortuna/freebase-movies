#!/usr/bin/env python

from elementtree.SimpleXMLWriter import XMLWriter
import changeset
import json
import sys
from collections import OrderedDict

def write_changeset():
    w = XMLWriter(sys.stdout)
    w.start("changeset")
    for obj in parse_jsons(sys.stdin):
        changeset.write_set_item(w, obj)
    w.end('changeset')

def parse_jsons(fd):
    for line in fd:
        yield json.loads(line, object_pairs_hook=OrderedDict)

if __name__ == '__main__':
    write_changeset()
