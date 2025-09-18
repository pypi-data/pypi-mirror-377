
class _SubscriptableDefault(object):
    NOT_DETERMINED = '__NOT_DETEMINED__'
    
    def __init__(self, default=None, next_level_default=NOT_DETERMINED, iterable_default=[]):
        self.value = default
        self.__next_level_default = next_level_default
        self.__iterable_default = iterable_default
    
    def __getitem__(self, __key):
        next_level_default_determined = bool(self.__next_level_default != self.NOT_DETERMINED)
        if next_level_default_determined:
            return _SubscriptableDefault(default=self.__next_level_default, iterable_default=self.__iterable_default)
        else:
            return _SubscriptableDefault(default=self.value, iterable_default=self.__iterable_default)
    
    def __is_iterable(self):
        try:
            iter(self.value)
            return True
        except TypeError:
            return False
    
    @property
    def iterable_value(self):
        if self.__is_iterable():
            return self.value
        return self.__iterable_default
    
    @property
    def flexible_value(self):
        return _SubscriptableDefault(default=self.value, iterable_default=self.__iterable_default)
    
    def __str__(self):
        return f'\nType: {type(self)} \nValue: {self.value}\n'


class FlexibleDict(dict):
    
    def __init__(self, input_dict, default=None, iterable_default=[], *args, **kwargs):
        iter(iterable_default)
        dict.__init__(self, *args, **kwargs)
        self.__value = self
        self.__default = default
        self.__iterable_default = iterable_default
        self.__load_dict(input_dict)
    
    
    def __load_dict(self, input_dict):
        is_input_dict = isinstance(input_dict, dict)
        if is_input_dict:
            for key, value in input_dict.items():
                super(FlexibleDict, self).__setitem__(key, value)
        return self
    
    def __setitem__(self, key, value):
        flexible_value = self.__generate_flexible_value(value)
        dict.__setitem__(self, key, flexible_value)
    
    def __getitem__(self, __key):
        if __key not in self.keys():
            self.__value = _SubscriptableDefault(default=self.__default, iterable_default=self.__iterable_default)
        else:
            inline_value = super(FlexibleDict, self).__getitem__(__key)
            self.__value = self.__generate_flexible_value(inline_value)
        return self.__value
    
    def __generate_flexible_value(self, inline_value):
        is_inline_value_dict = isinstance(inline_value, dict)
        is_inline_value_flexible_dict = isinstance(inline_value, FlexibleDict)
        is_inline_value_subscriptable_default = isinstance(inline_value, _SubscriptableDefault)
        
        if is_inline_value_flexible_dict or is_inline_value_subscriptable_default:
            flexible_value = inline_value
        elif is_inline_value_dict:
            flexible_value = FlexibleDict(input_dict=inline_value, default=self.__default, iterable_default=self.__iterable_default)
        else:
            flexible_value = _SubscriptableDefault(default=inline_value, next_level_default=self.__default, iterable_default=self.__iterable_default)
        return flexible_value
    
    def __is_iterable(self):
        try:
            iter(self.__value)
            return True
        except TypeError:
            return False
    
    @property
    def value(self):
        return dict(self.__value)
    
    @property
    def iterable_value(self):
        if self.__is_iterable():
            return dict(self.__value)
        return self.__iterable_default
    
    @property
    def flexible_value(self):
        return self.__value
    
    def __str__(self):
        return f'\nType: {type(self)} \nValue: {dict.__str__(self)}\n'
