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

from verbacratis.models.runtime_configuration import BUILD_ID
from verbacratis.models.runtime import *
from verbacratis.functions import user_function_factory
from verbacratis.utils import get_logger
from verbacratis.utils.parser import parse_configuration_file


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


def get_aws_identity_mock1(     # pragma: no cover
    boto3_clazz: object=Boto3Mock(),
    region: str='eu-central-1',
    logger=get_logger(),
    include_account_if_available: bool=False,
    include_arn_if_available: bool=False,
    delimiter_char: str=','
):
    raise Exception('Function Threw an Exception')


@unittest.skip("Deprecated")
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


@unittest.skip("Deprecated")
class TestClassVariableStateStore(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        self.classifications = (
            'build-variable',
            'ref',
            'exports',
            'shell',
            'func',
            'other',
            'env',
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
        v2 = Variable(id='func:print_s(message="${{build-variable:var1}}")', initial_value='', classification='func')
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


@unittest.skip("Deprecated")
class TestClassVariableStateStoreOperations(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        self.store = VariableStateStore(registered_functions=user_function_factory())
        self.store2 = VariableStateStore(
            registered_functions={
                'get_aws_identity': {
                    'f': get_aws_identity_mock1,
                    'fixed_parameters': {
                        'boto3_clazz': Boto3Mock(),
                    },
                },
            },
        )

        v1 = Variable(id='aa', initial_value='var1', classification='build-variable')
        v2 = Variable(id='bb', initial_value='${}func:print_s(message="${}ref:aa{}"){}'.format('{', '{', '}', '}'), classification='func')

        cmd1 = "find . -type f | awk -F\/ '{print $1}' | wc -l"
        v3 = Variable(id='cc', initial_value=cmd1, classification='shell')

        cmd2 = """files=`find . -type f`
qty=`echo $files | wc -l`
echo $qty
        """
        v4 = Variable(id='dd', initial_value=cmd2, classification='shell')
        v5 = Variable(id='ee', initial_value='${}func:get_aws_identity{}'.format('{', '}'), classification='func')
        v6 = Variable(id='ff', initial_value='${}func:get_aws_identity(){}'.format('{', '{', '}', '}'), classification='func', extra_parameters={'boto3_clazz': Boto3Mock()})
        v7 = Variable(id='gg', initial_value='${}func:get_aws_identity(include_account_if_available=True){}'.format('{', '}'), classification='func', extra_parameters={'boto3_clazz': Boto3Mock()})
        v8 = Variable(id='hh', initial_value=True, classification='build-variable', value_type=bool)
        v9 = Variable(id='ii', initial_value='${}func:get_aws_identity(include_account_if_available=${}build-variable:hh{}){}'.format('{', '{', '}', '}'), classification='func', extra_parameters={'boto3_clazz': Boto3Mock()})
        v10 = Variable(id='kk', initial_value=True, classification='build-variable', value_type=bool)
        v11 = Variable(id='ll', initial_value='DOES_NOT_EXIST', classification='env', value_type=str, extra_parameters={'default_value': 'some value'})
        v12 = Variable(id='mm', initial_value='HOME', classification='env', value_type=str, extra_parameters={'default_value': ''})
        v13 = Variable(id='nn', initial_value='aa', classification='ref')

        # Invalid Function Parameters
        e1 = Variable(id='jj', initial_value='${}func:get_aws_identity(blablabla=$$){}'.format('{', '{', '}', '}'), classification='func', extra_parameters={'boto3_clazz': Boto3Mock()})

        self.store.add_variable(var=v1)
        self.store.add_variable(var=v2)
        self.store.add_variable(var=v3)
        self.store.add_variable(var=v4)
        self.store.add_variable(var=v5)
        self.store.add_variable(var=v6)
        self.store.add_variable(var=v7)
        self.store.add_variable(var=v8)
        self.store.add_variable(var=v9)
        self.store.add_variable(var=v10)
        self.store.add_variable(var=v11)
        self.store.add_variable(var=v12)
        self.store.add_variable(var=v13)
        self.store.add_variable(var=e1)

        self.store2.add_variable(var=v1)
        self.store2.add_variable(var=v2)
        self.store2.add_variable(var=v3)
        self.store2.add_variable(var=v4)
        self.store2.add_variable(var=v5)
        self.store2.add_variable(var=v6)
        self.store2.add_variable(var=v7)
        self.store2.add_variable(var=v8)
        self.store2.add_variable(var=v9)
        self.store2.add_variable(var=v10)
        self.store2.add_variable(var=v11)
        self.store2.add_variable(var=v12)
        self.store2.add_variable(var=v13)
        self.store2.add_variable(var=e1)

    def test_class_variable_state_store_ops_get_variable(self):
        result1 = self.store.get_variable(id='aa', classification='build-variable')
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
        result = self.store.get_variable_value(id='aa', classification='build-variable', skip_embedded_variable_processing=True)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue(result, 'var1')

    def test_class_variable_state_store_ops_get_variable_value_aa(self):
        result = self.store.get_variable_value(id='aa', classification='build-variable', skip_embedded_variable_processing=False)
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
        self.assertEqual(result, 'UserId=AIDACCCCCCCCCCCCCCCCC', 'result contained "{}"'.format(result))

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

    def test_class_variable_state_store_ops_get_variable_value_gg(self):
        result = self.store.get_variable_value(id='gg', classification='func')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertEqual(result, 'UserId=AIDACCCCCCCCCCCCCCCCC,Account=123456789012', 'result contained "{}"'.format(result))

    def test_class_variable_state_store_ops_get_variable_value_hh(self):
        result = self.store.get_variable_value(id='hh', classification='build-variable')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_class_variable_state_store_ops_get_variable_value_ii(self):
        result = self.store.get_variable_value(id='ii', classification='func')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertEqual(result, 'UserId=AIDACCCCCCCCCCCCCCCCC,Account=123456789012', 'result contained "{}"'.format(result))

    def test_class_variable_state_store_ops_get_variable_value_jj(self):
        result = self.store.get_variable_value(id='jj', classification='func')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertEqual(result, 'UserId=AIDACCCCCCCCCCCCCCCCC', 'result contained "{}"'.format(result))

    def test_class_variable_state_store_ops_get_variable_value_ee_force_exception(self):
        result = self.store2.get_variable_value(id='jj', classification='func')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertEqual(result, '', 'result contained "{}"'.format(result))

    def test_class_variable_state_store_ops_update_variable_kk_value_true_from_string(self):
        kk = self.store.get_variable(id='kk', classification='build-variable')
        kk.value = '1'
        self.store.update_variable(variable=kk)
        result = self.store.get_variable_value(id='kk', classification='build-variable')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_class_variable_state_store_ops_update_variable_kk_value_false_from_string(self):
        kk = self.store.get_variable(id='kk', classification='build-variable')
        kk.value = 'false'
        self.store.update_variable(variable=kk)
        result = self.store.get_variable_value(id='kk', classification='build-variable')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_class_variable_state_store_ops_update_variable_kk_value_true_from_int(self):
        kk = self.store.get_variable(id='kk', classification='build-variable')
        kk.value = 1
        self.store.update_variable(variable=kk)
        result = self.store.get_variable_value(id='kk', classification='build-variable')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_class_variable_state_store_ops_update_variable_kk_value_false_from_int(self):
        kk = self.store.get_variable(id='kk', classification='build-variable')
        kk.value = 0
        self.store.update_variable(variable=kk)
        result = self.store.get_variable_value(id='kk', classification='build-variable')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, bool)
        self.assertFalse(result)

    def test_class_variable_state_store_ops_get_variable_value_kk(self):
        result = self.store.get_variable_value(id='kk', classification='build-variable')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, bool)
        self.assertTrue(result)

    def test_class_variable_state_store_ops_get_variable_value_ll(self):
        result = self.store.get_variable_value(id='ll', classification='env')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue('some value' in result)

    def test_class_variable_state_store_ops_get_variable_value_mm(self):
        result = self.store.get_variable_value(id='mm', classification='env')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue('home' in result.lower())

    def test_class_variable_state_store_ops_get_variable_value_nn(self):
        result = self.store.get_variable_value(id='nn', classification='ref')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertEqual('var1', result)


@unittest.skip("Deprecated")
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


@unittest.skip("Deprecated")
class TestFunctionConfigurationToVariableStateStore(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        self.configuration = parse_configuration_file(file_path='examples/example_01/example_01.yaml')
        self.initial_state_store = BUILD_ID

    def test_configuration_to_variable_state_store_call_with_defaults(self):
        state_store = VariableStateStore()
        state_store.add_variable(var=Variable(id='build_id', initial_value=BUILD_ID, value_type=str))
        result = configuration_to_variable_state_store(variable_state_store=state_store, configuration=self.configuration) 
        self.assertIsNotNone(result)
        self.assertIsInstance(result, VariableStateStore)

    def test_configuration_to_variable_state_store_call_with_invalid_configuration_expect_exception(self):
        with self.assertRaises(Exception) as context:
            configuration_to_variable_state_store(configuration={'test': 'this will never pass'})
        self.assertTrue('Configuration is invalid' in str(context.exception))


if __name__ == '__main__':
    unittest.main()
