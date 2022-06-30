"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest


from acfop.models.runtime import *


class TestClassVariable(unittest.TestCase):    # pragma: no cover

    def test_class_variable_init_defaults(self):
        result = Variable(id='var1')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Variable)
        self.assertEqual(result.id, 'var1')
        self.assertIsNone(result.value)
        self.assertEqual(result.value_type, str)
        self.assertEqual(result.classification, 'build-variable')

    def test_class_variable_init_invalid_classification(self):
        with self.assertRaises(Exception) as context:
            Variable(id='var1', classification='invalid')
        self.assertTrue('Invalid Classification' in str(context.exception))

    def test_class_variable_init_invalid_value_and_value_type_mismatch(self):
        with self.assertRaises(Exception) as context:
            Variable(id='var1', initial_value=123, value_type=str)
        self.assertTrue('Initial value must match value_type or None' in str(context.exception))

    def test_class_variable_method_get_value(self):
        for cf in ('build-variable', 'ref', 'exports'):
            result = Variable(id='var1', initial_value='test', classification=cf)
            self.assertEqual(result.get_value(), 'test', 'failed to fet value for classification {}'.format(cf))
        cmd = "find . -type f | awk -F\/ '{print $1}' | wc -l"
        result2 = int(Variable(id='var1', initial_value=cmd, classification='shell').get_value())
        self.assertIsInstance(result2, int)
        self.assertTrue(result2 > 0)
        cmd2 = """files=`find . -type f`
qty=`echo $files | wc -l`
echo $qty
        """
        result3 = int(Variable(id='var2', initial_value=cmd2, classification='shell').get_value())
        self.assertIsInstance(result2, int)
        self.assertTrue(result2 > 0)
        with self.assertRaises(Exception) as context:
            Variable(id='var1', initial_value='some value', classification='other').get_value()
        self.assertTrue('Classification "other" not yet supported' in str(context.exception))

    def test_class_variable_to_string(self):
        result = str(Variable(id='var1', initial_value='test'))
        self.assertEqual(result, 'Variable: id=var1 classification=build-variable >> value as string: test')


class TestClassVariableStateStore(unittest.TestCase):    # pragma: no cover

    def test_class_variable_state_store_init_defaults(self):
        result = VariableStateStore()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, VariableStateStore)


if __name__ == '__main__':
    unittest.main()
