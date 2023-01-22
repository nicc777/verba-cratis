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
from verbacratis.models.ordering import *


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


if __name__ == '__main__':
    unittest.main()
