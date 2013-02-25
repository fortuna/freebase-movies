#!/usr/bin/env python
from collections import OrderedDict

def require(event, node, expectedEvent=None, expectedName=None):
    if expectedEvent is not None and expectedEvent != event:
        raise IOError("Expected %s got %s" % (expectedEvent, event))
    if expectedName is not None and expectedName != node.nodeName:
        raise IOError("Expected %s got %s" % (expectedName, node.nodeName))

def as_int(value):
    try:
        return int(value)
    except ValueError:
        return None

def as_float(value):
    try:
        return float(value)
    except ValueError:
        return None

def as_bool(value):
    if value == 'true':
        return True
    elif value == 'false':
        return False
    else:
        return None

def _action_attributes(properties):
    result = {}
    if '_locator' in properties:
        result['locator'] = properties['_locator']
        if '_provider' in properties:
            result['provider'] = properties['_provider']
        if '_kind' in properties:
            result['kind'] = properties['_kind']
    elif '_id' in properties:
        result['id'] = properties['_id']
    else:
        raise Exception('Unable to extract action attributes from ' + properties)
    return result

def _write_value(w, value, trim_empty_strings=True):
    if value is None:
        pass
    elif type(value) == list:
        if len(value) > 0:
            w.start('array')
            for v in value:
                w.start('element')
                _write_value(w, v, False)
                w.end('element')
            w.end('array')
    elif type(value) in [dict, OrderedDict]:
        if len(value) > 0:
            w.start('struct')
            for k, v in value.items():
                w.start('entry', name=k)
                _write_value(w, v)
                w.end('entry')
            w.end('struct')
    elif type(value) == int:
        w.element('int', str(value))
    elif type(value) == float:
        w.element('real', str(value))
    elif type(value) == bool:
        w.element('bool', '1' if value else '0')
    elif type(value) == str or type(value) == unicode:
        value = value.strip()
        if len(value) > 0 or not trim_empty_strings:
            w.element('string', value)
    else:
        raise Exception('Unexpected ' + type(value) + ' value: ' + value)

def write_set_item(w, properties):
    w.start('set-item', _action_attributes(properties))
    w.start('properties')
    w.start('struct')
    for name, value in properties.items():
        if name.startswith('_'):
            continue
        w.start('entry', name=name)
        _write_value(w, value)
        w.end('entry')
    w.end('struct')
    w.end('properties')
    w.end('set-item')
