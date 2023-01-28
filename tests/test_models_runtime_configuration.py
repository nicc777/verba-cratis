"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
import tempfile
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest


from verbacratis.models.runtime_configuration import *
from sqlalchemy.engine import Engine


class TestClassStateStore(unittest.TestCase):    # pragma: no cover

    def test_state_store_init_with_defaults(self):
        result = StateStore()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, StateStore)

    def test_state_store_get_connection_sqlite_memory(self):
        result = StateStore(connection_url='sqlite+pysqlite:///:memory:')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, StateStore)
        result.create_db_engine()
        self.assertTrue(result.enable_state)

    def test_state_store_get_connection_sqlite_invalid_url_disables_state(self):
        result = StateStore(connection_url='not-valid')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, StateStore)
        result.create_db_engine()
        self.assertFalse(result.enable_state)


class TestApplicationConfiguration(unittest.TestCase):    # pragma: no cover

    def test_application_configuration_init_with_defaults(self):
        result = ApplicationConfiguration()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, ApplicationConfiguration)


class TestProject(unittest.TestCase):    # pragma: no cover

    def test_project_init_with_defaults(self):
        result = Project(name='test')
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Project)
        self.assertTrue('default' in result.scopes)

    def test_project_init_with_defaults_dump_as_yaml(self):
        result = str(Project(name='test'))
        print('='*80)
        print('# Project YAML')
        print(result)
        print('='*80)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue('name: test' in result)
        self.assertTrue('environments:' in result)
        self.assertTrue('- name: default' in result)
        self.assertTrue('includeFileRegex:' in result)
        self.assertTrue('- \'*\.yml\'' in result)
        self.assertTrue('- \'*\.yaml\'' in result)

    def test_project_method_add_parent_project(self):
        project_parent = Project(name='test_parent')
        project_child1 = Project(name='test_child1')
        project_child1.add_parent_project(parent_project_name=project_parent.name)
        self.assertEqual(len(project_parent.parent_item_names), 0)
        self.assertEqual(len(project_child1.parent_item_names), 1)
        self.assertTrue('test_parent' in project_child1.parent_item_names)

    def test_project_method_add_manifest_directory(self):
        project = Project(name='test')
        project.add_manifest_directory(path='/tmp')
        
        self.assertEqual(len(project.manifest_directories), 1)
        
        directory = project.manifest_directories[0]
        self.assertIsInstance(directory, dict)
        self.assertTrue('path' in directory)
        self.assertTrue('type' in directory)
        self.assertEqual('/tmp', directory['path'])
        self.assertEqual('YAML', directory['type'])

        project.add_manifest_directory(path='/something/else', type='ABC')
        self.assertEqual(len(project.manifest_directories), 2)

        directory1 = project.manifest_directories[0]
        self.assertIsInstance(directory1, dict)
        self.assertTrue('path' in directory1)
        self.assertTrue('type' in directory1)
        self.assertEqual('/tmp', directory1['path'])
        self.assertEqual('YAML', directory1['type'])

        directory2 = project.manifest_directories[1]
        self.assertIsInstance(directory2, dict)
        self.assertTrue('path' in directory2)
        self.assertTrue('type' in directory2)
        self.assertEqual('/something/else', directory2['path'])
        self.assertEqual('ABC', directory2['type'])

    def test_project_method_override_include_file_regex(self):
        project = Project(name='test')
        project.override_include_file_regex(include_file_regex=('a', 'b', 'c'))
        self.assertIsNotNone(project.include_file_regex)
        self.assertIsInstance(project.include_file_regex, tuple)
        self.assertEqual(len(project.include_file_regex), 3)
        self.assertTrue('a' in project.include_file_regex)
        self.assertTrue('b' in project.include_file_regex)
        self.assertTrue('c' in project.include_file_regex)

    def test_project_method_add_manifest_file(self):
        project = Project(name='test')

        project.add_manifest_file(path='/tmp/file1.yaml')
        self.assertEqual(len(project.manifest_files), 1)
        file1 = project.manifest_files[0]
        self.assertIsInstance(file1, dict)
        self.assertTrue('path' in file1)
        self.assertTrue('type' in file1)
        self.assertEqual('/tmp/file1.yaml', file1['path'])
        self.assertEqual('YAML', file1['type'])

        project.add_manifest_file(path='/file2', type='ABC')
        self.assertEqual(len(project.manifest_files), 2)
        file2 = project.manifest_files[1]
        self.assertIsInstance(file2, dict)
        self.assertTrue('path' in file2)
        self.assertTrue('type' in file2)
        self.assertEqual('/file2', file2['path'])
        self.assertEqual('ABC', file2['type'])

    def test_project_method_get_environment_names_with_defaults(self):
        project = Project(name='test')
        envs = project.get_environment_names()
        self.assertIsInstance(envs, list)
        self.assertEqual(len(envs), 1)
        self.assertTrue('default' in envs)

    def test_project_method_get_environment_names_with_defaults_and_extra_environments(self):
        project = Project(name='test')
        project.add_environment(environment_name='dev')
        envs = project.get_environment_names()
        self.assertIsInstance(envs, list)
        self.assertEqual(len(envs), 1)
        self.assertTrue('dev' in envs)

        project.add_environment(environment_name='test')
        project.add_environment(environment_name='prod')

        envs = project.get_environment_names()
        self.assertIsInstance(envs, list)
        self.assertEqual(len(envs), 3)
        self.assertTrue('dev' in envs)
        self.assertTrue('test' in envs)
        self.assertTrue('prod' in envs)

    def test_project_method_as_dict(self):
        project = Project(name='test')
        project_parent = Project(name='test_parent')
        project.add_environment(environment_name='dev')
        project.add_environment(environment_name='test')
        project.add_manifest_directory(path='/tmp')
        project.add_manifest_file(path='/file')
        project.add_parent_item_name(parent_item_name=project_parent.name)

        project_as_dict = project.as_dict()['spec']
        self.assertIsNotNone(project_as_dict)
        self.assertIsInstance(project_as_dict, dict)
        self.assertTrue('includeFileRegex' in project_as_dict)
        self.assertTrue('locations' in project_as_dict)
        self.assertTrue('environments' in project_as_dict)
        self.assertTrue('parentProjects' in project_as_dict)

        result = str(project)
        print('='*80)
        print('# Project YAML')
        """
            environments:
            - name: dev
            - name: test
            includeFileRegex:
            - '*\.yml'
            - '*\.yaml'
            locations:
              directories:
              - path: /tmp
                type: YAML
              files:
              - path: /file
                type: YAML
            parentProjects:
            - name: test_parent
        """
        print(result)
        print('='*80)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue('environments:' in result)
        self.assertTrue('- name: dev' in result)
        self.assertTrue('- name: test' in result)
        self.assertTrue('includeFileRegex:' in result)
        self.assertTrue('- \'*\.yml\'' in result)
        self.assertTrue('- \'*\.yaml\'' in result)
        self.assertTrue('locations:' in result)        
        self.assertTrue('directories:' in result)
        self.assertTrue('- path: /tmp' in result)
        self.assertTrue('  type: YAML' in result)
        self.assertTrue('files:' in result)
        self.assertTrue('- path: /file' in result)
        self.assertTrue('  type: YAML' in result)
        self.assertTrue('parentProjects' in result)
        self.assertTrue('- name: test_parent' in result)


class TestProjects(unittest.TestCase):    # pragma: no cover

    def test_projects_init_with_defaults(self):
        result = Projects()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Projects)

    def test_projects_add_2_projects(self):
        p1 = Project(name='proj01', use_default_scope=False)
        p2 = Project(name='proj02', use_default_scope=False)

        p1.add_environment(environment_name='dev')
        p1.add_environment(environment_name='test')
        p1.add_environment(environment_name='prod')

        p2.add_environment(environment_name='dev')
        p2.add_environment(environment_name='test')

        p1.add_parent_item_name(parent_item_name=p2.name)

        projects = Projects()
        projects.add_project(project=p1)
        projects.add_project(project=p2)

        self.assertIsNotNone(projects)
        self.assertIsInstance(projects, Projects)

    def test_projects_method_get_project_names_for_named_environment(self):
        p1 = Project(name='proj01', use_default_scope=False)
        p2 = Project(name='proj02', use_default_scope=False)

        p1.add_environment(environment_name='dev')
        p1.add_environment(environment_name='test')
        p1.add_environment(environment_name='prod')

        p2.add_environment(environment_name='dev')
        p2.add_environment(environment_name='test')

        p1.add_parent_item_name(parent_item_name=p2.name)

        projects = Projects()
        projects.add_project(project=p1)
        projects.add_project(project=p2)

        dev_env_project_names = projects.get_project_names_for_named_environment(environment_name='dev')
        self.assertIsNotNone(dev_env_project_names)
        self.assertIsInstance(dev_env_project_names, list)
        self.assertEqual(len(dev_env_project_names), 2)
        self.assertTrue('proj01' in dev_env_project_names)
        self.assertTrue('proj02' in dev_env_project_names)

        test_env_project_names = projects.get_project_names_for_named_environment(environment_name='test')
        self.assertIsNotNone(test_env_project_names)
        self.assertIsInstance(test_env_project_names, list)
        self.assertEqual(len(test_env_project_names), 2)
        self.assertTrue('proj01' in test_env_project_names)
        self.assertTrue('proj02' in test_env_project_names)

        prod_env_project_names = projects.get_project_names_for_named_environment(environment_name='prod')
        self.assertIsNotNone(prod_env_project_names)
        self.assertIsInstance(prod_env_project_names, list)
        self.assertEqual(len(prod_env_project_names), 1)
        self.assertTrue('proj01' in prod_env_project_names)

    def test_projects_method_get_project_names_for_named_environment_with_incorrect_environment_name_throwing_exception(self):
        p1 = Project(name='proj01', use_default_scope=False)
        p2 = Project(name='proj02', use_default_scope=False)

        p1.add_environment(environment_name='dev')
        p1.add_environment(environment_name='test')
        p1.add_environment(environment_name='prod')

        p2.add_environment(environment_name='dev')
        p2.add_environment(environment_name='test')

        p1.add_parent_item_name(parent_item_name=p2.name)

        projects = Projects()
        projects.add_project(project=p1)
        projects.add_project(project=p2)

        with self.assertRaises(Exception) as context:
            projects.get_project_names_for_named_environment(environment_name='i-dont-exist')
        self.assertTrue('Environment named "i-dont-exist" not found in collection of projects' in str(context.exception))
    
    def test_projects_method_get_project_by_name(self):
        p1 = Project(name='proj01', use_default_scope=False)
        p2 = Project(name='proj02', use_default_scope=False)

        p1.add_environment(environment_name='dev')
        p1.add_environment(environment_name='test')
        p1.add_environment(environment_name='prod')

        p2.add_environment(environment_name='dev')
        p2.add_environment(environment_name='test')

        p1.add_parent_item_name(parent_item_name=p2.name)

        projects = Projects()
        projects.add_project(project=p1)
        projects.add_project(project=p2)

        p_test = projects.get_project_by_name(project_name='proj01')
        self.assertEqual(p1, p_test)

    def test_projects_method_to_string(self):
        p1 = Project(name='proj01', use_default_scope=False)
        p2 = Project(name='proj02', use_default_scope=False)

        p1.add_environment(environment_name='dev')
        p1.add_environment(environment_name='test')
        p1.add_environment(environment_name='prod')

        p2.add_environment(environment_name='dev')
        p2.add_environment(environment_name='test')

        p1.add_parent_item_name(parent_item_name=p2.name)

        projects = Projects()
        projects.add_project(project=p1)
        projects.add_project(project=p2)

        projects_yaml = str(projects)
        self.assertIsNotNone(projects_yaml)
        self.assertIsInstance(projects_yaml, str)
        self.assertTrue(len(projects_yaml) > 10)
        self.assertTrue('---' in projects_yaml)
        print('='*80)
        print('# Projects YAML')
        print(projects_yaml)
        print('='*80)


class TestUnixHostAuthentication(unittest.TestCase):    # pragma: no cover

    def test_unix_host_authentication_init_with_defaults(self):
        result = UnixHostAuthentication(hostname='example.tld')
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


if __name__ == '__main__':
    unittest.main()
