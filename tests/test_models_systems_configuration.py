"""
    Copyright (c) 2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
from pathlib import Path
import os
import tempfile
import traceback
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest


from verbacratis.models.systems_configuration import *
from verbacratis.utils.parser2 import parse_yaml_file


def mock_get_file_contents(file: str)->str: # pragma: no cover
    return """---
apiVersion: v1-alpha
kind: SshCredentialsBasedAuthenticationConfig
metadata:
  name: cd-user@host1.myorg
spec:
  authenticationType: SshUsingCredentials
  password: ${{EnvironmentVariables:computed:someSecret}}
---
apiVersion: v1-alpha
kind: UnixInfrastructureAccount
metadata:
  environments:
  - default
  name: host1
spec:
  authentication:
    authenticationReference: cd-user@host1.myorg
    type: SshCredentialsBasedAuthenticationConfig
  provider: ShellScript
---
apiVersion: v1-alpha
kind: AwsProfileBasedAuthentication
metadata:
  name: accXYZ
spec:
  profile_name: profile_01
  region: eu-central-1
---
apiVersion: v1-alpha
kind: AwsInfrastructureAccount
metadata:
  environments:
  - sandbox-env
  name: sandbox-account
spec:
  authentication:
    authenticationReference: accXYZ
    type: AwsProfileBasedAuthentication
  provider: AWS
        """


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
        host = AwsKeyBasedAuthentication(name='default')
        self.assertIsNotNone(host)
        self.assertIsInstance(host, AwsAuthentication)
        self.assertIsInstance(host, AwsKeyBasedAuthentication)

    def test_aws_key_based_authentication_init_with_values_secret_insecure(self):
        host = AwsKeyBasedAuthentication(name='default', access_key='abc', secret_key='def')
        result = host.as_dict()
        self.assertEqual(result['spec']['secret_key'], '***')

    def test_aws_key_based_authentication_init_with_values_secret_secure(self):
        host = AwsKeyBasedAuthentication(name='default', access_key='abc', secret_key='${{EnvironmentVariables:computed:someSecret}}')
        result = host.as_dict()
        self.assertEqual(result['spec']['secret_key'], '${{EnvironmentVariables:computed:someSecret}}')

    def test_aws_key_based_authentication_dump_yaml(self):
        host = AwsKeyBasedAuthentication(name='default', access_key='abc', secret_key='${{EnvironmentVariables:computed:someSecret}}')
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
        credentials = AwsProfileBasedAuthentication(name='default', profile_name='default')
        self.assertIsNotNone(credentials)
        self.assertIsInstance(credentials, AwsAuthentication)
        self.assertIsInstance(credentials, AwsProfileBasedAuthentication)

    def test_aws_key_based_authentication_init_with_values_secret_insecure(self):
        credentials = AwsProfileBasedAuthentication(name='abc', profile_name='default')
        result = credentials.as_dict()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, dict)

    def test_aws_key_based_authentication_dump_yaml(self):
        credentials = AwsProfileBasedAuthentication(name='abc', profile_name='default')
        yaml_result = str(credentials)
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

    def test_infrastructure_account_init_with_no_environments_creates_default_environment(self):
        acc = InfrastructureAccount(environments=list())
        acc_dict = acc.as_dict()
        result = acc_dict['metadata']['environments']
        self.assertEqual(len(result), 1)
        self.assertTrue('default' in result)


class TestUnixInfrastructureAccount(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        self.private_key_file = '/tmp/test-key-for-test-host-1.pem'
        if Path(self.private_key_file).exists() is False:
            with open(self.private_key_file, 'w') as f:
                f.write('no-real-content')

    def tearDown(self):
        if Path(self.private_key_file).exists() is True:
            os.remove(self.private_key_file)

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

    def test_infrastructure_account_with_ssh_private_key_based_authentication_Config_dump_yaml(self):
        result = UnixInfrastructureAccount(account_name='host1')
        result.authentication_config = SshPrivateKeyBasedAuthenticationConfig(hostname='test-host-1', username='test-user', private_key_path=self.private_key_file)
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

    def test_infrastructure_account_init_with_no_environments_creates_default_environment(self):
        acc = UnixInfrastructureAccount(environments=list())
        acc_dict = acc.as_dict()
        result = acc_dict['metadata']['environments']
        self.assertEqual(len(result), 1)
        self.assertTrue('default' in result)

    def test_infrastructure_account_init_with_no_auth_config_returns_none_when_calling_method_auth_id(self):
        acc = UnixInfrastructureAccount(environments=list())
        acc.authentication_config = None
        auth_config = acc.auth_id()
        self.assertIsNone(auth_config)

    def test_infrastructure_account_init_with_no_auth_config_returns_alt_name_when_calling_method_auth_id(self):
        acc = UnixInfrastructureAccount(environments=list())
        auth_config = Authentication()
        auth_config.name = 'test'
        auth_config.username = None
        acc.authentication_config = auth_config # Replace default
        result = acc.auth_id()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertEqual(result, 'test')


class TestAwsInfrastructureAccount(unittest.TestCase):    # pragma: no cover

    def test_aws_infrastructure_account_with_aws_profile_based_Authentication_dump_yaml(self):
        credentials = AwsProfileBasedAuthentication(name='accXYZ', profile_name='profile_01')
        account = AwsInfrastructureAccount(account_name='sandbox-account', environments=['sandbox-env',], authentication_config=credentials)
        yaml_result = str(account)
        self.assertIsNotNone(yaml_result)
        self.assertIsInstance(yaml_result, str)
        self.assertTrue(len(yaml_result) > 10)
        print('='*80)
        print('# AwsInfrastructureAccount YAML')
        print(yaml_result)
        print('='*80)

    def test_infrastructure_account_init_with_no_environments_creates_default_environment(self):
        acc = AwsInfrastructureAccount(account_name='test', environments=list())
        acc_dict = acc.as_dict()
        result = acc_dict['metadata']['environments']
        self.assertEqual(len(result), 1)
        self.assertTrue('default' in result)


class TestSystemConfigurations(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        self.manifest_data = parse_yaml_file(file_path='data', get_file_contents_function=mock_get_file_contents)

    def test_SystemConfigurations_create_classes_from_manifest(self):
        system_configuration = SystemConfigurations()
        system_configuration.parse_yaml(raw_data=self.manifest_data)
        self.assertIsNotNone(system_configuration)
        self.assertIsInstance(system_configuration, SystemConfigurations)

        # TODO add tests to validate each object in system_configuration.parsed_configuration has been created correctly
        self.assertTrue('Authentication' in system_configuration.parsed_configuration)
        self.assertTrue('UnixHostAuthentication' in system_configuration.parsed_configuration)
        self.assertTrue('SshHostBasedAuthenticationConfig' in system_configuration.parsed_configuration)
        self.assertTrue('SshCredentialsBasedAuthenticationConfig' in system_configuration.parsed_configuration)
        self.assertTrue('SshPrivateKeyBasedAuthenticationConfig' in system_configuration.parsed_configuration)
        self.assertTrue('AwsAuthentication' in system_configuration.parsed_configuration)
        self.assertTrue('AwsKeyBasedAuthentication' in system_configuration.parsed_configuration)
        self.assertTrue('AwsProfileBasedAuthentication' in system_configuration.parsed_configuration)
        self.assertTrue('InfrastructureAccount' in system_configuration.parsed_configuration)
        self.assertTrue('UnixInfrastructureAccount' in system_configuration.parsed_configuration)
        self.assertTrue('AwsInfrastructureAccount' in system_configuration.parsed_configuration)
        self.assertEqual(len(system_configuration.parsed_configuration['Authentication']), 1)
        self.assertEqual(len(system_configuration.parsed_configuration['UnixHostAuthentication']), 0)
        self.assertEqual(len(system_configuration.parsed_configuration['SshHostBasedAuthenticationConfig']), 0)
        self.assertEqual(len(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig']), 1)
        self.assertEqual(len(system_configuration.parsed_configuration['SshPrivateKeyBasedAuthenticationConfig']), 0)
        self.assertEqual(len(system_configuration.parsed_configuration['AwsAuthentication']), 0)
        self.assertEqual(len(system_configuration.parsed_configuration['AwsKeyBasedAuthentication']), 0)
        self.assertEqual(len(system_configuration.parsed_configuration['AwsProfileBasedAuthentication']), 1)
        self.assertEqual(len(system_configuration.parsed_configuration['InfrastructureAccount']), 0)
        self.assertEqual(len(system_configuration.parsed_configuration['UnixInfrastructureAccount']), 2)
        self.assertEqual(len(system_configuration.parsed_configuration['AwsInfrastructureAccount']), 1)
        
        self.assertTrue('no-auth' in list(system_configuration.parsed_configuration['Authentication'].keys()), 'Found unexpected value in list: "{}"'.format(list(system_configuration.parsed_configuration['Authentication'].keys())))
        self.assertTrue('cd-user@host1.myorg' in list(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig'].keys()), 'Found unexpected value in list: "{}"'.format(list(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig'].keys())))
        self.assertTrue('accXYZ' in list(system_configuration.parsed_configuration['AwsProfileBasedAuthentication'].keys()), 'Found unexpected value in list: "{}"'.format(list(system_configuration.parsed_configuration['AwsProfileBasedAuthentication'].keys())))
        self.assertTrue('deployment-host' in list(system_configuration.parsed_configuration['UnixInfrastructureAccount'].keys()), 'Found unexpected value in list: "{}"'.format(list(system_configuration.parsed_configuration['UnixInfrastructureAccount'].keys())))
        self.assertTrue('host1' in list(system_configuration.parsed_configuration['UnixInfrastructureAccount'].keys()), 'Found unexpected value in list: "{}"'.format(list(system_configuration.parsed_configuration['UnixInfrastructureAccount'].keys())))
        self.assertTrue('sandbox-account' in list(system_configuration.parsed_configuration['AwsInfrastructureAccount'].keys()), 'Found unexpected value in list: "{}"'.format(list(system_configuration.parsed_configuration['AwsInfrastructureAccount'].keys())))

        self.assertIsInstance(system_configuration.parsed_configuration['Authentication']['no-auth'], Authentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['Authentication']['no-auth'], UnixHostAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['Authentication']['no-auth'], SshHostBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['Authentication']['no-auth'], SshCredentialsBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['Authentication']['no-auth'], SshPrivateKeyBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['Authentication']['no-auth'], AwsAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['Authentication']['no-auth'], AwsKeyBasedAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['Authentication']['no-auth'], AwsProfileBasedAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['Authentication']['no-auth'], InfrastructureAccount)
        self.assertNotIsInstance(system_configuration.parsed_configuration['Authentication']['no-auth'], UnixInfrastructureAccount)
        self.assertNotIsInstance(system_configuration.parsed_configuration['Authentication']['no-auth'], AwsInfrastructureAccount)

        self.assertIsInstance(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig']['cd-user@host1.myorg'], Authentication)
        self.assertIsInstance(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig']['cd-user@host1.myorg'], UnixHostAuthentication)
        self.assertIsInstance(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig']['cd-user@host1.myorg'], SshHostBasedAuthenticationConfig)
        self.assertIsInstance(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig']['cd-user@host1.myorg'], SshCredentialsBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig']['cd-user@host1.myorg'], SshPrivateKeyBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig']['cd-user@host1.myorg'], AwsAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig']['cd-user@host1.myorg'], AwsKeyBasedAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig']['cd-user@host1.myorg'], AwsProfileBasedAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig']['cd-user@host1.myorg'], InfrastructureAccount)
        self.assertNotIsInstance(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig']['cd-user@host1.myorg'], UnixInfrastructureAccount)
        self.assertNotIsInstance(system_configuration.parsed_configuration['SshCredentialsBasedAuthenticationConfig']['cd-user@host1.myorg'], AwsInfrastructureAccount)

        self.assertIsInstance(system_configuration.parsed_configuration['AwsProfileBasedAuthentication']['accXYZ'], Authentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsProfileBasedAuthentication']['accXYZ'], UnixHostAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsProfileBasedAuthentication']['accXYZ'], SshHostBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsProfileBasedAuthentication']['accXYZ'], SshCredentialsBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsProfileBasedAuthentication']['accXYZ'], SshPrivateKeyBasedAuthenticationConfig)
        self.assertIsInstance(system_configuration.parsed_configuration['AwsProfileBasedAuthentication']['accXYZ'], AwsAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsProfileBasedAuthentication']['accXYZ'], AwsKeyBasedAuthentication)
        self.assertIsInstance(system_configuration.parsed_configuration['AwsProfileBasedAuthentication']['accXYZ'], AwsProfileBasedAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsProfileBasedAuthentication']['accXYZ'], InfrastructureAccount)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsProfileBasedAuthentication']['accXYZ'], UnixInfrastructureAccount)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsProfileBasedAuthentication']['accXYZ'], AwsInfrastructureAccount)

        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['deployment-host'], Authentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['deployment-host'], UnixHostAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['deployment-host'], SshHostBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['deployment-host'], SshCredentialsBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['deployment-host'], SshPrivateKeyBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['deployment-host'], AwsAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['deployment-host'], AwsKeyBasedAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['deployment-host'], AwsProfileBasedAuthentication)
        self.assertIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['deployment-host'], InfrastructureAccount)
        self.assertIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['deployment-host'], UnixInfrastructureAccount)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['deployment-host'], AwsInfrastructureAccount)

        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['host1'], Authentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['host1'], UnixHostAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['host1'], SshHostBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['host1'], SshCredentialsBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['host1'], SshPrivateKeyBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['host1'], AwsAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['host1'], AwsKeyBasedAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['host1'], AwsProfileBasedAuthentication)
        self.assertIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['host1'], InfrastructureAccount)
        self.assertIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['host1'], UnixInfrastructureAccount)
        self.assertNotIsInstance(system_configuration.parsed_configuration['UnixInfrastructureAccount']['host1'], AwsInfrastructureAccount)

        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsInfrastructureAccount']['sandbox-account'], Authentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsInfrastructureAccount']['sandbox-account'], UnixHostAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsInfrastructureAccount']['sandbox-account'], SshHostBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsInfrastructureAccount']['sandbox-account'], SshCredentialsBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsInfrastructureAccount']['sandbox-account'], SshPrivateKeyBasedAuthenticationConfig)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsInfrastructureAccount']['sandbox-account'], AwsAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsInfrastructureAccount']['sandbox-account'], AwsKeyBasedAuthentication)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsInfrastructureAccount']['sandbox-account'], AwsProfileBasedAuthentication)
        self.assertIsInstance(system_configuration.parsed_configuration['AwsInfrastructureAccount']['sandbox-account'], InfrastructureAccount)
        self.assertNotIsInstance(system_configuration.parsed_configuration['AwsInfrastructureAccount']['sandbox-account'], UnixInfrastructureAccount)
        self.assertIsInstance(system_configuration.parsed_configuration['AwsInfrastructureAccount']['sandbox-account'], AwsInfrastructureAccount)

    def test_SystemConfigurations_create_classes_from_manifest_dump_back_as_yaml(self):
        system_configuration = SystemConfigurations()
        system_configuration.parse_yaml(raw_data=self.manifest_data)
        yaml_result = str(system_configuration)
        self.assertIsNotNone(yaml_result)
        self.assertIsInstance(yaml_result, str)
        self.assertTrue(len(yaml_result) > 10)
        print('='*80)
        print('# SystemConfigurations YAML')
        print(yaml_result)
        print('='*80)


class TestAllFunctions(unittest.TestCase):  # pragma: no cover

    def setUp(self):
        self.test_repo_https = 'https://github.com/nicc777/verba-cratis-test-infrastructure.git'

    def test_function_get_yaml_configuration_from_git_git_main_branch(self):
        sc = get_yaml_configuration_from_git(git_clone_url=self.test_repo_https)
        self.assertIsNotNone(sc)
        self.assertIsInstance(sc, SystemConfigurations)
        test_conf = sc.get_configuration_instance(class_type_name='AwsInfrastructureAccount', instance_name='sandbox-account')
        self.assertIsNotNone(test_conf)
        self.assertIsInstance(test_conf, AwsInfrastructureAccount)
        self.assertEqual(test_conf.account_name, 'sandbox-account')
        self.assertFalse('sandbox2' in test_conf.environments)


if __name__ == '__main__':
    unittest.main()
