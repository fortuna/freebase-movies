#!/usr/bin/env python
import itertools
import os
import sys
from collections import defaultdict, OrderedDict
import json

TSV_DIR = 'film'
_dict_factory = OrderedDict
_trimmed_properties = [
    '_locator','_kind','name','tagline','initial_release_date','genre','rating','runtime_runtime',
    'starring_actor','starring_character','directed_by','written_by',]

def parse_all(files_or_kinds):
    kinds = [os.path.splitext(x)[0] for x in files_or_kinds]
    registry = load_registry()

    if kinds == ['all']:
        kinds = registry.keys()
    elif kinds == [''] or len(kinds) == 0:
        kinds = DEFAULT_KINDS

    for values_dict in [v for k,v in registry.items() if k in kinds]:
        for obj in values_dict.values():
            print json.dumps(_normalize(obj, registry))

def load_registry():
    registry = defaultdict(_dict_factory)
    for filename in os.listdir(TSV_DIR):
        with open(os.path.join(TSV_DIR, filename)) as fd:
            kind = os.path.splitext(filename)[0]
            for obj in parse_tsv(filename, fd):
                obj['_kind'] = kind
                if obj['id'] in registry.get(kind, dict()):
                    print >>sys.stderr, 'Id conflict %s %s\n  %s\n  %s\n' % (kind, obj['id'], registry[kind][obj['id']], obj)
                else:
                    registry[kind][obj['id']] = obj
    return registry

def parse_tsv(filename, fd):
    keys = [v.strip() for v in fd.readline().split('\t')]
    num_keys = len(keys)
    for line, linenum in itertools.izip(fd, itertools.count(1)):
        values = [v.strip() for v in line.split('\t')]
        num_values = len(values)
        if num_values < num_keys:
            print >>sys.stderr, 'Skipping invalid line with too few fields %s %d expected: %s actual: %s\n%s' % (filename, linenum, num_keys, num_values, line,)
        else:
            if len(values) != len(keys):
                print >>sys.stderr, 'Processing line with extra fields %s %d expected: %s actual: %s\n%s' % (filename, linenum, num_keys, num_values, line,)
            yield _dict_factory(zip(keys, values))

def _normalize(obj, registry):
    result = _dict_factory((k,v) for k, v in obj.items() if v != '')
    result.update({
        '_locator': obj['id'],
        '_kind': obj['_kind'],
    })
    del result['id']
    _split_values(result, ['name','tagline','initial_release_date'])
    _connect_references(result, registry)
    if obj['_kind'] == 'film':
        _make_parallel_lists(result, 'starring', ['actor','character',])
        _make_parallel_lists(result, 'runtime', ['runtime'])
        if 'runtime_runtime' in result:
            result['runtime_runtime'] = result['runtime_runtime'][0]
        result = _dict_factory([(k,v) for k,v in result.items() if k in _trimmed_properties])
    else:
        for key in result.keys():
            _make_parallel_lists(result, key)
    return result

def _make_parallel_lists(result, key, nested_keys=None):
    if key in result:
        v = result[key]
        if nested_keys is None:
            nested_keys = set()
            for value in [value for value in v if type(value) == _dict_factory]:
                nested_keys.update(value.keys())
        for nested_key in nested_keys:
            if len([value[nested_key] for value in v if type(value) == _dict_factory if value[nested_key] != '']) > 0:
                if not key + '_' + nested_key in result:
                    result.update({key + '_' + nested_key: [value[nested_key] for value in v if type(value) == _dict_factory]})

def _split_values(result, ignore_keys=tuple()):
    for k,v in [(k,v) for k,v in result.items() if not k.startswith('_') and k not in ignore_keys]:
        result.update({k: v.split(',')})

def _connect_references(result, registry):
    for k,v in result.items():
        if not k.startswith('_') and k != 'id' and type(v) == list:
            result.update({k: list(itertools.chain(*(_find_by_id(registry, locator) for locator in result.get(k, list()))))})

def _find_by_id(registry, locator):
    if not locator.startswith('/m/'):
        yield locator
    else:
        num_found = 0
        other_kind = ''
        for v in registry.values():
            if locator in v:
                num_found += 1
                if num_found > 1:
                    print >>sys.stderr, 'Multiple objects found with id %s\n\t%s\n\t%s\n\n' % (locator,v[locator]['_kind'], other_kind)
                other_kind = v[locator]['_kind']
                yield v[locator]

DEFAULT_KINDS = [os.path.splitext(x)[0] for x in '''
actor.tsv
cinematographer.tsv
director.tsv
dubbing_performance.tsv
editor.tsv
film.tsv
film_art_director.tsv
film_casting_director.tsv
film_character.tsv
film_costumer_designer.tsv
film_crewmember.tsv
film_critic.tsv
film_cut.tsv
film_cut_type.tsv
film_distribution_medium.tsv
film_distributor.tsv
film_featured_song.tsv
film_festival.tsv
film_festival_event.tsv
film_festival_focus.tsv
film_festival_sponsor.tsv
film_festival_sponsorship.tsv
film_film_company_relationship.tsv
film_film_distributor_relationship.tsv
film_format.tsv
film_genre.tsv
film_job.tsv
film_location.tsv
film_production_designer.tsv
film_regional_release_date.tsv
film_screening_venue.tsv
film_series.tsv
film_set_designer.tsv
film_song.tsv
film_song_performer.tsv
film_song_relationship.tsv
film_story_contributor.tsv
film_subject.tsv
film_theorist.tsv
music_contributor.tsv
performance.tsv
person_or_entity_appearing_in_film.tsv
personal_film_appearance.tsv
personal_film_appearance_type.tsv
producer.tsv
production_company.tsv
writer.tsv
'''.split('\n')]

if __name__ == '__main__':
    parse_all(sys.argv[1:])
