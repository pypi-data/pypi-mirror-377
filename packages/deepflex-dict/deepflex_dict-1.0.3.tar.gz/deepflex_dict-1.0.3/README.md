## Usage

When working with deeply nested dictionaries, handling missing keys can be cumbersome. Normally, you would need to catch errors or provide default values when a key does not exist.  

`FlexibleDict`, which is a redefined version of Python’s built-in dictionary, eliminates the need for explicit error handling. You can chain multiple key lookups without worrying about whether each key exists. If a key is missing, a predefined default value is returned instead of raising an error.  

An important feature is that the default value itself is also a `FlexibleDict`, meaning you can continue chaining key lookups without interruptions. Once the entire key chain has been traversed, if a missing key was encountered along the way, the predefined default value will be returned.  

An example of how to use this class can be found in the `how_to_use.py` file included in this package. Below, we explain how to create a `FlexibleDict` object and the available methods for accessing values.

---

## Creating a FlexibleDict

```python
my_flexible_dict = FlexibleDict(input_dict=a_simple_dict, default=..., iterable_default=...)
```

- **`input_dict`**: a regular Python dictionary that will be wrapped by `FlexibleDict`.  
- **`default`**: the value to return whenever a missing key is accessed.  
- **`iterable_default`**: a special default value used when an iterable is expected (explained below).  

---

## Available Methods (Reading Data)

To read nested keys, simply chain them one after another. There are three main ways to retrieve values:

### 1. `.value`
Use `.value` to get the plain Python value.  
- If the keys exist, the actual value is returned.  
- If not, the predefined `default` value is returned.  

> Note: the returned value is always a standard Python type. For example, if it’s a dictionary, it will be a regular `dict`, not a `FlexibleDict`.  

This is the most common way to read values for everyday use.

---

### 2. `.flexible_value`
Use `.flexible_value` if you want the result to remain a `FlexibleDict`, allowing you to continue chaining key lookups even after missing keys.  
- This is useful if you want to traverse further without worrying about whether the intermediate values exist.  

To finally extract a standard Python type, you should still use `.value`.

---

### 3. `.iterable_value`
When iterating with `for` loops, you need to ensure the value is iterable.  
- `.iterable_value` guarantees that behavior.  
- If the result is iterable, it will be returned as is.  
- If not, the predefined `iterable_default` (provided during object creation) will be returned instead.  

This makes error handling easier when iterating over values. For example, you can set `iterable_default` to an empty list `[]`. If the key doesn’t exist or the value is not iterable, the empty list is returned, and the `for` loop simply won’t execute.  


## How To Use
```python
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
```