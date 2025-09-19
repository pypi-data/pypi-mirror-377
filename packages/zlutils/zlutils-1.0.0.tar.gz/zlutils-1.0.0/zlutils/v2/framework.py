import os
import queue
import time
import threading
from collections import defaultdict
from zlutils.v1.typing.dataitem import DataItem

def _fixPathList(plist):
    ret = []
    for sep in plist:
        sep = sep.strip()
        if len(sep) == 0:
            continue
        cdot = sep.count('.')
        if cdot == len(sep):
            ret = ret[:len(ret)-cdot+1]
            continue
        ret.append(sep)
    return ret


def _pathJoin(base, name=''):
    base = base.strip()
    name = name.strip()
    ret = ''
    if base.startswith('/'):
        ret = '/'
    topflag = True
    plist = base.split('/') + name.split('/')
    plist = _fixPathList(plist)
    ret += '/'.join(plist)
    return ret


class Event(DataItem):
    # 事件类
    name = 'undef'
    target = None
    data = None


class Unit:
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get('name', self.__class__.__name__)
        # self.target_plist = target_path.split('/')
        self.parent = kwargs.get('parent', None)
        # self.raw_subscribs = defaultdict(list)
        self.event_listeners = defaultdict(list)
        self.plugins = {}
        # self.listeners = None
        self.event_threading = None
        self.event_queue = queue.Queue()

        self.init(*args, **kwargs)
        # auto
        self._startEventThreading()

    def init(self, *args, **kwargs):
        pass


    @property
    def uapi(self):
        if self.parent is None:
            return self
        return self.parent.uapi

    @property
    def upath(self):
        if self.parent is None:
            return '/' + self.name
        return _pathJoin(self.parent.target_path, self.name)

    def _wrapPath(self, path):
        path = path.strip()
        if path.startswith('/'):
            return path
        return _pathJoin(self.upath, path)


    def subscribeEvent(self, path, callback, priority=-1):
        self.event_listeners[path].append((callback, priority))
        return self.uapi._subscribeEvent(self._wrapPath(path), callback, priority)

    def _subscribeEvent(self, _path, callback, priority=-1):
        self.event_listeners.append((callback, priority))

    def _unsubscribeEvent(self, _path, callback):
        try:
            idx = self.event_listeners[_path].index(callback)
            self.event_listeners[_path].remove(idx)
        except:
            pass

    def publishEvent(self, event: Event):
        path = self._wrapPath(event.name)
        return self.uapi._publishEvent(path, event)

    def _publishEvent(self, path, event: Event):
        self.event_queue.put((path, event, time.time()))
        # self.startEventThreading()
        # if path in self.subscribs:

    def _startEventThreading(self):
        if self.event_threading is None or not self.event_threading.is_alive():
            self.event_threading = threading.Thread(target=self._eventThreading)
            self.event_threading.start()
        pass

    def _stopEventThreading(self):
        self.event_queue.put(None)

    def _eventThreading(self):
        while True:
            pac = self.event_queue.get()
            if pac is None:
                break
            path, event, ts = pac
            for func in self.event_listeners[path]:
                func(event)

    def plug(self, target: Unit):
        # 关闭自身的事件线程
        self._stopEventThreading()
        self.parent = target
        self.parent.plugins[self.name] = self
        for rpath in self.event_listeners:
            path = self._wrapPath(rpath)
            for callback, priority = self.event_listeners[rpath]:
                self.uapi._subscribeEvent(path, callback, priority)

    def unplug(self):
        del self.parent.plugins[self.name]
        self.parent = None
        for rpath in self.event_listeners:
            path = self._wrapPath(rpath)
            for callback, priority = self.event_listeners[rpath]:
                self.uapi._unsubscribeEvent(path, callback)
        self._startEventThreading()


        # TODO publishEvent, plug, unplug, eventthread

