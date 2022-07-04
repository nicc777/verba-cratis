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


class StsClientMock:    # pragma: no cover

    def get_caller_identity(self)->dict:
        return {
            "UserId": "AIDACCCCCCCCCCCCCCCCC",
            "Account": "123456789012",
            "Arn": "arn:aws:iam::214483558614:user/my-user",
        }


class Boto3Mock:    # pragma: no cover

    def __init__(self):
        pass

    def client(self, service_name: str, region_name: str='eu-central-1'):
        if service_name == 'sts':
            return StsClientMock()


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
        result2 = Variable(id='var1', initial_value=cmd, classification='shell').get_value()
        self.assertIsInstance(result2, str)
        self.assertEqual(cmd, result2)
        cmd2 = """files=`find . -type f`
qty=`echo $files | wc -l`
echo $qty
        """
        result3 = Variable(id='var2', initial_value=cmd2, classification='shell').get_value()
        self.assertIsInstance(result2, str)
        self.assertEqual(cmd, result2)

    def test_class_variable_to_string(self):
        result = str(Variable(id='var1', initial_value='test'))
        self.assertEqual(result, 'Variable: id=var1 classification=build-variable >> value as string: test')


class TestClassVariableStateStore(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        self.classifications = (
            'build-variable',
            'ref',
            'exports',
            'shell',
            'func',
            'other',
        )

    def test_class_variable_state_store_init_defaults(self):
        result = VariableStateStore()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, VariableStateStore)
        self.assertIsNotNone(result.variables)
        self.assertIsInstance(result.variables, dict)
        self.assertTrue(len(result.variables) == len(self.classifications))
        for key in self.classifications:
            self.assertTrue(key in result.variables, 'Expecting key "{}" but not found'.format(key))

    def test_class_variable_state_store_add_variable(self):
        store = VariableStateStore()
        v1 = Variable(id='ref:var1', initial_value='', classification='ref')
        v2 = Variable(id='func:print_s(message="${{var:var1}}")', initial_value='', classification='func')
        store.add_variable(var=v1)
        store.add_variable(var=v2)
        self.assertIsNotNone(store)
        self.assertTrue(len(store.variables['ref']) == 1)
        self.assertTrue(len(store.variables['func']) == 1)
        self.assertTrue(len(store.variables['build-variable']) == 0)
        self.assertTrue(len(store.variables['exports']) == 0)
        self.assertTrue(len(store.variables['shell']) == 0)
        self.assertTrue(len(store.variables['other']) == 0)

    def test_class_variable_state_store_add_variable_force_exception(self):
        store = VariableStateStore()
        invalid_classification = 'not-going-to-work'
        v1 = Variable(id='ref:var1', initial_value='', classification='ref')
        v1.classification = invalid_classification
        with self.assertRaises(Exception) as context:
            store.add_variable(var=v1)
        self.assertTrue('Variable classification "not-going-to-work" is not supported' in str(context.exception))


class TestClassVariableStateStoreOperations(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        self.store = VariableStateStore()
        v1 = Variable(id='aa', initial_value='var1', classification='ref')
        v2 = Variable(id='bb', initial_value='${}func:print_s(message="${}ref:var1{}"){}'.format('{', '{', '}', '}'), classification='func')

        cmd1 = "find . -type f | awk -F\/ '{print $1}' | wc -l"
        v3 = Variable(id='cc', initial_value=cmd1, classification='shell')

        cmd2 = """files=`find . -type f`
qty=`echo $files | wc -l`
echo $qty
        """
        v4 = Variable(id='dd', initial_value=cmd2, classification='shell')
        v5 = Variable(id='ee', initial_value='${}func:get_aws_identity{}'.format('{', '{', '}', '}'), classification='func')
        v6 = Variable(id='ff', initial_value='${}func:get_aws_identity(){}'.format('{', '{', '}', '}'), classification='func')
        v7 = Variable(id='gg', initial_value='${}func:get_aws_identity(include_account_if_available=True){}'.format('{', '}'), classification='func', extra_parameters={'boto3_clazz': Boto3Mock()})
        v8 = Variable(id='hh', initial_value=True, classification='build-variable', value_type=bool)
        v9 = Variable(id='ii', initial_value='${}func:get_aws_identity(include_account_if_available=${}ref:hh{}){}'.format('{', '{', '}', '}'), classification='func', extra_parameters={'boto3_clazz': Boto3Mock()})

        self.store.add_variable(var=v1)
        self.store.add_variable(var=v2)
        self.store.add_variable(var=v3)
        self.store.add_variable(var=v4)
        self.store.add_variable(var=v5)
        self.store.add_variable(var=v6)
        self.store.add_variable(var=v7)
        self.store.add_variable(var=v8)
        self.store.add_variable(var=v9)

    def test_class_variable_state_store_ops_get_variable(self):
        result1 = self.store.get_variable(id='aa', classification='ref')
        self.assertIsNotNone(result1)
        self.assertIsInstance(result1, Variable)
        self.assertTrue(result1.id == 'aa')
        result2 = self.store.get_variable(id='bb', classification='func')
        self.assertIsNotNone(result2)
        self.assertIsInstance(result2, Variable)
        self.assertTrue(result2.id == 'bb')

    def test_class_variable_state_store_ops_get_variable_exception(self):
        with self.assertRaises(Exception) as context:
            self.store.get_variable(id='where-am-i', classification='func')
        self.assertTrue('Variable with id "where-am-i" with classification "func" does not exist' in str(context.exception))


    def test_class_variable_state_store_ops_get_variable_value_aa_no_processing(self):
        result = self.store.get_variable_value(id='aa', classification='ref', skip_embedded_variable_processing=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue(result, 'var1')

    def test_class_variable_state_store_ops_get_variable_value_aa(self):
        result = self.store.get_variable_value(id='aa', classification='ref', skip_embedded_variable_processing=False)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue(result, 'var1')

    def test_class_variable_state_store_ops_get_variable_value_bb_expect_exception(self):
        with self.assertRaises(Exception) as context:
            self.store.get_variable_value(id='bb', classification='func', skip_embedded_variable_processing=False)
        self.assertTrue('Function "print_s" is not a recognized function.' in str(context.exception))

    def test_class_variable_state_store_ops_get_variable_value_ee_expect_exception(self):
        with self.assertRaises(Exception) as context:
            self.store.get_variable_value(id='ee', classification='func', skip_embedded_variable_processing=False)
        self.assertTrue('Value does not appear to contain a function call' in str(context.exception))

    def test_class_variable_state_store_ops_get_variable_value_ff_expect_success(self):
        result = self.store.get_variable_value(id='ff', classification='func', skip_embedded_variable_processing=False)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)

    def test_class_variable_state_store_ops_get_variable_value_cc(self):
        result = int(self.store.get_variable_value(id='cc', classification='shell', skip_embedded_variable_processing=False))
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)
        self.assertTrue(result > 0)

    def test_class_variable_state_store_ops_get_variable_value_dd(self):
        result = int(self.store.get_variable_value(id='dd', classification='shell', skip_embedded_variable_processing=False))
        self.assertIsNotNone(result)
        self.assertIsInstance(result, int)
        self.assertTrue(result > 0)

    @unittest.skip("Function processing not yet implemented, so this will fail")    # TODO re-activate test
    def test_class_variable_state_store_ops_get_variable_value_gg(self):
        result = self.store.get_variable_value(id='gg', classification='func')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertEqual(result, 'UserId=AIDACCCCCCCCCCCCCCCCC', 'result contained "{}"'.format(result))

    def test_class_variable_state_store_ops_get_variable_value_hh(self):
        result = self.store.get_variable_value(id='hh', classification='build-variable')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    @unittest.skip("Function processing not yet implemented, so this will fail")    # TODO re-activate test
    def test_class_variable_state_store_ops_get_variable_value_ii(self):
        result = self.store.get_variable_value(id='i', classification='func')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertEqual(result, 'UserId=AIDACCCCCCCCCCCCCCCCC,Account=123456789012', 'result contained "{}"'.format(result))


class TestClassVariableStateStoreOperationsMaxDepthTest(unittest.TestCase):    # pragma: no cover

    def test_class_variable_state_store_ops_get_variable_value_exceeding_max_depth_processing(self):
        # 'ref:${ref:${ref:${ref:${ref:${ref:value}}}}}'
        value = 'ref:${}ref:${}ref:${}ref:${}ref:${}ref:value{}{}{}{}{}'.format(
            '{', 
            '{', 
            '{', 
            '{', 
            '{', 
            '}', 
            '}', 
            '}', 
            '}', 
            '}'
        )
        v1 = Variable(id='aa', initial_value=value, classification='ref')
        store = VariableStateStore()
        store.add_variable(var=v1)
        with self.assertRaises(Exception) as context:
            store.get_variable_value(id='aa', classification='ref')
        self.assertTrue('Maximum embedded variable parsing depth exceeded' in str(context.exception))


if __name__ == '__main__':
    unittest.main()
