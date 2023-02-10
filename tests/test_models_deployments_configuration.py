"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.realpath(__file__)) + "/../src")
print('sys.path={}'.format(sys.path))

import unittest


from verbacratis.models.deployments_configuration import *
from verbacratis.utils.file_io import *
import copy


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
        self.assertTrue('- default' in result)
        self.assertTrue('includeFileRegex:' in result)
        self.assertTrue('.yml' in result)
        self.assertTrue('.yaml' in result)

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
        project.add_manifest_directory(path='/tmp2')
        project.add_manifest_file(path='/file')
        project.add_parent_item_name(parent_item_name=project_parent.name)

        project_as_dict = project.as_dict()['spec']
        self.assertIsNotNone(project_as_dict)
        self.assertIsInstance(project_as_dict, dict)
        self.assertTrue('includeFileRegex' in project_as_dict)
        self.assertTrue('locations' in project_as_dict)
        self.assertTrue('parentProjects' in project_as_dict)

        result = str(project)
        print('='*80)
        print('# Project YAML')
        print(result)
        print('='*80)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue('includeFileRegex:' in result)
        self.assertTrue('.yml' in result)
        self.assertTrue('.*\.yaml' in result)
        self.assertTrue('locations:' in result)        
        self.assertTrue('directories:' in result)
        self.assertTrue('- path: /tmp' in result)
        self.assertTrue('  type: YAML' in result)
        self.assertTrue('files:' in result)
        self.assertTrue('- path: /file' in result)
        self.assertTrue('  type: YAML' in result)
        self.assertTrue('parentProjects' in result)
        self.assertTrue('- name: test_parent' in result)


    def test_project_method_as_dict_only_files_no_parent(self):
        project = Project(name='test')
        project.add_environment(environment_name='dev')
        project.add_environment(environment_name='test')
        project.add_manifest_file(path='/file')

        project_as_dict = project.as_dict()['spec']
        self.assertIsNotNone(project_as_dict)
        self.assertIsInstance(project_as_dict, dict)
        self.assertTrue('includeFileRegex' in project_as_dict)
        self.assertTrue('locations' in project_as_dict)

        result = str(project)
        print('='*80)
        print('# Project YAML')
        print(result)
        print('='*80)


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


class TestLocation(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        self.dir_for_test_files = create_tmp_dir(sub_dir='test_files')
        self.file1 = create_tmp_file(tmp_dir=self.dir_for_test_files, file_name='file1.yaml', data='---\ntest1: true')
        self.file2 = create_tmp_file(tmp_dir=self.dir_for_test_files, file_name='file2.yaml', data='---\ntest2: true')
        self.git_repo = 'https://github.com/nicc777/verba-cratis-test-projects.git%00branch%3Dmain'
        self.file_at_url = 'https://raw.githubusercontent.com/nicc777/verba-cratis-test-projects/main/project-hello-world.yaml'

    def tearDown(self):
        remove_tmp_dir_recursively(dir=self.dir_for_test_files)

    def _verify_init(self, loc: Location):
        self.assertIsNotNone(loc.work_dir)
        self.assertIsInstance(loc.work_dir, str)
        self.assertTrue(len(loc.work_dir) > 0)

        self.assertIsNotNone(loc.checksum)
        self.assertIsInstance(loc.checksum, str)
        self.assertTrue(len(loc.checksum) > 0)
        
        self.assertIsNotNone(loc.files)
        self.assertIsInstance(loc.files, list)
        self.assertTrue(len(loc.files) > 0)

    def _verify_file_exists_and_has_content(self, work_file: str):
        data = ''
        with open(work_file, 'r') as f:
            data = f.read()
        self.assertIsNotNone(data)
        self.assertIsInstance(data, str)
        self.assertTrue(len(data) > 0)
        self.assertTrue(data.startswith('---'))

    def _verify_cleanup(self, loc: Location):
        files = copy.deepcopy(loc.files)
        loc.cleanup_work_dir()
        for file in files:
            self.assertFalse(does_file_exists(data_value=file))

    def test_location_init_with_local_dir_of_files(self):
        loc = Location(reference=self.dir_for_test_files)
        self.assertIsNotNone(loc)
        self.assertIsInstance(loc, Location)
        self._verify_init(loc=loc)
        self.assertEqual(len(loc.files),2)
        for work_file in loc.files:
            print('work file: {}'.format(work_file))
            self._verify_file_exists_and_has_content(work_file=work_file)
        self._verify_cleanup(loc=loc)

    def test_location_init_with_local_file(self):
        loc = Location(reference=self.file1)
        self.assertIsNotNone(loc)
        self.assertIsInstance(loc, Location)
        self._verify_init(loc=loc)
        self.assertEqual(len(loc.files),1)
        for work_file in loc.files:
            print('work file: {}'.format(work_file))
            self._verify_file_exists_and_has_content(work_file=work_file)
        self._verify_cleanup(loc=loc)

    def test_location_init_with_http_file(self):
        loc = Location(reference=self.file_at_url)
        self.assertIsNotNone(loc)
        self.assertIsInstance(loc, Location)
        self._verify_init(loc=loc)
        self.assertEqual(len(loc.files),1)
        for work_file in loc.files:
            print('work file: {}'.format(work_file))
            self._verify_file_exists_and_has_content(work_file=work_file)
        self._verify_cleanup(loc=loc)

    def test_location_init_with_git(self):
        loc = Location(reference=self.git_repo)
        self.assertIsNotNone(loc)
        self.assertIsInstance(loc, Location)
        self._verify_init(loc=loc)
        self.assertEqual(len(loc.files),1)
        for work_file in loc.files:
            print('work file: {}'.format(work_file))
            self._verify_file_exists_and_has_content(work_file=work_file)
        self._verify_cleanup(loc=loc)


if __name__ == '__main__':
    unittest.main()