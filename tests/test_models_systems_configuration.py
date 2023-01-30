"""
    Copyright (c) 2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
import tempfile
import traceback
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest


from verbacratis.models.systems_configuration import *
from sqlalchemy.engine import Engine


class TestAuthentication(unittest.TestCase):    # pragma: no cover

    def test_unix_host_authentication_init_with_defaults(self):
        result =Authentication()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Authentication)

        unix_yaml = str(result)
        self.assertIsNotNone(unix_yaml)
        self.assertIsInstance(unix_yaml, str)
        self.assertTrue(len(unix_yaml) > 10)
        print('='*80)
        print('# Authentication YAML')
        print(unix_yaml)
        print('='*80)

    def test_unix_host_authentication_method_as_dict(self):
        host = Authentication()
        result = host.as_dict()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)


class TestUnixHostAuthentication(unittest.TestCase):    # pragma: no cover

    def test_unix_host_authentication_init_with_defaults(self):
        result = UnixHostAuthentication()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, UnixHostAuthentication)

        unix_yaml = str(result)
        self.assertIsNotNone(unix_yaml)
        self.assertIsInstance(unix_yaml, str)
        self.assertTrue(len(unix_yaml) > 10)
        print('='*80)
        print('# UnixHostAuthentication YAML')
        print(unix_yaml)
        print('='*80)

    def test_unix_host_authentication_method_as_dict(self):
        host = UnixHostAuthentication(hostname='example.tld')
        result = host.as_dict()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)


class TestSshHostBasedAuthenticationConfig(unittest.TestCase):    # pragma: no cover

    def test_ssh_host_based_authentication_config_init_with_defaults(self):
        result = SshHostBasedAuthenticationConfig(hostname='example.tld', username='testuser')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, UnixHostAuthentication)
        self.assertIsInstance(result, SshHostBasedAuthenticationConfig)

        unix_yaml = str(result)
        self.assertIsNotNone(unix_yaml)
        self.assertIsInstance(unix_yaml, str)
        self.assertTrue(len(unix_yaml) > 10)
        print('='*80)
        print('# UnixHostAuthentication YAML')
        print(unix_yaml)
        print('='*80)

    def test_ssh_host_based_authentication_config_init_with_username_validation_failures(self):
        with self.assertRaises(Exception) as context:
            SshHostBasedAuthenticationConfig(hostname='example.tld', username=None)
        self.assertTrue('username is required' in str(context.exception))

        with self.assertRaises(Exception) as context:
            SshHostBasedAuthenticationConfig(hostname='example.tld', username=123)
        self.assertTrue('username must be a string value' in str(context.exception))

        with self.assertRaises(Exception) as context:
            SshHostBasedAuthenticationConfig(hostname='example.tld', username='')
        self.assertTrue('username is required' in str(context.exception))


class TestSshCredentialsBasedAuthenticationConfig(unittest.TestCase):    # pragma: no cover

    def test_ssh_credentials_based_authentication_config_init_with_defaults(self):
        result = SshCredentialsBasedAuthenticationConfig(hostname='example.tld', username='testuser', password='password')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, UnixHostAuthentication)
        self.assertIsInstance(result, SshHostBasedAuthenticationConfig)
        self.assertIsInstance(result, SshCredentialsBasedAuthenticationConfig)

        as_dict = result.as_dict()
        self.assertEqual(as_dict['spec']['password'], '*'*len(result.password))

        unix_yaml = str(result)
        self.assertIsNotNone(unix_yaml)
        self.assertIsInstance(unix_yaml, str)
        self.assertTrue(len(unix_yaml) > 10)
        print('='*80)
        print('# UnixHostAuthentication YAML')
        print(unix_yaml)
        print('='*80)

    def test_ssh_credentials_based_authentication_config_init_with_password_in_environment_variable(self):
        result = SshCredentialsBasedAuthenticationConfig(hostname='example.tld', username='testuser', password='${{EnvironmentVariables:computed:MyPassword}}')

        as_dict = result.as_dict()
        self.assertEqual(as_dict['spec']['password'], '${{EnvironmentVariables:computed:MyPassword}}')

        unix_yaml = str(result)
        self.assertIsNotNone(unix_yaml)
        self.assertIsInstance(unix_yaml, str)
        self.assertTrue(len(unix_yaml) > 10)
        print('='*80)
        print('# UnixHostAuthentication YAML')
        print(unix_yaml)
        print('='*80)


class TextSshPrivateKeyBasedAuthenticationConfig(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        tmp_key_file = '{}{}test_key_file'.format(
            tempfile.gettempdir(),
            os.sep
        )
        if os.path.exists(tmp_key_file):
            try:
                os.remove(tmp_key_file)
            except:
                traceback.print_exc()
        if os.path.exists(tmp_key_file) is False:
            try:
                with open(tmp_key_file, 'w') as f:
                    f.write('test data')
            except:
                traceback.print_exc()
        self.private_key_file = tmp_key_file
        if os.path.exists(tmp_key_file):
            print('TEST KEY FILE CREATED {}'.format(self.private_key_file))
        else:
            print('TEST KEY FILE FAILED TO BE CREATED {}'.format(self.private_key_file))

    def tearDown(self):
        if os.path.exists(self.private_key_file):
            try:
                os.remove(self.private_key_file)
            except:
                traceback.print_exc()

    def test_ssh_private_key_based_authentication_config_init_with_defaults(self):
        result = SshPrivateKeyBasedAuthenticationConfig(hostname='example.tld', username='testuser', private_key_path=self.private_key_file)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, UnixHostAuthentication)
        self.assertIsInstance(result, SshHostBasedAuthenticationConfig)
        self.assertIsInstance(result, SshPrivateKeyBasedAuthenticationConfig)

    def test_ssh_private_key_based_authentication_config_init_with_non_existing_key_file(self):
        with self.assertRaises(Exception) as context:
            SshPrivateKeyBasedAuthenticationConfig(hostname='example.tld', username='testuser', private_key_path='/does/not/exists')
        self.assertTrue('Private Key file "/does/not/exists" does not exist' in str(context.exception))

    def test_ssh_private_key_based_authentication_config_method_as_dict(self):
        host = SshPrivateKeyBasedAuthenticationConfig(hostname='example.tld', username='testuser', private_key_path=self.private_key_file)
        result = host.as_dict()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)


class TestAwsAuthentication(unittest.TestCase):    # pragma: no cover

    def test_aws_authentication_init_with_defaults(self):
        host = AwsAuthentication()
        self.assertIsNotNone(host)
        self.assertIsInstance(host, AwsAuthentication)
        self.assertEqual(host.region, 'eu-central-1')
        
    def test_aws_authentication_method_as_dict(self):
        host = AwsAuthentication()
        result = host.as_dict()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)
        for element in ('apiVersion', 'kind', 'metadata', 'spec'):
            self.assertTrue(element in result, 'Key "{}" not found'.format(element))

    def test_aws_authentication_dump_yaml(self):
        host = AwsAuthentication()
        yaml_result = str(host)
        self.assertIsNotNone(yaml_result)
        self.assertIsInstance(yaml_result, str)
        self.assertTrue(len(yaml_result) > 10)
        print('='*80)
        print('# AwsAuthentication YAML')
        print(yaml_result)
        print('='*80)


class TestAwsKeyBasedAuthentication(unittest.TestCase):    # pragma: no cover

    def test_aws_key_based_authentication_init_with_defaults(self):
        host = AwsKeyBasedAuthentication(account_reference='default')
        self.assertIsNotNone(host)
        self.assertIsInstance(host, AwsAuthentication)
        self.assertIsInstance(host, AwsKeyBasedAuthentication)

    def test_aws_key_based_authentication_init_with_values_secret_insecure(self):
        host = AwsKeyBasedAuthentication(account_reference='default', access_key='abc', secret_key='def')
        result = host.as_dict()
        self.assertEqual(result['spec']['secret_key'], '***')

    def test_aws_key_based_authentication_init_with_values_secret_secure(self):
        host = AwsKeyBasedAuthentication(account_reference='default', access_key='abc', secret_key='${{EnvironmentVariables:computed:someSecret}}')
        result = host.as_dict()
        self.assertEqual(result['spec']['secret_key'], '${{EnvironmentVariables:computed:someSecret}}')

    def test_aws_key_based_authentication_dump_yaml(self):
        host = AwsKeyBasedAuthentication(account_reference='default', access_key='abc', secret_key='${{EnvironmentVariables:computed:someSecret}}')
        yaml_result = str(host)
        self.assertIsNotNone(yaml_result)
        self.assertIsInstance(yaml_result, str)
        self.assertTrue(len(yaml_result) > 10)
        print('='*80)
        print('# AwsKeyBasedAuthentication YAML')
        print(yaml_result)
        print('='*80)


class TestAwsProfileBasedAuthentication(unittest.TestCase):    # pragma: no cover

    def test_aws_profile_based_authentication_init_with_defaults(self):
        host = AwsProfileBasedAuthentication(account_reference='default', profile_name='default')
        self.assertIsNotNone(host)
        self.assertIsInstance(host, AwsAuthentication)
        self.assertIsInstance(host, AwsProfileBasedAuthentication)

    def test_aws_key_based_authentication_init_with_values_secret_insecure(self):
        host = AwsProfileBasedAuthentication(account_reference='abc', profile_name='default')
        result = host.as_dict()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_aws_key_based_authentication_dump_yaml(self):
        host = AwsProfileBasedAuthentication(account_reference='abc', profile_name='default')
        yaml_result = str(host)
        self.assertIsNotNone(yaml_result)
        self.assertIsInstance(yaml_result, str)
        self.assertTrue(len(yaml_result) > 10)
        print('='*80)
        print('# AwsKeyBasedAuthentication YAML')
        print(yaml_result)
        print('='*80)


class TestInfrastructureAccount(unittest.TestCase):    # pragma: no cover

    def test_infrastructure_account_init_with_defaults(self):
        result = InfrastructureAccount()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, InfrastructureAccount)
        self.assertIsNotNone(result.account_name)
        self.assertEqual(result.account_name, 'deployment-host')
        self.assertIsNotNone(result.account_provider)
        self.assertEqual(result.account_provider, 'RunOnLocalhost')
        self.assertIsNotNone(result.environments)
        self.assertIsInstance(result.environments, list)
        self.assertEqual(len(result.environments), 1)
        self.assertTrue('default' in result.environments)

    def test_infrastructure_account_dump_yaml(self):
        result = InfrastructureAccount()
        yaml_result = str(result)
        self.assertIsNotNone(yaml_result)
        self.assertIsInstance(yaml_result, str)
        self.assertTrue(len(yaml_result) > 10)
        print('='*80)
        print('# InfrastructureAccount YAML')
        print(yaml_result)
        print('='*80)


class TestUnixInfrastructureAccount(unittest.TestCase):    # pragma: no cover

    def test_infrastructure_account_with_credential_based_authentication_dump_yaml(self):
        result = UnixInfrastructureAccount(account_name='host1')
        result.authentication_config = SshCredentialsBasedAuthenticationConfig(hostname='host1.myorg', username='cd-user', password='${{EnvironmentVariables:computed:someSecret}}')
        yaml_result = str(result)
        self.assertIsNotNone(yaml_result)
        self.assertIsInstance(yaml_result, str)
        self.assertTrue(len(yaml_result) > 10)
        print('='*80)
        print('# UnixInfrastructureAccount YAML')
        print(yaml_result)
        print('='*80)

    def test_infrastructure_account_with_credential_based_authentication_method_auth_id(self):
        result = UnixInfrastructureAccount(account_name='host1')
        result.authentication_config = SshCredentialsBasedAuthenticationConfig(hostname='host1.myorg', username='cd-user', password='${{EnvironmentVariables:computed:someSecret}}')
        auth_id = result.auth_id()
        self.assertIsNotNone(auth_id)
        self.assertIsInstance(auth_id, str)
        self.assertEqual(auth_id, 'cd-user@host1.myorg')
        

if __name__ == '__main__':
    unittest.main()
