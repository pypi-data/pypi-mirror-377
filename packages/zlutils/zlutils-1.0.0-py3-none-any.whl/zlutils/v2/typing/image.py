import time
from PIL import Image as PILImage
import cv2
import numpy as np
import io
import requests
import threading


NORM_SIZE = (224, 224)

# ----------------------------------------
def file_path2pilimage(p):
    return PILImage.open(p)


def pilimage2bgrmat(img):
    return np.array(img)


def bgrmat2pilimage(imat):
    rgbmat = cv2.cvtColor(imat, cv2.COLOR_BGR2RGB)
    return PILImage.fromarray(rgbmat, mode="RGB")


def png2pilimage(b):
    fp = io.BytesIO(b)
    return PILImage.open(fp)


def jpeg2pilimage(b):
    fp = io.BytesIO(b)
    return PILImage.open(fp)


def url2pilimage(url):
    response = requests.get(url)
    if response.status_code == 200:
        # 将二进制数据转换为BytesIO对象
        image_bytes = io.BytesIO(response.content)
        # 使用PIL打开图片
        return PILImage.open(image_bytes)
    else:
        raise Exception(f"unable to download image：{response.status_code}")


def pilimage2png(img):
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='PNG')
    return img_byte_arr.getvalue()


def pilimage2jpeg(img):
    img_byte_arr = io.BytesIO()
    if img.mode == 'RGBA':
        img.convert('RGB').save(img_byte_arr, format='JPEG')
    else:
        img.save(img_byte_arr, format='JPEG')
    return img_byte_arr.getvalue()



# ----------------------------------------
class _autoproperty:

    def __init__(self, imtype):
        self.imtype = imtype
    # 转换函数命名例如： pilimage2bgrmat
    namespace = globals()

    def trans(self, imageobj, target_type=None, source_type_blocks=[]):
        # 确定转换源优先级
        imtype = self.imtype
        namespace = self.namespace
        if target_type is None:
            target_type = imtype.__name__
        source_order = imtype(imageobj)
        if source_order is None:
            source_order = imageobj._source_order

        directs = [source_type for source_type in source_order if source_type in imageobj._cache]
        directs += list(set(imageobj._cache.keys()) - set(directs))

        for source_type in directs:
            func_name = f'{source_type}2{target_type}'
            if func_name in namespace:
                func = namespace[func_name]
                imageobj._cache[target_type] = func(imageobj._cache[source_type])
                return True

        transits = [source_type for source_type in source_order if source_type not in imageobj._cache]
        alltypes = [source_type for source_type in dir(imageobj) if (not source_type.startswith('_')) and (source_type not in ['setImage', 'getCondition', 'size', 'width', 'height', 'resize'])]
        transits += list(set(alltypes) - set(transits) - set(source_type_blocks))

        source_type_blocks_new = source_type_blocks+transits
        for source_type in transits:
            if source_type == target_type:
                continue
            func_name = f'{source_type}2{target_type}'
            if func_name in namespace and self.trans(imageobj,
                     target_type=source_type,
                     source_type_blocks=source_type_blocks_new
                     ):

                func = namespace[func_name]
                imageobj._cache[target_type] = func(imageobj._cache[source_type])
                return True
        return False

    def auto(self, imageobj):
        imtype = self.imtype
        if imtype.__name__ in imageobj._cache or self.trans(imageobj, imtype.__name__):
            return imageobj._cache[imtype.__name__]
        raise RuntimeError(f'无法转换到类型{imtype.__name__}， 数据源类型：{imageobj._source_type}')
        return None

    def __get__(self, obj, owner):
        if obj is None:
            return self
        if self.imtype is None:
            raise AttributeError('_autoproperty只能作为zlimage中的装饰器使用')
        return self.auto(obj)


def getDefaultImagePath():
    import os
    fdir = os.path.dirname(__file__)
    return os.path.join(fdir, 'no_image.jpg')

def autoType(source):
    import typing
    from ...v1.typing.image import imghdr  # TODO remove v1 dependance
    if isinstance(source, typing.ByteString):
        return imghdr.what(None, source)
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


class ZLImage:
    _ZLIMAGE2_=None
    _source_order = []
    def __init__(self, source=None, source_type=None, size_limit=0):
        self._cache = None
        self._source_type = None
        self._create_time = time.time()
        # self._size_limit = size_limit  # TODO
        self._conditions = {}
        self.setImage(source, source_type)

    def getCondition(self, name):
        if name not in self._conditions:
            self._conditions[name] = threading.Condition()
        return self._conditions[name]

    def _publishCondition(self, name):
        if name in self._conditions:
            with self._conditions[name]:
                self._conditions[name].notify_all()

    def setImage(self, source, source_type=None):
        if source is None:
            source = getDefaultImagePath()
            # return False
        if self._cache is not None and id(source) == id(self._cache[self._source_type]):
            return False
        if hasattr(source, '_ZLIMAGE2_'):
            if id(source._cache) == id(self._cache):
                return False
            self._source_type = source._source_type
            self._cache = source._cache
            self._publishCondition('new_image')
            return True

        if hasattr(source, '_ZLIMAGE1_'):
            self._source_type = source.source_type
            self._cache = {self._source_type: source.source}
            self._publishCondition('new_image')
            return True

        if isinstance(source, str):
            source = source.strip()
        self._source_type = autoType(source) if source_type is None else source_type
        self._cache = {self._source_type: source}
        self._publishCondition('new_image')
        return True

    def __eq__(self, o):
        return id(self.source) == id(o.source)

    def __hash__(self):
        return hash(str(id(self.source)))

    def __contains__(self, item):
        return item in self._cache

    @_autoproperty
    def file_path(self): pass

    @_autoproperty
    def pilimage(self): pass

    @_autoproperty
    def bgrmat(self): pass

    @_autoproperty
    def png(self): pass

    @_autoproperty
    def jpeg(self): pass

    @property
    def image(self): return self.pilimage

    @property
    def size(self):
        return self.pilimage.size

    @property
    def width(self):
        return self.size[0]

    @property
    def height(self):
        return self.size[1]

    def _repr_jpeg_(self):
        return self.pilimage._repr_jpeg_()

    def resize(self, size, resample=0):
        return ZLImage(self.pilimage.resize(size, resample=0), 'pilimage')

    # external
    def _cvthumbnail(self, size=NORM_SIZE):
        # 生成一个对应尺寸的快照
        size = tuple(size)
        if '_cvthumbnail' not in self:
            self._cache['_cvthumbnail'] = {}
        cache = self._cache['_cvthumbnail']
        if size in cache:
            return cache[size]
        if 'bgrmat' in self:
            resize_flag = False
            if size[0] < NORM_SIZE[0] or size[1] < NORM_SIZE[1]:
                resize_flag = True
            imat = self.bgrmat
            th, tw = max(size[0], NORM_SIZE[0]), max(size[1], NORM_SIZE[1])
            rx, ry = int(imat.shape[1]/size[0]), int(imat.shape[0] / size[1])
            ox, oy = int((imat.shape[1] - rx*size[0])/2), int((imat.shape[0] - ry*size[1])/2)
            timat = imat[oy::ry, ox::rx]
            if resize_flag:
                ret = cv2.resize(timat, size, interpolation=cv2.INTER_AREA)
            else:
                ret = timat
            cache[size] = ret
            return ret
            # return cv2.resize(self.source, size, interpolation=0)
        ret = np.array(self.pilimage.resize(size, resample=0))
        cache[size] = ret
        return ret


Image = ZLImage
