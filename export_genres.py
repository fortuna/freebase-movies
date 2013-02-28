#!/usr/bin/env python
from apiclient import discovery, model
from apiclient.errors import HttpError
from collections import OrderedDict
import json
import sys
import time

mql = [{
  'limit': 1000,
  'id':   None,
  'name': None,
  'type': '/film/film_genre',
  '/media_common/media_genre/child_genres': [{'id':None, 'type':[], 'name':None, 'optional' : True}],
  '/media_common/media_genre/parent_genre': [{'id':None, 'type':[], 'name':None, 'optional' : True}],
}]

MAX_REQUEST_RETRIES = 10
RETRY_SLEEP_SECS = 5

def main(developer_key):
    freebase = discovery.build('freebase', 'v1', developerKey=developer_key)
    objects = get_genre_objects(freebase)
    print json.dumps(objects, indent=2)
    print >>sys.stderr, 'Exported %d genres' % (len(objects),)

def get_genre_objects(freebase):
    result = list()
    cursor = ''
    retry_count = 0
    while cursor is not None and (MAX_REQUEST_RETRIES == -1 or retry_count < MAX_REQUEST_RETRIES):
        try:
            raw_response = freebase.mqlread(query=json.dumps(mql), cursor=cursor).execute()
            retry_count = 0 # success, reset retry count
            response = json.loads(raw_response, object_pairs_hook=OrderedDict)
            cursor = response.get('cursor')
            result.extend(response.get('result', list()))
            if not cursor:
                cursor = None
        except HttpError, e:
            retry_count += 1
            print >>sys.stderr, e
            print >>sys.stderr, 'About to retry %d with cursor=%s' % (retry_count, cursor,)
            time.sleep(RETRY_SLEEP_SECS)
            print >>sys.stderr, 'Retrying %d with cursor=%s' % (retry_count, cursor,)
    return result

if __name__ == '__main__':
    main(*sys.argv[1:])
