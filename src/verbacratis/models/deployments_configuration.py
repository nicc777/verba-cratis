"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import yaml
from verbacratis.models import GenericLogger
from verbacratis.models.ordering import Item, Items


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
        self.include_file_regex = ('*\.yml', '*\.yaml')
        self.project_effective_manifest = None      # The manifest for the particular scopes
        self.previous_project_checksum = dict()     # Checksum of the previous effective manifest, per environment (scope)
        self.current_project_checksum = None        # The current checksum of the project_effective_manifest

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
        root['spec'] = dict()
        data = dict()
        # data['name'] = self.name
        data['includeFileRegex'] = list()
        if len(self.include_file_regex) > 0:
            for file_regex in self.include_file_regex:
                data['includeFileRegex'].append(file_regex)
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
        data['environments'] = [{'name': 'default'},]
        if len(self.scopes) > 0:
            data['environments'] = list()
            for scope_name in self.scopes:
                data['environments'].append({'name': scope_name, })
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

    def __str__(self)->str:
        yaml_str = ''
        for project_name, project in self.items.items():
            yaml_str = '{}---\n{}'.format(yaml_str, str(project))
        return yaml_str

