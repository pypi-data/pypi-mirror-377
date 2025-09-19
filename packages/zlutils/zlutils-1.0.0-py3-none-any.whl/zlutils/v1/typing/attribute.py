from collections import defaultdict
from typing import Callable


ATTRIBUTE_TYPES = ['sync', 'custom', 'default']  # order


class MutationObserver:

    def __init__(self, callback=lambda key, value: print(f'[modify] {key}: {value}')):
        assert isinstance(callback, Callable), f"callback ({callback}) not Callable"
        self.callback = callback

    def __call__(self, key, value):
        self.callback(key, value)


class _Attribute:

    def __init__(self, tag='', default_attribute_type='custom'):
        self._tag = tag
        self._default_attribute_type = default_attribute_type
        self._data = defaultdict(dict)
        self._observers = defaultdict(dict)

    def _wrapKey(self, key):
        assert ('.' not in key) and (not key.startswith('_')), f'属性名({key})包含非法字符:"." 或非法开头"_"'
        if self._tag != '':
            return f'{self._tag}.{key}'
        return key

    '''
    def view(self, tag='', attribute_type=None):
        tag = self._tag if tag == '' else self._wrapKey(tag)
        attribute_type = self._default_attribute_type if attribute_type is None else attribute_type
        new_attribute = _Attribute()
        new_attribute._data = self._data
        new_attribute._tag = tag
        new_attribute._default_attribute_type = attribute_type
        new_attribute._observers = self._observers
        return new_attribute
    '''

    def _toDict(self, total=False):
        d = {}
        for atype in reversed(ATTRIBUTE_TYPES):
            if total:
                d.update(self._data[atype])
            elif self._tag=='':
                d.update({key: value for key, value in self._data[atype].items() if '.' not in key})
            else:
                sptag = self._tag.split('.')
                d.update({key: value for key, value in self._data[atype].items() if sptag == key.split('.')[:len(sptag)]})
        return d

    def _setObserver(self, key, observer, attribute_type=None):
        attribute_type = self._default_attribute_type if attribute_type is None else attribute_type
        key = self._wrapKey(key)
        self._observers[attribute_type][key] = observer
        return self

    def _setAttribute(self, key, value, attribute_type, key_wrap=True):
        wkey = self._wrapKey(key) if key_wrap else key
        self._data[attribute_type][wkey] = value
        default_observer_key = self._wrapKey('')
        if default_observer_key in self._observers[attribute_type]:
            self._observers[attribute_type][default_observer_key](key, value)
        if wkey in self._observers[attribute_type]:
            self._observers[attribute_type][wkey](key, value)
        return self

    def _setDefault(self, key, value, key_wrap = True):
        self._setAttribute(key, value, 'default', key_wrap)

    def __setitem__(self, key, value):
        return self._setAttribute(key, value, attribute_type=self._default_attribute_type)

    def _getAttribute(self, key, attribute_type=None, key_wrap=True):
        key = self._wrapKey(key) if key_wrap else key
        if attribute_type is None:
            for attribute_type in ATTRIBUTE_TYPES:
                if key in self._data[attribute_type]:
                    return self._data[attribute_type][key]
        return self._data[attribute_type][key]

    def get(self, key, default=None, attribute_type=None, key_wrap=True):
        if key in self:
            return self[key]
        else:
            return default

    def __getitem__(self, key):
        return self._getAttribute(key)

    def __getattribute__(self, name):  # 简化调用
        if not name.startswith('_') and name in self:
            return self._getAttribute(name)
        return super().__getattribute__(name)

    def _contains(self, key, attribute_type=None, key_wrap=True):
        key = self._wrapKey(key) if key_wrap else key
        if attribute_type is None:
            for attribute_type in ATTRIBUTE_TYPES:
                if key in self._data[attribute_type]:
                    return True
            return False
        return key in self._data[attribute_type]

    def __contains__(self, key):
        return self._contains(key)

    def _update(self, data, attribute_type='custom'):
        self._data[attribute_type].update(data)
        return self


def Attribute(*arg, **kwarg):
    return _Attribute(*arg, **kwarg)
