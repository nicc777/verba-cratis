"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import yaml
import hashlib
import os
from verbacratis.models import GenericLogger
from verbacratis.models.ordering import Item, Items
from verbacratis.utils.file_io import PathTypes, identify_local_path_type, create_tmp_dir, remove_tmp_dir_recursively, copy_file, get_file_from_path, file_checksum, find_matching_files
from verbacratis.utils.git_integration import is_url_a_git_repo, git_clone_checkout_and_return_list_of_files, extract_parameters_from_url
from verbacratis.utils.http_requests_io import download_files


class LocationType:
    LOCAL_DIRECTORY = 1
    LOCAL_FILE = 2
    FILE_URL = 3
    GIT_URL = 4
    types = range(1,5)

    def exportable_names_to_class_values_map(self):
        return {
            'LocalDirectory': self.LOCAL_DIRECTORY,
            'LocalFile': self.LOCAL_FILE,
            'FileURL': self.FILE_URL,
            'GitUrl': self.GIT_URL,
        }

    def class_values_to_exportable_names_map(self):
        return {
            self.LOCAL_DIRECTORY: 'LocalDirectory',
            self.LOCAL_FILE: 'LocalFile',
            self.FILE_URL: 'FileURL',
            self.GIT_URL: 'GitUrl',
        }


LOCATION_KIND_MAP = {
    1: 'LocalDirectoryManifestLocation',
    2: 'LocalFileManifestLocation',
    3: 'FileUrlManifestLocation',
    4: 'GitManifestLocation',
}


class ManifestLocation:

    def __init__(
        self,
        reference: str,
        manifest_name: str,
        include_file_regex: str='.*\.yml|.*\.yaml',
        set_no_verify_ssl: bool=False,
        branch: str='main',
        relative_start_directory: str='/',
        ssh_private_key_path: str=None
    ):
        self.manifest_name = manifest_name
        self.reference = reference
        self.files = list()
        self.work_dir = None
        self.checksum = None
        self.location_type = None

        # Directory and Git Specific
        self.include_file_regex = include_file_regex

        # File URL Specific
        self.set_no_verify_ssl = set_no_verify_ssl

        # Git Specific
        self.branch = branch
        self.relative_start_directory = relative_start_directory
        self.ssh_private_key_path = ssh_private_key_path

    def _update_checksum_from_work_dir_files(self)->str:
        raw_string = ''
        for file in self.files:
            raw_string = '{}{}\n'.format(raw_string, file_checksum(path=file))
        self.checksum = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()

    def cleanup_work_dir(self):
        remove_tmp_dir_recursively(dir=self.work_dir)
        self.files = list()
        self.work_dir = None

    def get_files(self)->list:
        raise Exception('Implement in ManifestLocation sub-classes')

    def sync(self):
        self.cleanup_work_dir()
        self.work_dir = create_tmp_dir(sub_dir='Location__{}'.format(hashlib.sha256(self.reference.encode('utf-8')).hexdigest()))
        self.get_files()
        self._update_checksum_from_work_dir_files()

    def as_dict(self):
        root = dict()
        root['spec'] = dict()
        root['spec']['location'] = self.reference
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = LOCATION_KIND_MAP[self.location_type]
        root['metadata'] = dict()
        root['metadata']['name'] = self.manifest_name
        if self.location_type == LocationType.LOCAL_DIRECTORY or self.location_type == LocationType.GIT_URL:
            root['spec']['include_file_regex'] = self.include_file_regex
        if self.location_type == LocationType.FILE_URL:
            root['spec']['set_no_verify_ssl'] = self.set_no_verify_ssl
        if self.location_type == LocationType.GIT_URL:
            if self.reference.lower().startswith('http'):
                root['spec']['set_no_verify_ssl'] = self.set_no_verify_ssl
        if self.location_type == LocationType.GIT_URL:
            root['spec']['branch'] = self.branch
            root['spec']['relative_start_directory'] = self.relative_start_directory
            if self.ssh_private_key_path is not None:
                root['spec']['ssh_private_key_path'] = self.ssh_private_key_path
        return root

    def __str__(self)->str:
        return yaml.dump(self.as_dict())


class LocalFileManifestLocation(ManifestLocation):

    def __init__(self, reference: str, manifest_name: str):
        super().__init__(reference, manifest_name)
        self.location_type = LocationType.LOCAL_FILE
        self.sync()

    def get_files(self)->list:
        self.files.append(copy_file(source_file=self.reference, file_name=get_file_from_path(input_path=self.reference), tmp_dir=self.work_dir))


class LocalDirectoryManifestLocation(ManifestLocation):

    def __init__(self, reference: str, manifest_name: str, include_file_regex: str='.*\.yml|.*\.yaml'):
        super().__init__(reference, manifest_name, include_file_regex)
        self.location_type = LocationType.LOCAL_DIRECTORY
        self.sync()

    def get_files(self)->list:
        for file in find_matching_files(start_dir=self.reference, pattern=self.include_file_regex):
            self.files.append(
                copy_file(
                    source_file=file,
                    file_name=hashlib.sha256(file.encode('utf-8')).hexdigest(),
                    tmp_dir=self.work_dir
                )
            )


class FileUrlManifestLocation(ManifestLocation):

    def __init__(self, reference: str, manifest_name: str, set_no_verify_ssl: bool=False):
        super().__init__(reference, manifest_name, set_no_verify_ssl)
        self.location_type = LocationType.FILE_URL
        self.sync()

    def get_files(self)->list:
        files = download_files(
            urls=[self.reference,],
            target_dir=self.work_dir,
            set_no_verify_ssl=self.set_no_verify_ssl
        )
        self.files = files


class GitManifestLocation(ManifestLocation):

    def __init__(self, reference: str, manifest_name: str, include_file_regex: str='.*\.yml|.*\.yaml', branch: str='main', relative_start_directory: str='/', ssh_private_key_path: str=None, set_no_verify_ssl: bool=False):
        super().__init__(reference, manifest_name, include_file_regex, set_no_verify_ssl, branch, relative_start_directory, ssh_private_key_path)
        self.location_type = LocationType.GIT_URL
        self.sync()

    def get_files(self)->list:
        self.files = git_clone_checkout_and_return_list_of_files(
            git_clone_url=self.reference,
            branch=self.branch,
            relative_start_directory=self.relative_start_directory,
            include_files_regex=self.include_file_regex,
            target_dir=self.work_dir,
            ssh_private_key_path=self.ssh_private_key_path,
            set_no_verify_ssl=self.set_no_verify_ssl
        )


class Project(Item):

    def __init__(
        self,
        name: str,
        logger: GenericLogger = GenericLogger(),
        use_default_scope: bool = True
    ):
        super().__init__(name, logger, use_default_scope)
        self.project_effective_manifest = None      # The manifest for the particular scopes
        self.previous_project_checksum = dict()     # Checksum of the previous effective manifest, per environment (scope)
        self.current_project_checksum = None        # The current checksum of the project_effective_manifest
        self.locations = list()                     # list of Location instances

        # TODO Needs to point to files/directories on the local file system ~~ OR ~~ to a Git repository, with a local work directory. Need to consider Git credentials...

    def add_manifest_location(self, location: ManifestLocation):
        self.locations.append(location)

    def add_environment(self, environment_name: str):
        self.add_scope(scope_name=environment_name)
        # self.environments.append(environment_name)

    def add_parent_project(self, parent_project_name: str):
        self.add_parent_item_name(parent_item_name=parent_project_name)

    def get_environment_names(self)->list:
        return self.scopes

    def as_dict(self):
        root = dict()
        root['spec'] = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'Project'
        root['metadata'] = dict()
        root['metadata']['name'] = self.name
        if len(self.scopes) > 0:
            root['metadata']['environments'] = self.scopes
        root['spec'] = dict()
        data = dict()
        if len(self.locations) > 0:
            data['locations'] = list()
            for location in self.locations:
                data['locations'].append(location.manifest_name)
        if len(self.parent_item_names) > 0:
            data['parentProjects'] = list()
            for parent_name in self.parent_item_names:
                data['parentProjects'].append({'name': parent_name,})
        root['spec'] = data
        return root

    def __str__(self)->str:
        yaml_str = ''
        for loc in self.locations:
            yaml_str = '{}---\n{}'.format(yaml_str, str(loc))
        return '{}---\n{}'.format(yaml_str, yaml.dump(self.as_dict()))


class Projects(Items):

    def __init__(self, logger: GenericLogger = GenericLogger()):
        super().__init__(logger)
        self.project_names_per_environment = dict()

    def add_project(self, project: Project):
        self.add_item(item=project)
        for environment_name in project.scopes:
            if environment_name not in self.project_names_per_environment:
                self.project_names_per_environment[environment_name] = list()
            self.project_names_per_environment[environment_name].append(project.name)
            

    def get_project_names_for_named_environment(self, environment_name: str='default')->list:
        if environment_name in self.project_names_per_environment:
            return self.project_names_per_environment[environment_name]
        raise Exception('Environment named "{}" not found in collection of projects'.format(environment_name))

    def get_project_by_name(self, project_name: str)->Project:
        return self.get_item_by_name(name=project_name)

    def parse_yaml(self, raw_data: dict):
        """Parse data into the various Objects.

        Use something like parse_yaml_file() from `verbacratis.utils.parser2` to obtain the dictionary value from a parsed YAML file
        """
        # Create individual class instances and add to the parsed_configuration for each type
        for part, data in raw_data.items():
            if isinstance(data, dict):
                converted_data = dict((k.lower(),v) for k,v in data.items()) # Convert keys to lowercase
                if 'kind' in converted_data:
                    if converted_data['kind'] == 'project':
                        use_default_scope = True
                        if 'environments' in converted_data['metadata']:
                            use_default_scope = False
                        project = Project(name=converted_data['metadata']['name'], use_default_scope=use_default_scope)
                        if 'spec' in converted_data:
                            spec = converted_data['spec']
                            if 'parentProjects' in spec:
                                for parent_project_data in spec['parentProjects']:
                                    project.add_parent_project(parent_project_name=parent_project_data['name'])
                                
                    elif converted_data['kind'] in ('LocalDirectoryManifestLocation', 'LocalFileManifestLocation', 'FileUrlManifestLocation', 'GitManifestLocation',):
                        parameters = converted_data['spec']
                        parameters['reference'] = parameters['location']
                        parameters['manifest_name'] = converted_data['metadata']['name']
                        parameters.pop('location')
                        if converted_data['kind'] == 'LocalDirectoryManifestLocation':
                            project.add_manifest_location(LocalDirectoryManifestLocation(parameters))
                        elif converted_data['kind'] == 'LocalFileManifestLocation':
                            project.add_manifest_location(LocalFileManifestLocation(parameters))
                        elif converted_data['kind'] == 'FileUrlManifestLocation':
                            project.add_manifest_location(FileUrlManifestLocation(parameters))
                        elif converted_data['kind'] == 'GitManifestLocation':
                            project.add_manifest_location(GitManifestLocation(parameters))
                        

    def __str__(self)->str:
        yaml_str = ''
        for project_name, project in self.items.items():
            yaml_str = '{}---\n{}'.format(yaml_str, str(project))
        return yaml_str

