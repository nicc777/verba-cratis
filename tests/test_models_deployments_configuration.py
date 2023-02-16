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

    def setUp(self):
        self.dir_for_test_files = create_tmp_dir(sub_dir='test_files')
        self.file1 = create_tmp_file(tmp_dir=self.dir_for_test_files, file_name='file1.yaml', data='---\ntest1: true')
        self.file2 = create_tmp_file(tmp_dir=self.dir_for_test_files, file_name='file2.yaml', data='---\ntest2: true')
        self.dir_for_local_dir_location = create_tmp_dir(sub_dir='test_single_local_file')
        local_dir_data = """---
apiVersion: v1-alpha
kind: LocalDirectoryManifestLocation
metadata:
  name: local_dir_test_1
spec:
  location: {}""".format(self.dir_for_test_files)
        self.local_dir_data_manifest = create_tmp_file(tmp_dir=self.dir_for_local_dir_location, file_name='manifest.yaml', data=local_dir_data)
        self.loc = LocalDirectoryManifestLocation(reference=self.dir_for_test_files, manifest_name='local_dir_test_1')
        self.project_manifest_example = """---
apiVersion: v1-alpha
kind: LocalDirectoryManifestLocation
metadata:
  name: local_dir_test_1
spec:
  include_file_regex: .*\.yml|.*\.yaml
  location: /tmp/test_files
---
apiVersion: v1-alpha
kind: Project
metadata:
  environments:
  - default
  name: test
spec:
  locations:
  - local_dir_test_1"""
        self.projects = list()

    def tearDown(self):
        for project in self.projects:
            for loc in project.locations:
                loc.cleanup_work_dir()
        remove_tmp_dir_recursively(dir=self.dir_for_test_files)
        remove_tmp_dir_recursively(dir=self.dir_for_local_dir_location)

    def test_project_init_with_defaults(self):
        project = Project(name='test')
        self.assertIsNotNone(project)
        self.assertIsInstance(project, Project)
        self.assertTrue('default' in project.scopes)
        self.assertEqual(len(project.locations), 0)
        self.projects.append(project)

    def test_project_init_with_defaults_dump_as_yaml(self):
        project = Project(name='test')
        result = str(project)
        print('='*80)
        print('# Project YAML')
        print(result)
        print('='*80)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue('name: test' in result)
        self.assertTrue('environments:' in result)
        self.assertTrue('- default' in result)
        self.assertFalse('locations' in result)
        self.projects.append(project)

    def test_project_method_add_parent_project(self):
        project_parent = Project(name='test_parent')
        project_child1 = Project(name='test_child1')
        project_child1.add_parent_project(parent_project_name=project_parent.name)
        self.assertEqual(len(project_parent.parent_item_names), 0)
        self.assertEqual(len(project_child1.parent_item_names), 1)
        self.assertTrue('test_parent' in project_child1.parent_item_names)
        self.projects.append(project_parent)
        self.projects.append(project_child1)

    def test_project_method_add_manifest_directory(self):
        project = Project(name='test')
        project.add_manifest_location(location=self.loc)
        self.assertEqual(len(project.locations), 1)
        result = str(project)
        print('='*80)
        print('# Project YAML')
        print(result)
        print('='*80)
        self.assertIsNotNone(result)
        self.assertIsInstance(result, str)
        self.assertTrue('name: test' in result)
        self.assertTrue('environments:' in result)
        self.assertTrue('- default' in result)
        self.assertTrue('locations' in result)
        self.projects.append(project)
        

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
        project.add_manifest_location(location=self.loc)
        project_parent = Project(name='test_parent')
        project.add_environment(environment_name='dev')
        project.add_environment(environment_name='test')
        project.add_parent_item_name(parent_item_name=project_parent.name)

        project_as_dict = project.as_dict()['spec']
        self.assertIsNotNone(project_as_dict)
        self.assertIsInstance(project_as_dict, dict)
        self.assertTrue('locations' in project_as_dict)
        self.assertTrue('parentProjects' in project_as_dict)

    def test_project_method_as_dict_only_files_no_parent(self):
        project = Project(name='test')
        project.add_manifest_location(location=self.loc)
        project.add_environment(environment_name='dev')
        project.add_environment(environment_name='test')

        project_as_dict = project.as_dict()['spec']
        self.assertIsNotNone(project_as_dict)
        self.assertIsInstance(project_as_dict, dict)
        self.assertTrue('locations' in project_as_dict)
        self.assertFalse('parentProjects' in project_as_dict)


class TestProjects(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        self.test_projects_git_https = 'https://raw.githubusercontent.com/nicc777/verba-cratis-test-projects/main/project-hello-world.yaml'
        self.test_project_tmp_dir = create_tmp_dir(sub_dir='test-project')
        self.local_docker_install_project = create_tmp_dir(sub_dir='local-docker-install')
        self.hello_world_project = create_tmp_dir(sub_dir='sample-docker-app')

    def tearDown(self):
        remove_tmp_dir_recursively(dir=self.local_docker_install_project)
        remove_tmp_dir_recursively(dir=self.hello_world_project)
        remove_tmp_dir_recursively(dir=self.test_project_tmp_dir)

    def test_projects_init_with_defaults(self):
        result = Projects()
        self.assertIsNotNone(result)
        self.assertIsInstance(result, Projects)

    def test_projects_init_with_test_projects(self):
        files = download_files(urls=[self.test_projects_git_https,], target_dir=self.test_project_tmp_dir)
        self.assertIsNotNone(files)
        self.assertIsInstance(files, list)
        self.assertEqual(len(files), 1)
        for file in files:
            self.assertTrue(self.test_project_tmp_dir in file)
            self.assertTrue(len(file) > len(self.test_project_tmp_dir))
        projects = get_project_from_files(files=files)
        self.assertIsNotNone(projects)
        self.assertIsInstance(projects, Projects)
        

#     def test_projects_add_2_projects(self):
#         p1 = Project(name='proj01', use_default_scope=False)
#         p2 = Project(name='proj02', use_default_scope=False)

#         p1.add_environment(environment_name='dev')
#         p1.add_environment(environment_name='test')
#         p1.add_environment(environment_name='prod')

#         p2.add_environment(environment_name='dev')
#         p2.add_environment(environment_name='test')

#         p1.add_parent_item_name(parent_item_name=p2.name)

#         projects = Projects()
#         projects.add_project(project=p1)
#         projects.add_project(project=p2)

#         self.assertIsNotNone(projects)
#         self.assertIsInstance(projects, Projects)

#     def test_projects_method_get_project_names_for_named_environment(self):
#         p1 = Project(name='proj01', use_default_scope=False)
#         p2 = Project(name='proj02', use_default_scope=False)

#         p1.add_environment(environment_name='dev')
#         p1.add_environment(environment_name='test')
#         p1.add_environment(environment_name='prod')

#         p2.add_environment(environment_name='dev')
#         p2.add_environment(environment_name='test')

#         p1.add_parent_item_name(parent_item_name=p2.name)

#         projects = Projects()
#         projects.add_project(project=p1)
#         projects.add_project(project=p2)

#         dev_env_project_names = projects.get_project_names_for_named_environment(environment_name='dev')
#         self.assertIsNotNone(dev_env_project_names)
#         self.assertIsInstance(dev_env_project_names, list)
#         self.assertEqual(len(dev_env_project_names), 2)
#         self.assertTrue('proj01' in dev_env_project_names)
#         self.assertTrue('proj02' in dev_env_project_names)

#         test_env_project_names = projects.get_project_names_for_named_environment(environment_name='test')
#         self.assertIsNotNone(test_env_project_names)
#         self.assertIsInstance(test_env_project_names, list)
#         self.assertEqual(len(test_env_project_names), 2)
#         self.assertTrue('proj01' in test_env_project_names)
#         self.assertTrue('proj02' in test_env_project_names)

#         prod_env_project_names = projects.get_project_names_for_named_environment(environment_name='prod')
#         self.assertIsNotNone(prod_env_project_names)
#         self.assertIsInstance(prod_env_project_names, list)
#         self.assertEqual(len(prod_env_project_names), 1)
#         self.assertTrue('proj01' in prod_env_project_names)

#     def test_projects_method_get_project_names_for_named_environment_with_incorrect_environment_name_throwing_exception(self):
#         p1 = Project(name='proj01', use_default_scope=False)
#         p2 = Project(name='proj02', use_default_scope=False)

#         p1.add_environment(environment_name='dev')
#         p1.add_environment(environment_name='test')
#         p1.add_environment(environment_name='prod')

#         p2.add_environment(environment_name='dev')
#         p2.add_environment(environment_name='test')

#         p1.add_parent_item_name(parent_item_name=p2.name)

#         projects = Projects()
#         projects.add_project(project=p1)
#         projects.add_project(project=p2)

#         with self.assertRaises(Exception) as context:
#             projects.get_project_names_for_named_environment(environment_name='i-dont-exist')
#         self.assertTrue('Environment named "i-dont-exist" not found in collection of projects' in str(context.exception))
    
#     def test_projects_method_get_project_by_name(self):
#         p1 = Project(name='proj01', use_default_scope=False)
#         p2 = Project(name='proj02', use_default_scope=False)

#         p1.add_environment(environment_name='dev')
#         p1.add_environment(environment_name='test')
#         p1.add_environment(environment_name='prod')

#         p2.add_environment(environment_name='dev')
#         p2.add_environment(environment_name='test')

#         p1.add_parent_item_name(parent_item_name=p2.name)

#         projects = Projects()
#         projects.add_project(project=p1)
#         projects.add_project(project=p2)

#         p_test = projects.get_project_by_name(project_name='proj01')
#         self.assertEqual(p1, p_test)

#     def test_projects_method_to_string(self):
#         p1 = Project(name='proj01', use_default_scope=False)
#         p2 = Project(name='proj02', use_default_scope=False)

#         p1.add_environment(environment_name='dev')
#         p1.add_environment(environment_name='test')
#         p1.add_environment(environment_name='prod')

#         p2.add_environment(environment_name='dev')
#         p2.add_environment(environment_name='test')

#         p1.add_parent_item_name(parent_item_name=p2.name)

#         projects = Projects()
#         projects.add_project(project=p1)
#         projects.add_project(project=p2)

#         projects_yaml = str(projects)
#         self.assertIsNotNone(projects_yaml)
#         self.assertIsInstance(projects_yaml, str)
#         self.assertTrue(len(projects_yaml) > 10)
#         self.assertTrue('---' in projects_yaml)
#         print('='*80)
#         print('# Projects YAML')
#         print(projects_yaml)
#         print('='*80)


class TestLocationClasses(unittest.TestCase):    # pragma: no cover

    def setUp(self):
        self.dir_for_test_files = create_tmp_dir(sub_dir='test_files')
        self.file1 = create_tmp_file(tmp_dir=self.dir_for_test_files, file_name='file1.yaml', data='---\ntest1: true')
        self.file2 = create_tmp_file(tmp_dir=self.dir_for_test_files, file_name='file2.yaml', data='---\ntest2: true')
        self.file_at_url = 'https://raw.githubusercontent.com/nicc777/verba-cratis-test-projects/main/project-hello-world.yaml'
        self.git_ssh = 'git@github.com:nicc777/verba-cratis-test-projects.git'
        self.git_http = 'https://github.com/nicc777/verba-cratis-test-projects.git'
        
        self.local_file_manifest_location = create_tmp_dir(sub_dir='test_single_local_file')
        local_file_data = """---
apiVersion: v1-alpha
kind: LocalFileManifestLocation
metadata:
  name: local_file_test_1
spec:
  location: {}""".format(self.file1)
        self.local_file_manifest = create_tmp_file(tmp_dir=self.local_file_manifest_location, file_name='manifest.yaml', data=local_file_data)

        self.dir_for_local_dir_location = create_tmp_dir(sub_dir='test_single_local_file')
        local_dir_data = """---
apiVersion: v1-alpha
kind: LocalDirectoryManifestLocation
metadata:
  name: local_dir_test_1
spec:
  location: {}""".format(self.dir_for_test_files)
        self.local_dir_data_manifest = create_tmp_file(tmp_dir=self.dir_for_local_dir_location, file_name='manifest.yaml', data=local_dir_data)

        self.dir_for_file_url_location = create_tmp_dir(sub_dir='test_file_url_file')
        local_dir_data = """---
apiVersion: v1-alpha
kind: FileUrlManifestLocation
metadata:
  name: file_url_test_1
spec:
  location: {}
  set_no_verify_ssl: true""".format(self.file_at_url)
        self.local_dir_data_manifest = create_tmp_file(tmp_dir=self.dir_for_file_url_location, file_name='manifest.yaml', data=local_dir_data)
        

    def tearDown(self):
        remove_tmp_dir_recursively(dir=self.dir_for_test_files)
        remove_tmp_dir_recursively(dir=self.local_file_manifest_location)
        remove_tmp_dir_recursively(dir=self.dir_for_file_url_location)

    def _verify_init(self, loc: ManifestLocation):
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
        # self.assertTrue(data.startswith('---'))

    def _verify_cleanup(self, loc: ManifestLocation):
        files = copy.deepcopy(loc.files)
        loc.cleanup_work_dir()
        for file in files:
            self.assertFalse(does_file_exists(data_value=file))
        self.assertEqual(len(loc.files), 0)

    def _verify_as_dict(self, data: dict, expected_keys:tuple):
        self.assertTrue('spec' in data)
        for key in expected_keys:
            self.assertTrue(key in data['spec'])
        self.assertEqual(len(data['spec']), len(expected_keys))

    def test_class_LocalFileManifestLocation_basic(self):
        loc = LocalFileManifestLocation(reference=self.file1, manifest_name='local_file_test_1')
        self.assertIsNotNone(loc)
        self.assertIsInstance(loc, ManifestLocation)
        self.assertIsInstance(loc, LocalFileManifestLocation)
        self.assertNotIsInstance(loc, LocalDirectoryManifestLocation)
        self.assertNotIsInstance(loc, FileUrlManifestLocation)
        self.assertNotIsInstance(loc, GitManifestLocation)

        location_yaml = str(loc)
        self.assertIsNotNone(location_yaml)
        self.assertIsInstance(location_yaml, str)
        self.assertTrue(len(location_yaml) > 10)
        print('='*80)
        print('# LocalFileManifestLocation YAML')
        print(location_yaml)
        print('='*80)

        self.assertEqual(loc.location_type, LocationType.LOCAL_FILE)
        self._verify_init(loc=loc)
        self.assertEqual(len(loc.files),1)
        for work_file in loc.files:
            print('work file: {}'.format(work_file))
            self._verify_file_exists_and_has_content(work_file=work_file)
        self._verify_as_dict(data=loc.as_dict(), expected_keys=('location',))
        self._verify_cleanup(loc=loc)

    def test_class_LocalDirectoryManifestLocation_basic(self):
        loc = LocalDirectoryManifestLocation(reference=self.dir_for_test_files, manifest_name='local_dir_test_1')
        self.assertIsNotNone(loc)
        self.assertIsInstance(loc, ManifestLocation)
        self.assertIsInstance(loc, LocalDirectoryManifestLocation)
        self.assertNotIsInstance(loc, FileUrlManifestLocation)
        self.assertNotIsInstance(loc, LocalFileManifestLocation)
        self.assertNotIsInstance(loc, GitManifestLocation)

        location_yaml = str(loc)
        self.assertIsNotNone(location_yaml)
        self.assertIsInstance(location_yaml, str)
        self.assertTrue(len(location_yaml) > 10)
        print('='*80)
        print('# LocalDirectoryManifestLocation YAML')
        print(location_yaml)
        print('='*80)

        self.assertEqual(loc.location_type, LocationType.LOCAL_DIRECTORY)
        self._verify_init(loc=loc)
        self.assertEqual(len(loc.files),2)
        for work_file in loc.files:
            print('work file: {}'.format(work_file))
            self._verify_file_exists_and_has_content(work_file=work_file)
        self._verify_as_dict(data=loc.as_dict(), expected_keys=('location', 'include_file_regex',))
        self._verify_cleanup(loc=loc)

    def test_class_FileUrlManifestLocation_basic(self):
        loc = FileUrlManifestLocation(reference=self.file_at_url, manifest_name='file_url_test_1')
        self.assertIsNotNone(loc)
        self.assertIsInstance(loc, ManifestLocation)
        self.assertIsInstance(loc, FileUrlManifestLocation)
        self.assertNotIsInstance(loc, LocalDirectoryManifestLocation)
        self.assertNotIsInstance(loc, LocalFileManifestLocation)
        self.assertNotIsInstance(loc, GitManifestLocation)

        location_yaml = str(loc)
        self.assertIsNotNone(location_yaml)
        self.assertIsInstance(location_yaml, str)
        self.assertTrue(len(location_yaml) > 10)
        print('='*80)
        print('# FileUrlManifestLocation YAML')
        print(location_yaml)
        print('='*80)

        self.assertEqual(loc.location_type, LocationType.FILE_URL)
        self._verify_init(loc=loc)
        self.assertEqual(len(loc.files),1)
        for work_file in loc.files:
            print('work file: {}'.format(work_file))
            self._verify_file_exists_and_has_content(work_file=work_file)
        self._verify_as_dict(data=loc.as_dict(), expected_keys=('location', 'set_no_verify_ssl',))
        self._verify_cleanup(loc=loc)

    def test_class_GitManifestLocation_ssh(self):
        loc = GitManifestLocation(
            reference=self.git_ssh,
            manifest_name='git_ssh_test_1',
            branch='main'
        )
        self.assertIsNotNone(loc)
        self.assertIsInstance(loc, ManifestLocation)
        self.assertIsInstance(loc, GitManifestLocation)
        self.assertNotIsInstance(loc, FileUrlManifestLocation)
        self.assertNotIsInstance(loc, LocalDirectoryManifestLocation)
        self.assertNotIsInstance(loc, LocalFileManifestLocation)

        location_yaml = str(loc)
        self.assertIsNotNone(location_yaml)
        self.assertIsInstance(location_yaml, str)
        self.assertTrue(len(location_yaml) > 10)
        print('='*80)
        print('# GitManifestLocation YAML')
        print(location_yaml)
        print('='*80)

        self.assertEqual(loc.location_type, LocationType.GIT_URL)
        self._verify_init(loc=loc)
        self.assertEqual(len(loc.files),1)
        for work_file in loc.files:
            print('work file: {}'.format(work_file))
            self._verify_file_exists_and_has_content(work_file=work_file)
        self._verify_as_dict(data=loc.as_dict(), expected_keys=('location', 'include_file_regex', 'branch', 'relative_start_directory', ))
        self._verify_cleanup(loc=loc)

    def test_class_GitManifestLocation_http_no_ssl_verify(self):
        loc = GitManifestLocation(
            reference=self.git_http,
            manifest_name='git_http_test_1',
            branch='main',
            set_no_verify_ssl=True
        )
        self.assertIsNotNone(loc)
        self.assertIsInstance(loc, ManifestLocation)
        self.assertIsInstance(loc, GitManifestLocation)
        self.assertNotIsInstance(loc, FileUrlManifestLocation)
        self.assertNotIsInstance(loc, LocalDirectoryManifestLocation)
        self.assertNotIsInstance(loc, LocalFileManifestLocation)

        location_yaml = str(loc)
        self.assertIsNotNone(location_yaml)
        self.assertIsInstance(location_yaml, str)
        self.assertTrue(len(location_yaml) > 10)
        print('='*80)
        print('# GitManifestLocation YAML')
        print(location_yaml)
        print('='*80)

        self.assertEqual(loc.location_type, LocationType.GIT_URL)
        self._verify_init(loc=loc)
        self.assertEqual(len(loc.files),1)
        for work_file in loc.files:
            print('work file: {}'.format(work_file))
            self._verify_file_exists_and_has_content(work_file=work_file)
        self._verify_as_dict(data=loc.as_dict(), expected_keys=('location', 'include_file_regex', 'branch', 'relative_start_directory', 'set_no_verify_ssl', ))
        self._verify_cleanup(loc=loc)


if __name__ == '__main__':
    unittest.main()