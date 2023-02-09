"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import yaml
import hashlib
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


class Location:

    def __init__(self, reference: str, include_file_regex: str='.*\.yml|.*\.yaml'):
        self.files = list()
        self.checksum = None
        self.location_type = None
        local_type_attempt = identify_local_path_type(path=reference)
        if local_type_attempt is not PathTypes.UNKNOWN:
            if local_type_attempt == PathTypes.FILE:
                self.location_type = LocationType.LOCAL_FILE
            elif local_type_attempt == PathTypes.DIRECTORY:
                self.location_type = LocationType.LOCAL_DIRECTORY
        else:
            if is_url_a_git_repo(url=reference):
                self.location_type = LocationType.GIT_URL
            elif reference.lower().startswith('http') is True:
                self.location_type = LocationType.FILE_URL
        if self.location_type is None:
            raise Exception('Could not identify the location type with the reference "{}"'.format(reference))
        self.location_reference = reference
        self.include_file_regex = include_file_regex
        self.sync()
        
    def sync(self):
        self.cleanup_work_dir()
        self.work_dir = create_tmp_dir(sub_dir='Location__{}'.format(self.location_reference))
        self.file_list = self.get_files()
        self._update_checksum_from_work_dir_files()

    def cleanup_work_dir(self):
        remove_tmp_dir_recursively(dir=self.work_dir)
        self.file_list = list()

    def _get_files_from_git(self):
        final_location, branch, relative_start_directory, ssh_private_key_path, set_no_verify_ssl = extract_parameters_from_url(location=self.location_reference)
        self.files = git_clone_checkout_and_return_list_of_files(
            git_clone_url=final_location,
            branch=branch,
            relative_start_directory=relative_start_directory,
            include_files_regex=self.include_file_regex,
            target_dir=self.work_dir,
            ssh_private_key_path=ssh_private_key_path,
            set_no_verify_ssl=set_no_verify_ssl
        )

    def _get_file_from_url(self):
        final_location, branch, relative_start_directory, ssh_private_key_path, set_no_verify_ssl = extract_parameters_from_url(location=self.location_reference)
        files = download_files(
            urls=[final_location,],
            target_dir=self.work_dir,
            set_no_verify_ssl=set_no_verify_ssl
        )
        self.files = files

    def _get_files_from_dir(self):
        for file in find_matching_files(start_dir=self.location_reference, pattern=self.include_file_regex):
            self.files.append(
                copy_file(
                    source_file=file,
                    file_name=hashlib.sha256(file.encode('utf-8')).hexdigest(),
                    tmp_dir=self.work_dir
                )
            )

    def get_files(self)->list:
        """Builds a list of files from the location reference and parse according to the type

        All local and remote files will be copied into the local temporary work directory in self.work_dir
        """
        if len(self.files) == 0:
            if self.location_type == LocationType.GIT_URL:
                self._get_files_from_git()
            elif self.location_type == LocationType.FILE_URL:
                self._get_file_from_url()
            elif self.location_type == LocationType.LOCAL_FILE:
                self.files.append(copy_file(source_file=self.location_reference, file_name=get_file_from_path(input_path=self.location_reference), tmp_dir=self.work_dir))
            elif self.location_type == LocationType.LOCAL_DIRECTORY:
                self._get_files_from_dir()
        return self.files

    def _update_checksum_from_work_dir_files(self):
        raw_string = ''
        for file in self.files:
            raw_string = '{}{}\n'.format(raw_string, file_checksum(path=file))
        self.checksum = hashlib.sha256(raw_string.encode('utf-8')).hexdigest()


class Project(Item):

    def __init__(
        self,
        name: str,
        logger: GenericLogger = GenericLogger(),
        use_default_scope: bool = True
    ):
        super().__init__(name, logger, use_default_scope)
        self.manifest_directories = list()  # List of dict with items "path" and "type", where type can only be YAML (for now at least)
        self.manifest_files = list()        # List of dict with items "path" and "type", where type can only be YAML (for now at least)
        self.include_file_regex = '.*\.yml|.*\.yaml'
        self.project_effective_manifest = None      # The manifest for the particular scopes
        self.previous_project_checksum = dict()     # Checksum of the previous effective manifest, per environment (scope)
        self.current_project_checksum = None        # The current checksum of the project_effective_manifest

        # TODO Needs to point to files/directories on the local file system ~~ OR ~~ to a Git repository, with a local work directory. Need to consider Git credentials...

    def add_environment(self, environment_name: str):
        self.add_scope(scope_name=environment_name)
        # self.environments.append(environment_name)

    def add_parent_project(self, parent_project_name: str):
        self.add_parent_item_name(parent_item_name=parent_project_name)

    def add_manifest_directory(self, path: str, type: str='YAML'):
        self.manifest_directories.append({'path': path, 'type': type})

    def override_include_file_regex(self, include_file_regex: tuple):
        self.include_file_regex = include_file_regex

    def add_manifest_file(self, path: str, type: str='YAML'):
        self.manifest_files.append({'path': path, 'type': type})

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
        if self.include_file_regex is not None:
            if len(self.include_file_regex) > 0:
                data['includeFileRegex'] = self.include_file_regex
        if len(self.manifest_directories) > 0:
            if 'locations' not in data:
                data['locations'] = dict()
            data['locations']['directories'] = list()
            for directory in self.manifest_directories:
                if 'path' in directory and 'type' in directory:
                    directory_data = {
                        'path': directory['path'],
                        'type': directory['type'],
                    }
                    data['locations']['directories'].append(directory_data)
        if len(self.manifest_files) > 0:
            if 'locations' not in data:
                data['locations'] = dict()
            data['locations']['files'] = list()
            for file in self.manifest_files:
                if 'path' in file and 'type' in file:
                    file_data = {
                        'path': file['path'],
                        'type': file['type'],
                    }
                    data['locations']['files'].append(file_data)
        if len(self.parent_item_names) > 0:
            data['parentProjects'] = list()
            for parent_name in self.parent_item_names:
                data['parentProjects'].append({'name': parent_name,})
        root['spec'] = data
        return root

    def __str__(self)->str:
        return yaml.dump(self.as_dict())


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
                    if converted_data['kind'].lower() == 'Project'.lower():
                        use_default_scope = True
                        if 'environments' in converted_data['metadata']:
                            use_default_scope = False
                        project = Project(name=converted_data['metadata']['name'], use_default_scope=use_default_scope)
                        if 'spec' in converted_data:
                            spec = converted_data['spec']
                            if 'includeFileRegex' in spec:
                                project.include_file_regex = '{}'.format(converted_data['spec']['includeFileRegex'])
                            if 'locations' in spec:
                                if 'directories' in spec['locations']:
                                    for dir_data in spec['locations']['directories']:
                                        dir_type = 'YAML'
                                        if 'type' in dir_data:
                                            dir_type = dir_data['type']
                                        if 'path' in dir_data:
                                            project.add_manifest_directory(path=dir_data['path'], type=dir_type)
                                if 'files' in spec['locations']:
                                    for dir_data in spec['locations']['files']:
                                        dir_type = 'YAML'
                                        if 'type' in dir_data:
                                            dir_type = dir_data['type']
                                        if 'path' in dir_data:
                                            project.add_manifest_file(path=dir_data['path'], type=dir_type)
                            if 'parentProjects' in spec:
                                for parent_project_data in spec['parentProjects']:
                                    project.add_parent_project(parent_project_name=parent_project_data['name'])

    def __str__(self)->str:
        yaml_str = ''
        for project_name, project in self.items.items():
            yaml_str = '{}---\n{}'.format(yaml_str, str(project))
        return yaml_str

