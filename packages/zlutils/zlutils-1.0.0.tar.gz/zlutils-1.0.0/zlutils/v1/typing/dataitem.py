

class DataItem(dict):
    '''
    sample:
        class IT1(DataItem):
            A = 1  # const
            a = 22  # attribute with default value

        # new
        di = IT1(a=1)  # init attribute
        di.update(a=2)  # update attribute
'''

    __dict_internels = dir(dict())

    def __getattribute__(self, name: str):
        if name.startswith('_') or name in self.__dict_internels:
            return super().__getattribute__(name)
        # print(f'get {name}')
        return self.get(name, super().__getattribute__(name))

    def __setattr__(self, name: str , value: any):
        if not hasattr(self, name):
            raise AttributeError(f'can not  new attribute, {name}')
        elif name.isupper():
            raise AttributeError(f'can not  set const, {name}')
        elif name in self.__dict_internels:
            raise AttributeError(f'can not  set internel method, {name}')
        else:
            if super().__getattribute__(name) is not None and type(value) != type(super().__getattribute__(name)):
                 raise AttributeError(f'attribute type not match , {type(super().__getattribute__(name))} -> {type(value)}')
            self.__setitem__(name, value)
