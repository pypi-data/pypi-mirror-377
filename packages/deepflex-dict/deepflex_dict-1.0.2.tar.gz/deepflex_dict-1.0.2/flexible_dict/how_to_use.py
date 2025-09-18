from flexible_dict import FlexibleDict


a = {'a': 'a',
     'c': 30,
     'b': 'b',
     'cdefg': {
         'c': 'c',
         'defg': {
             'd': 'd',
             'efg':{
                 'e': 'e',
                 'fg': {'f': 'f', 'g': 'g'}
                }
             }
         },
     }

b = FlexibleDict(input_dict=a, default='__MY_NONE__', iterable_default='__MY_ITERABLE_DEFAULT__')
print(b['a'].value == 'a')
print(b['b'].value == 'b')
print(b['cdefg']['c'].value == 'c')
print(b['b']['c'].value == '__MY_NONE__')
print(b['b']['c']['k'].value == '__MY_NONE__')
print(b['cdefg']['defg']['d'].value == 'd')
print(b['cdefg']['defg']['kk'].value == '__MY_NONE__')
print(b['cdefg']['defg']['efg'].value == {'e': 'e', 'fg': {'f': 'f', 'g': 'g'}})
print(b['cdefg']['defg']['efg']['e'].value == 'e')
print(b['cdefg']['defg']['efg']['fg'].value == {'f': 'f', 'g': 'g'})
print(b['cdefg']['defg']['efg']['fg']['k'].value == '__MY_NONE__')
print(b['cdefg']['defg']['efg']['fg']['f'].value == 'f')
print(b['cdefg']['defg']['efg']['fg']['g']['k'].value == '__MY_NONE__')
print(b['a'].value)
print(b['a'].flexible_value)
print(b['a'].flexible_value.value)
print(b['cdefg'].flexible_value)
print(type(b['cdefg'].flexible_value))
print(b['cdefg'].flexible_value.value)
print(type(b['cdefg'].flexible_value.value))
print(b['cdefg'].value)
print(type(b['cdefg'].value))


print(b['cdefg'])
b['cdefg'] = {'f': 'f', 'g': 'g'}
print(b['cdefg'])

print(b['cdefg'].value)
print(type(b['cdefg'].value))
print(b['a'].iterable_value)
print(b['c'].iterable_value)
b['cdefg'].value['f'] = 'new'
print(b['cdefg']['f'].value)
b['cdefg']['f'].value = 'new'
print(b['cdefg']['f'].value)

b['cdefg']['f'] = 'new'
print(b['cdefg']['f'])
print(b['cdefg']['f'].value)
