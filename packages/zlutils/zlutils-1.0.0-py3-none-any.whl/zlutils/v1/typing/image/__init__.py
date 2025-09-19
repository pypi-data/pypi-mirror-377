import cv2
import numpy as np
# from PIL.Image import Image as PILImageType
from PIL import Image as PILImage

from functools import cache
import io
import requests
from os import PathLike
import typing
import threading
import time
from . import imghdr


NORM_SIZE = (224, 224)

def imageBlobType(blob):
    return imghdr.what(None, blob)


def autoType(source):
    if isinstance(source, typing.ByteString):
        return imageBlobType(source)
    elif isinstance(source, PILImage.Image):
        return 'image'
    elif isinstance(source, np.ndarray):
        return 'bgrmat'
    elif isinstance(source, str):
        if source.startswith('http://') or source.startswith('https://') or source.startswith('ftp://'):
            return 'url'
        return 'file_path'
    raise RuntimeError(f'[error] undef source_type: {type(source)}')
    return None
    pass


def getDefaultImagePath():
    import os
    fdir = os.path.dirname(__file__)
    return os.path.join(fdir, 'no_image.jpg')


class _Image:
    '''
source_type: bgrmat, image(pil), png, jpeg, file_path, url
'''
    # TODO 移除@cache 管理缓存
    # conditions: new_image

    _ZLIMAGE1_=None

    def __init__(self, source=None, source_type=None, size_limit=0):
        self.source = None
        self.source_type = None
        self._cache = {}
        self._create_time = time.time()
        self.size_limit = size_limit
        self._conditions = {}
        # self.condition_new = threading.Condition()
        self._meta = {}
        if source is None:
            source = getDefaultImagePath()
        self.setImage(source, source_type)

    def getCondition(self, name):
        if name not in self._conditions:
            self._conditions[name] = threading.Condition()
        return self._conditions[name]

    def clear(self):
        # 清除缓存
        for key in dir(self):
            if not key.startswith('_') or key.startswith('__'):
                continue
            func = getattr(self, key)
            if hasattr(func, 'cache_clear'):
                func.cache_clear()
        return self

    def _repr_jpeg_(self):
        return self.image._repr_jpeg_()

    def resize(self, size, resample=0):
        return _Image(self.image.resize(size, resample=0))

    def setImage(self, source, source_type=None):
        # print('setimage. ')
        if source is None:
            source = getDefaultImagePath()
            # return False
        if id(source) == id(self.source):
            return False
        while hasattr(source, 'source'):  # TODO
            if id(self.source) == id(source.source):
                return False
            source = source.source
        # print(type(source))
        if isinstance(source, str):
            source = source.strip()

        self.source_type = autoType(source) if source_type is None else source_type
        self.source = source

        self.clear()
        if 'new_image' in self._conditions:
            with self._conditions['new_image']:
                self._conditions['new_image'].notify_all()
        # print(self.conditions)
        return True

    @property
    def size(self):
        return self.image.size

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    @property
    def image(self):
        return self._image()

    @cache
    def _image(self):
        if self.source_type in ['image', 'pil']:
            img = self.source
        elif self.source_type in ['png', 'jpg', 'jpeg']:
            fp = io.BytesIO(self.source)
            img = PILImage.open(fp)
            # with io.BytesIO(self.source) as fp:
            #    img = PILImage.open(fp)
        elif self.source_type == 'bgrmat':
            rgbmat = cv2.cvtColor(self.source, cv2.COLOR_BGR2RGB)
            img = PILImage.fromarray(rgbmat, mode="RGB")
        elif self.source_type == 'file_path':
            img = PILImage.open(self.source)
        elif self.source_type == 'url':
            response = requests.get(self.source)
            if response.status_code == 200:
                # 将二进制数据转换为BytesIO对象
                image_bytes = io.BytesIO(response.content)
                # 使用PIL打开图片
                img = PILImage.open(image_bytes)
            else:
                raise Exception(f"unable to download image：{response.status_code}")
        else:
            raise RuntimeError(f'[error] undef source_type: {self.source_type}')
        if self.size_limit > 0:
            osize = img.size[0]*img.size[1]
            if osize > self.size_limit:
                r = (self.size_limit / osize) ** 0.5
                newsize = (int(img.size[0]*r), int(img.size[1]*r))
                img = img.resize(newsize)
        return img

    @property
    def png(self):
        return self._png()

    @cache
    def _png(self):
        if self.source_type == 'png':
            return self.source
        img_byte_arr = io.BytesIO()
        self.image.save(img_byte_arr, format='PNG')
        return img_byte_arr.getvalue()

    @property
    def jpeg(self):
        return self._jpeg()

    @cache
    def _jpeg(self):
        if self.source_type == 'jpeg':
            return self.source
        img_byte_arr = io.BytesIO()
        if self.image.mode == 'RGBA':
            self.image.convert('RGB').save(img_byte_arr, format='JPEG')
        else:
            self.image.save(img_byte_arr, format='JPEG')
        return img_byte_arr.getvalue()

    @cache
    def _cvthumbnail(self, size=NORM_SIZE):
        # 生成一个对应尺寸的快照
        if self.source_type == 'bgrmat':
            resize_flag = False
            if size[0] < NORM_SIZE[0] or size[1] < NORM_SIZE[1]:
                resize_flag = True
            imat = self.source
            th, tw = max(size[0], NORM_SIZE[0]), max(size[1], NORM_SIZE[1])
            rx, ry = int(imat.shape[1]/size[0]), int(imat.shape[0] / size[1])
            ox, oy = int((imat.shape[1] - rx*size[0])/2), int((imat.shape[0] - ry*size[1])/2)
            timat = imat[oy::ry, ox::rx]
            if resize_flag:
                return cv2.resize(timat, size, interpolation=cv2.INTER_AREA)
            else:
                return timat
            # return cv2.resize(self.source, size, interpolation=0)
        return np.array(self.image.resize(size, resample=0))

    @property
    def bgrmat(self):
        return self._bgrmat()

    @cache
    def _bgrmat(self):
        if self.source_type == 'bgrmat':
            return self.source
        np.array(self.image)

    def __eq__(self, o):
        return id(self.source) == id(o.source)

    def __hash__(self):
        return hash(str(id(self.source)))


def Image(source=getDefaultImagePath(), source_type=None, size_limit=0):

    if isinstance(source, _Image):
        source.size_limit = size_limit
        return source
    return _Image(source, source_type, size_limit=size_limit)

