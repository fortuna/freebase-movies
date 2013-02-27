#!/usr/bin/env python

import json
import sys
import urllib2
from collections import OrderedDict
from elementtree.SimpleXMLWriter import XMLWriter

ENGINE_QUERY = '''
{
  "facets": {
    "%(dimension)s": {
      "topN": 1000,
      "minCount": %(min_count)d,
      "sortBy":"countDesc"
    }
  }
}
'''
ENGINE_URL = 'http://freebase-movies.discoverysearchengine.com:8090/'

def main():
    dimension = sys.argv[1]
    min_count = int(sys.argv[2])
    engine_response = _json_post('%s/ws/query' % (ENGINE_URL), ENGINE_QUERY % {'dimension':dimension, 'min_count': min_count})
    facets = engine_response['facets'][dimension]['childIds']
    w = XMLWriter(sys.stdout)
    w.start("dimension", {'id': dimension, 'type': 'tree'})
    for facet in facets:
        w.start('element', {'id': facet, '_count':str(engine_response['facets'][dimension]['data'][facet]['count'])})
        w.end('element')
    w.end('dimension')

def _json_post(url, data):
    httpReq = urllib2.Request(url, data,{'Content-Type': 'application/json'})
    return json.loads(urllib2.urlopen(httpReq).read(), object_pairs_hook=OrderedDict)

if __name__ == '__main__':
    main()
