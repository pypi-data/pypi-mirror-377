from unittest import TestCase
import unittest

from flexible_dict import FlexibleDict, _SubscriptableDefault


INITIAL_DICT = {'a': 'a',
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


class FlexibleDictBehaviourTestCase(TestCase):
    MY_NONE = '__MY_NONE__'
    MY_ITERABLE_DEFAULT = '__MY_ITERABLE_DEFAULT__'
    
    def setUp(self):
        self.flexible_dict = FlexibleDict(input_dict=INITIAL_DICT,
                                          default=self.MY_NONE,
                                          iterable_default=self.MY_ITERABLE_DEFAULT)
    
    def tearDown(self):
        pass
    
    def test_simple_access_level_1(self):
        self.assertEqual(self.flexible_dict['a'].value, 'a')
        self.assertEqual(self.flexible_dict['b'].value, 'b')
        self.assertEqual(self.flexible_dict['c'].value, 30)
    
    def test_simple_access_level_2(self):
        self.assertEqual(self.flexible_dict['cdefg']['c'].value, 'c')
    
    def test_simple_access_level_3(self):
        self.assertEqual(self.flexible_dict['cdefg']['defg']['d'].value, 'd')
        self.assertEqual(self.flexible_dict['cdefg']['defg']['efg'].value, {'e': 'e', 'fg': {'f': 'f', 'g': 'g'}})
    
    def test_simple_access_level_4(self):
        self.assertEqual(self.flexible_dict['cdefg']['defg']['efg']['e'].value, 'e')
        self.assertEqual(self.flexible_dict['cdefg']['defg']['efg']['fg'].value, {'f': 'f', 'g': 'g'})
    
    def test_simple_access_level_5(self):
        self.assertEqual(self.flexible_dict['cdefg']['defg']['efg']['fg']['f'].value, 'f')
    
    def test_interable_access_level_1(self):
        self.assertEqual(self.flexible_dict['cdefg'].iterable_value, INITIAL_DICT['cdefg'])
        self.assertNotEqual(self.flexible_dict['c'].iterable_value, INITIAL_DICT['c'])
        self.assertEqual(self.flexible_dict['c'].iterable_value, self.MY_ITERABLE_DEFAULT)
    
    def test_iterable_value_returns_iterable_default(self):
        value = self.flexible_dict['cdefg']['defg']['efg']['fg']['f']['ttt'].iterable_value
        self.assertEqual(value, self.MY_NONE)
        value = self.flexible_dict['cdefg']['defg']['ttt'].iterable_value
        self.assertEqual(value, self.MY_NONE)
        value = self.flexible_dict['c'].iterable_value
        self.assertEqual(value, self.MY_ITERABLE_DEFAULT)
    
    def test_flexible_value_level_1(self):
        self.assertEqual(self.flexible_dict['a'].flexible_value.value, 'a')
        self.assertEqual(self.flexible_dict['c'].flexible_value.value, 30)
    
    def test_flexible_value_level_more(self):
        self.assertEqual(self.flexible_dict['cdefg']['c'].flexible_value.value, 'c')
        self.assertEqual(self.flexible_dict['cdefg']['defg']['d'].flexible_value.value, 'd')
        self.assertEqual(self.flexible_dict['cdefg']['defg']['efg']['fg']['f'].flexible_value.value, 'f')
    
    def test_flexible_value_type_level_more_than_exists(self):
        self.assertEqual(self.flexible_dict['cdefg']['defg']['efg']['fg']['f']['tt'].flexible_value.value, self.MY_NONE)
    
    def test_flexible_value_chained(self):
        self.assertEqual(self.flexible_dict['cdefg'].flexible_value.value, INITIAL_DICT['cdefg'])
        self.assertEqual(self.flexible_dict['cdefg'].flexible_value.flexible_value.value, INITIAL_DICT['cdefg'])
        self.assertEqual(self.flexible_dict['cdefg'].flexible_value.flexible_value.flexible_value.value, INITIAL_DICT['cdefg'])
        
        self.assertEqual(self.flexible_dict['cdefg']['c'].flexible_value.value, 'c')
        self.assertEqual(self.flexible_dict['cdefg']['c'].flexible_value.flexible_value.value, 'c')
        self.assertEqual(self.flexible_dict['cdefg']['c'].flexible_value.flexible_value.flexible_value.value, 'c')
    
    def test_flexible_value_chained_iterable_value(self):
        self.assertEqual(self.flexible_dict['cdefg'].flexible_value.iterable_value, INITIAL_DICT['cdefg'])
        self.assertEqual(self.flexible_dict['cdefg'].flexible_value.flexible_value.iterable_value, INITIAL_DICT['cdefg'])
        self.assertEqual(self.flexible_dict['cdefg'].flexible_value.flexible_value.flexible_value.iterable_value, INITIAL_DICT['cdefg'])
        
        self.assertEqual(self.flexible_dict['c'].flexible_value.flexible_value.flexible_value.iterable_value, self.MY_ITERABLE_DEFAULT)
        
        self.assertEqual(self.flexible_dict['cdefg']['c'].flexible_value.iterable_value, 'c')
        self.assertEqual(self.flexible_dict['cdefg']['c'].flexible_value.flexible_value.iterable_value, 'c')
        self.assertEqual(self.flexible_dict['cdefg']['c'].flexible_value.flexible_value.flexible_value.iterable_value, 'c')
    
    def test_not_exists_access_level_1(self):
        self.assertEqual(self.flexible_dict['d'].value, self.MY_NONE)
    
    def test_not_exists_access_level_2(self):
        self.assertEqual(self.flexible_dict['b']['c'].value, self.MY_NONE)
    
    def test_not_exists_access_level_3(self):
        self.assertEqual(self.flexible_dict['b']['c']['k'].value, self.MY_NONE)
        self.assertEqual(self.flexible_dict['cdefg']['defg']['kk'].value, self.MY_NONE)
    
    def test_not_exists_access_level_4(self):
        self.assertEqual(self.flexible_dict['cdefg']['defg']['kk']['hh'].value, self.MY_NONE)
        
    def test_not_exists_access_level_5(self):
        self.assertEqual(self.flexible_dict['cdefg']['defg']['efg']['fg']['k'].value, self.MY_NONE)
        
    def test_not_exists_access_level_6(self):
        self.assertEqual(self.flexible_dict['cdefg']['defg']['efg']['fg']['g']['k'].value, self.MY_NONE)


class FlexibleDictStructureTestCase(TestCase):
    MY_NONE = '__MY_NONE__'
    MY_ITERABLE_DEFAULT = '__MY_ITERABLE_DEFAULT__'
    
    def setUp(self):
        self.flexible_dict = FlexibleDict(input_dict=INITIAL_DICT,
                                          default=self.MY_NONE,
                                          iterable_default=self.MY_ITERABLE_DEFAULT)
    
    def tearDown(self):
        pass
    
    def test_final_value_type(self):
        self.assertIsInstance(self.flexible_dict['a'].value, str)
        self.assertIsInstance(self.flexible_dict['a'].flexible_value.value, str)
        self.assertIsInstance(self.flexible_dict['cdefg'].value, dict)
        self.assertIsInstance(self.flexible_dict['cdefg'].flexible_value.value, dict)
    
    def test_inner_value_is_flexible(self):
        self.assertIsInstance(self.flexible_dict['cdefg']['defg'], FlexibleDict)
        self.assertIsInstance(self.flexible_dict['cdefg']['c'], _SubscriptableDefault)
    
    def test_inner_value_is_not_flexible_after_dotvalue(self):
        self.assertNotIsInstance(self.flexible_dict['cdefg'].value['defg'], FlexibleDict)
        self.assertNotIsInstance(self.flexible_dict['cdefg'].value['c'], _SubscriptableDefault)
    
    def test_flexible_value_type(self):
        self.assertIsInstance(self.flexible_dict['a'].flexible_value, _SubscriptableDefault)
        self.assertIsInstance(self.flexible_dict['cdefg'].flexible_value, FlexibleDict)
    
    def test_iterable_value_type_level_1(self):
        self.assertIsInstance(self.flexible_dict['cdefg'].iterable_value, dict)
        self.assertNotIsInstance(self.flexible_dict['cdefg'].iterable_value, FlexibleDict)
    
    def test_iterable_value_type_level_2(self):
        self.assertIsInstance(self.flexible_dict['cdefg']['defg'], dict)
        self.assertNotIsInstance(self.flexible_dict['cdefg']['defg'].iterable_value, FlexibleDict)
        self.assertIsInstance(self.flexible_dict['cdefg']['c'].iterable_value, str)
    
    def test_flexible_value_type_level_1(self):
        self.assertIsInstance(self.flexible_dict['a'].flexible_value, _SubscriptableDefault)
        self.assertIsInstance(self.flexible_dict['c'].flexible_value, _SubscriptableDefault)
        self.assertNotIsInstance(self.flexible_dict['a'].flexible_value, str)
        self.assertNotIsInstance(self.flexible_dict['c'].flexible_value, int)
        
        self.assertIsInstance(self.flexible_dict['cdefg'].flexible_value, dict)
        self.assertIsInstance(self.flexible_dict['cdefg'].flexible_value, FlexibleDict)
    
    def test_flexible_value_type_level_mpre(self):
        self.assertIsInstance(self.flexible_dict['cdefg']['c'].flexible_value, _SubscriptableDefault)
        self.assertIsInstance(self.flexible_dict['cdefg']['defg']['d'].flexible_value, _SubscriptableDefault)
        self.assertIsInstance(self.flexible_dict['cdefg']['defg']['efg']['fg']['f'].flexible_value, _SubscriptableDefault)
    
    def test_flexible_value_type_level_more_than_exists(self):
        self.assertIsInstance(self.flexible_dict['cdefg']['defg']['efg']['fg']['f']['tt'].flexible_value, _SubscriptableDefault)
    
    def test_flexible_value_type_chained(self):
        self.assertIsInstance(self.flexible_dict['cdefg'].flexible_value, FlexibleDict)
        self.assertIsInstance(self.flexible_dict['cdefg'].flexible_value.flexible_value, FlexibleDict)
        self.assertIsInstance(self.flexible_dict['cdefg'].flexible_value.flexible_value.flexible_value, FlexibleDict)
        
        self.assertIsInstance(self.flexible_dict['cdefg']['c'].flexible_value, _SubscriptableDefault)
        self.assertIsInstance(self.flexible_dict['cdefg']['c'].flexible_value.flexible_value, _SubscriptableDefault)
        self.assertIsInstance(self.flexible_dict['cdefg']['c'].flexible_value.flexible_value.flexible_value, _SubscriptableDefault)
    
    def test_flexible_value_chained_iterable_value_type(self):
        self.assertIsInstance(self.flexible_dict['cdefg'].flexible_value.iterable_value, dict)
        self.assertNotIsInstance(self.flexible_dict['cdefg'].flexible_value.iterable_value, FlexibleDict)
        self.assertIsInstance(self.flexible_dict['cdefg'].flexible_value.flexible_value.iterable_value, dict)
        self.assertNotIsInstance(self.flexible_dict['cdefg'].flexible_value.flexible_value.iterable_value, FlexibleDict)
        self.assertIsInstance(self.flexible_dict['cdefg'].flexible_value.flexible_value.flexible_value.iterable_value, dict)
        self.assertNotIsInstance(self.flexible_dict['cdefg'].flexible_value.flexible_value.flexible_value.iterable_value, FlexibleDict)
        
        self.assertIsInstance(self.flexible_dict['c'].flexible_value.flexible_value.flexible_value.iterable_value, type(self.MY_ITERABLE_DEFAULT))
        
        self.assertIsInstance(self.flexible_dict['cdefg']['c'].flexible_value.iterable_value, str)
        self.assertIsInstance(self.flexible_dict['cdefg']['c'].flexible_value.flexible_value.iterable_value, str)
        self.assertIsInstance(self.flexible_dict['cdefg']['c'].flexible_value.flexible_value.flexible_value.iterable_value, str)
    
    def test_chained_flexible_value_type(self):
        self.assertIsInstance(self.flexible_dict['a'].flexible_value.flexible_value, _SubscriptableDefault)
        self.assertIsInstance(self.flexible_dict['cdefg'].flexible_value.flexible_value, FlexibleDict)
    
    def test_flexible_value_chain(self):
        level_1 = self.flexible_dict['a'].flexible_value
        level_2 = level_1.flexible_value
        level_3 = level_2.flexible_value
        self.assertEqual(level_1.__dict__, level_2.__dict__)
        self.assertEqual(level_2.__dict__, level_3.__dict__)
        self.assertNotEqual(level_1, level_2)
        self.assertNotEqual(level_2, level_3)
        self.assertEqual(level_1.value, 'a')
        self.assertEqual(level_2.value, 'a')
        self.assertEqual(level_3.value, 'a')
    
    def test_flexible_value_not_changes_the_final_value(self):
        final_value = self.flexible_dict['a'].value
        final_value_with_flexible_in_middle = self.flexible_dict['a'].flexible_value.value
        self.assertEqual(final_value, final_value_with_flexible_in_middle)
    
    def test_final_value_type_after_setitem(self):
        self.flexible_dict['cdefg'] = {'f': 'f_val', 'g': 'g_val'}
        self.assertIsInstance(self.flexible_dict['cdefg'], dict)
        self.assertIsInstance(self.flexible_dict['cdefg'], FlexibleDict)
        
        self.assertIsInstance(self.flexible_dict['cdefg'].value, dict)
        self.assertNotIsInstance(self.flexible_dict['cdefg'].value, FlexibleDict)
        self.assertNotIsInstance(self.flexible_dict['cdefg'].value, _SubscriptableDefault)
        
        self.assertIsInstance(self.flexible_dict['cdefg'].flexible_value.value, dict)
        self.assertNotIsInstance(self.flexible_dict['cdefg'].flexible_value.value, FlexibleDict)
        self.assertNotIsInstance(self.flexible_dict['cdefg'].flexible_value.value, _SubscriptableDefault)
        
        self.assertIsInstance(self.flexible_dict['cdefg']['f'], _SubscriptableDefault)
        self.assertIsInstance(self.flexible_dict['cdefg']['f'].value, str)
        self.assertNotIsInstance(self.flexible_dict['cdefg']['f'].value, _SubscriptableDefault)
        self.assertIsInstance(self.flexible_dict['cdefg']['f'].flexible_value.value, str)
    
    def test_flexible_value_type_after_setitem(self):
        self.flexible_dict['cdefg'] = {'f': 'f_val', 'g': 'g_val'}
        self.assertIsInstance(self.flexible_dict['cdefg'].flexible_value, FlexibleDict)
        self.assertIsInstance(self.flexible_dict['cdefg']['f'].flexible_value, _SubscriptableDefault)
        self.assertIsInstance(self.flexible_dict['cdefg']['f']['n'].flexible_value, _SubscriptableDefault)
    
    def test_item_setted_after_setitem_level_1(self):
        item = {'f': 'f_val', 'g': 'g_val'}
        self.flexible_dict['cdefg'] = item
        self.assertEqual(self.flexible_dict['cdefg'].value, item)
        self.assertEqual(self.flexible_dict['cdefg'].flexible_value.value, item)
        self.assertEqual(self.flexible_dict['cdefg']['g'].value, 'g_val')
    
    def test_item_setted_after_setitem_level_2(self):
        item = {'f': 'f_val', 'g': 'g_val'}
        self.flexible_dict['cdefg'] = item
        self.flexible_dict['cdefg']['f'] = 'new'
        self.assertIsInstance(self.flexible_dict['cdefg']['f'], _SubscriptableDefault)
        self.assertEqual(self.flexible_dict['cdefg']['f'].value, 'new')
        self.assertEqual(self.flexible_dict['cdefg']['f'].flexible_value.value, 'new')
        self.assertEqual(self.flexible_dict['cdefg']['g'].value, 'g_val')
    
    def test_flexible_relation_disconnection_after_call_dotvalue(self):
        self.flexible_dict['cdefg'] = {'f': 'f_val', 'g': 'g_val'}
        self.flexible_dict['cdefg'].value['f'] = 'new'
        self.assertNotEqual(self.flexible_dict['cdefg']['f'].value, 'new')
        self.assertEqual(self.flexible_dict['cdefg']['f'].value, 'f_val')
        self.assertEqual(self.flexible_dict['cdefg']['g'].value, 'g_val')


if __name__=='__main__':
    unittest.main()
