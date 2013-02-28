#!/usr/bin/env python

from elementtree.SimpleXMLWriter import XMLWriter
import itertools
import json
import sys

_warn_missing_parent = False
_warn_missing_child = False

def main():
    genre_objects = json.load(sys.stdin)
    registry = {}
    for obj in genre_objects:
        registry[obj['id']] = obj

    _validate_parent_child_relationships(registry)

    top_level = [obj for obj in genre_objects if len(obj['_parent_ids']) == 0]

    touched = set()
    paths = set()

    w = XMLWriter(sys.stdout)
    w.start("dimension", {'id':'genre', 'type':'tree'})
    for obj in top_level:
        process_genre(w, obj, '', registry, touched, paths)
    w.end('dimension')

    _assert_all_visited(registry, touched)

def _validate_parent_child_relationships(registry):
    for obj in registry.values():
        obj['_parent_ids'] = [genre['id'] for genre in obj.get('/media_common/media_genre/parent_genre', list())]
        obj['_child_ids'] = [genre['id'] for genre in obj.get('/media_common/media_genre/child_genres', list())]
        if '/media_common/media_genre/parent_genre' in obj:
            del obj['/media_common/media_genre/parent_genre']
        if '/media_common/media_genre/child_genres' in obj:
            del obj['/media_common/media_genre/child_genres']

    for obj in registry.values():
        for parent_id in list(obj['_parent_ids']):
            if parent_id not in registry:
                obj['_parent_ids'].remove(parent_id)
                if _warn_missing_parent:
                    print >> sys.stderr, 'Parent %s of %s (%s) not in registry' % (parent_id, obj['id'], obj.get('name'))
            elif obj['id'] not in registry[parent_id]['_child_ids']:
                print >> sys.stderr, 'Adding missing child link to parent'
                registry[parent_id]['_child_ids'].append(obj['id'])

        for child_id in list(obj['_child_ids']):
            if child_id not in registry:
                obj['_child_ids'].remove(child_id)
                if _warn_missing_child:
                    print >> sys.stderr, 'Child %s of %s (%s) not in registry' % (child_id, obj['id'], obj.get('name'))
            elif obj['id'] not in registry[child_id]['_parent_ids']:
                print >> sys.stderr, 'Adding missing parent link to child'
                registry[child_id]['_parent_ids'].append(obj['id'])

def _assert_all_visited(registry, touched):
    all_names = set()
    all_names.update([obj['name'] for obj in registry.values()])
    not_touched = all_names.difference(touched)
    if len(not_touched) > 0:
        print >> sys.stderr, 'missed %d' % (len(not_touched), )
        print >> sys.stderr, not_touched
        for name in not_touched:
            for obj in [obj for obj in registry.values() if obj['name'] == name]:
                print >> sys.stderr, json.dumps(obj, indent=2)
                for pid in obj['_parent_ids']:
                    if pid not in registry:
                        print >> sys.stderr, '    %s not in registry' % (pid, )
                    else:
                        print >> sys.stderr, '    parent %s found in registry' % (pid, )
                        print >> sys.stderr, '    child_ids: %s' % (registry[pid]['_child_ids'])

def process_genre(w, obj, path, registry, touched, paths):
    if len(path) > 0:
        my_path = '%s|%s' % (path,obj['name'])
    else:
        my_path = obj['name']
    if my_path not in paths or len(obj['_child_ids']) > 0:
        paths.add(my_path)
        touched.add(obj['name'])
        not_in_registry = [child_id for child_id in obj['_child_ids'] if child_id not in registry]
        if len(not_in_registry) > 0:
            print >> sys.stderr, '%s has children not in registry: %s' % (obj['id'], not_in_registry)
        children = [registry[child_id] for child_id in obj['_child_ids'] if child_id in registry]
        element_properties = {'id':obj['name']}
        if my_path != obj['name']:
            element_properties.update({'id': my_path, 'value': obj['name'], 'name':obj['name']})
        w.start('element', element_properties)
        for child in children:
            process_genre(w, registry[child['id']], my_path, registry, touched, paths)
        w.end('element')
    else:
        print >> sys.stderr, 'Already saw %s skipping ' % (my_path,)

if __name__ == '__main__':
    main()
