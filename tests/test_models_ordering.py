"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest


from verbacratis.models import GenericLogger
from verbacratis.models.ordering import Item, Items, get_ordered_item_list_for_named_scope


class Dummy:

    def __init__(self, val: str=None):
        self.val = val


class TestItem(unittest.TestCase):    # pragma: no cover

    def test_item_with_defaults(self):
        result = Item(name='item1')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Item)
        self.assertTrue('default' in result.scopes)
        self.assertIsInstance(result.logger, GenericLogger)

    def test_item_add_scope_with_default_scope(self):
        result = Item(name='item1')
        result.add_scope(scope_name='scope1', replace_default_if_exists=False)
        self.assertEqual(len(result.scopes), 2)
        self.assertTrue('default' in result.scopes)
        self.assertTrue('scope1' in result.scopes)

    def test_item_add_scope_with_no_default_scope(self):
        result = Item(name='item1')
        result.add_scope(scope_name='scope1')
        self.assertEqual(len(result.scopes), 1)
        self.assertFalse('default' in result.scopes)
        self.assertTrue('scope1' in result.scopes)


class TestItems(unittest.TestCase):    # pragma: no cover

    def test_items_with_defaults(self):
        result = Items()
        result.add_item(item=Item(name='item1'))
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Items)
        self.assertTrue('item1' in result.items)
        self.assertEqual(len(result.items), 1)

    def test_items_add_scope_to_item_with_default_scope(self):
        result = Items()
        result.add_item(item=Item(name='item1'))
        result.add_item_scope(item_name='item1', scope_name='scope1', replace_default_if_exists=False)
        self.assertEqual(len(result.items['item1'].scopes), 2)
        self.assertTrue('default' in result.items['item1'].scopes)
        self.assertTrue('scope1' in result.items['item1'].scopes)

    def test_items_add_item_scope_with_no_default_scope(self):
        result = Items()
        result.add_item(item=Item(name='item1'))
        result.add_item_scope(item_name='item1', scope_name='scope1')
        self.assertEqual(len(result.items['item1'].scopes), 1)
        self.assertFalse('default' in result.items['item1'].scopes)
        self.assertTrue('scope1' in result.items['item1'].scopes)

    def test_items_add_parent(self):
        result = Items()
        result.add_item(item=Item(name='item1'))
        result.add_item(item=Item(name='item2'))
        result.add_item_scope(item_name='item1', scope_name='scope1')
        result.add_item_scope(item_name='item2', scope_name='scope1')
        result.add_link_to_parent_item(parent_item_name='item2', sibling_item_name='item1')
        self.assertEqual(len(result.items['item1'].parent_item_names), 1)
        self.assertEqual(result.items['item1'].parent_item_names[0], 'item2')

    def test_items_add_link_to_parent_item_parent_item_not_found(self):
        items = Items()
        items.add_item(item=Item(name='item1'))
        items.add_item(item=Item(name='item2'))
        items.add_item_scope(item_name='item1', scope_name='scope1')
        items.add_item_scope(item_name='item2', scope_name='scope1')
        items.add_link_to_parent_item(parent_item_name='item2', sibling_item_name='item1')
        with self.assertRaises(Exception) as context:
            items.add_link_to_parent_item(parent_item_name='item3', sibling_item_name='item1')
        self.assertTrue('No item named' in str(context.exception), 'Expected not to find item3 in {}'.format(items.items))

    def test_items_add_link_to_parent_item_sibling_item_not_found(self):
        items = Items()
        items.add_item(item=Item(name='item1'))
        items.add_item(item=Item(name='item2'))
        items.add_item_scope(item_name='item1', scope_name='scope1')
        items.add_item_scope(item_name='item2', scope_name='scope1')
        items.add_link_to_parent_item(parent_item_name='item2', sibling_item_name='item1')
        with self.assertRaises(Exception) as context:
            items.add_link_to_parent_item(parent_item_name='item2', sibling_item_name='item3')
        self.assertTrue('No item named' in str(context.exception), 'Expected not to find item3 in {}'.format(items.items))

    def test_items_add_link_to_with_no_scoped_matching(self):
        items = Items()
        items.add_item(item=Item(name='item1'))
        items.add_item(item=Item(name='item2'))
        items.add_item_scope(item_name='item1', scope_name='scope1')
        items.add_item_scope(item_name='item2', scope_name='scope2')
        with self.assertRaises(Exception) as context:
            items.add_link_to_parent_item(parent_item_name='item2', sibling_item_name='item1')
        self.assertTrue('At least one scope name must be present in both parent and sibling' in str(context.exception))

    def test_items_get_item_by_name_raises_exception_when_searching_for_item_not_in_list_of_items(self):
        items = Items()
        items.add_item(item=Item(name='item1'))
        items.add_item(item=Item(name='item2'))
        items.add_item_scope(item_name='item1', scope_name='scope1')
        items.add_item_scope(item_name='item2', scope_name='scope2')
        with self.assertRaises(Exception) as context:
            items.get_item_by_name(name='item3')
        self.assertTrue('Item named "item3" not found' in str(context.exception))


class TestFunctionGetOrderedItemListForNamedScope(unittest.TestCase):    # pragma: no cover

    def test_basic(self):
        items = Items()
        items.add_item(item=Item(name='item1'))
        items.add_item(item=Item(name='item2'))
        items.add_item_scope(item_name='item1', scope_name='scope1')
        items.add_item_scope(item_name='item2', scope_name='scope1')
        items.add_link_to_parent_item(parent_item_name='item2', sibling_item_name='item1')
        result = get_ordered_item_list_for_named_scope(items=items, scope_name='scope1', start_item=items.get_item_by_name(name='item1'))
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertTrue('item1' in result)
        self.assertTrue('item2' in result)
        self.assertEqual(result[0], 'item2')
        self.assertEqual(result[1], 'item1')

    def test_handle_circular_references(self):
        items = Items()
        items.add_item(item=Item(name='item1'))
        items.add_item(item=Item(name='item2'))
        items.add_item_scope(item_name='item1', scope_name='scope1')
        items.add_item_scope(item_name='item2', scope_name='scope1')
        items.add_link_to_parent_item(parent_item_name='item2', sibling_item_name='item1')
        items.add_link_to_parent_item(parent_item_name='item1', sibling_item_name='item2')
        result = get_ordered_item_list_for_named_scope(items=items, scope_name='scope1', start_item=items.get_item_by_name(name='item1'))
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertTrue('item1' in result)
        self.assertTrue('item2' in result)
        self.assertEqual(result[0], 'item2')
        self.assertEqual(result[1], 'item1')

    def test_more_complex(self):
        items = Items()
        items.add_item(item=Item(name='item1'))
        items.add_item(item=Item(name='item2'))
        items.add_item(item=Item(name='item3'))
        items.add_item(item=Item(name='item4'))
        items.add_item_scope(item_name='item1', scope_name='scope1')
        items.add_item_scope(item_name='item2', scope_name='scope1')
        items.add_item_scope(item_name='item3', scope_name='scope1')
        items.add_item_scope(item_name='item4', scope_name='scope1')
        items.add_link_to_parent_item(sibling_item_name='item1', parent_item_name='item2')
        items.add_link_to_parent_item(sibling_item_name='item1', parent_item_name='item3')
        items.add_link_to_parent_item(sibling_item_name='item2', parent_item_name='item4')
        items.add_link_to_parent_item(sibling_item_name='item3', parent_item_name='item4')
        result = get_ordered_item_list_for_named_scope(items=items, scope_name='scope1', start_item=items.get_item_by_name(name='item1'), ordered_item_names=list())
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 4)
        self.assertTrue('item1' in result)
        self.assertTrue('item2' in result)
        self.assertTrue('item3' in result)
        self.assertTrue('item4' in result)
        self.assertEqual(result[0], 'item4')
        self.assertEqual(result[1], 'item2')
        self.assertEqual(result[2], 'item3')
        self.assertEqual(result[3], 'item1')

    def test_more_complex_scoped(self):
        items = Items()
        items.add_item(item=Item(name='item1'))
        items.add_item(item=Item(name='item2'))
        items.add_item(item=Item(name='item3'))
        items.add_item(item=Item(name='item4'))
        items.add_item_scope(item_name='item1', scope_name='scope1')
        items.add_item_scope(item_name='item2', scope_name='scope1')
        items.add_item_scope(item_name='item3', scope_name='scope1')
        items.add_item_scope(item_name='item4', scope_name='scope1')
        items.add_item_scope(item_name='item1', scope_name='scope2')
        items.add_item_scope(item_name='item2', scope_name='scope2')
        items.add_link_to_parent_item(sibling_item_name='item1', parent_item_name='item2')
        items.add_link_to_parent_item(sibling_item_name='item1', parent_item_name='item3')
        items.add_link_to_parent_item(sibling_item_name='item2', parent_item_name='item4')
        items.add_link_to_parent_item(sibling_item_name='item3', parent_item_name='item4')
        result = get_ordered_item_list_for_named_scope(items=items, scope_name='scope2', start_item=items.get_item_by_name(name='item1'), ordered_item_names=list())
        self.assertIsNotNone(result)
        self.assertIsInstance(result, list)
        self.assertEqual(len(result), 2)
        self.assertTrue('item1' in result)
        self.assertTrue('item2' in result)
        self.assertEqual(result[0], 'item2')
        self.assertEqual(result[1], 'item1')


if __name__ == '__main__':
    unittest.main()
