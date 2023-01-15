import boto3
import hashlib
import copy
import os
import shutil
import tempfile
from acfop.utils.file_io import *


class Kinds:
    UNSUPPORTED = None
    KIND_ENVIRONMENT = 'Environment'
    KIND_SHELL_SCRIPT = 'ShellScript'
    KIND_ENVIRONMENT_VARIABLES = 'EnvironmentVariables'
    KIND_INFRASTRUCTURE_TEMPLATE = 'InfrastructureTemplate'
    KIND_TASK = 'Task'
    KIND_DEPLOYMENT = 'Deployment'


class Interpreters:
    PYTHON = 'python'
    SHELL = 'shell'


class MetaData:

    def __init__(self, data: dict) -> None:
        self.name = 'noName'
        self.labels = dict()
        if 'name' in data:
            self.name = '{}'.format(data['name'])
        if 'labels' in data:
            for k, v in data['labels'].items():
                self.labels[k] = '{}'.format(v)


class ConfigurationDefinition:

    def __init__(
        self,
        api_version: str='v1-alpha',
        kind: Kinds=Kinds.UNSUPPORTED,
        metadata: MetaData=MetaData(),
        spec: dict=dict()
    )->None:
        self.api_version = api_version
        self.kind = kind
        self.metadata = metadata
        self.spec = spec
        self.identifier = '{}:{}'.format(
            kind,
            hashlib.sha256(str(metadata.name).encode(('utf-8'))).hexdigest()
        )


class ConfigurationStore:

    def __init__(self, environment: str='default') -> None:
        self.environment = environment
        self.store = dict()             # Stores references to all ConfigurationDefinition manifests indexed by a calculated identifier in ConfigurationDefinition
        self.kind_store_map = dict()    # Stores the user friendly name of each configuration manifest, grouped by it's kind, with a link to the store identifier
        self.kind_store_map[Kinds.KIND_DEPLOYMENT] = dict()
        self.kind_store_map[Kinds.KIND_ENVIRONMENT] = dict()
        self.kind_store_map[Kinds.KIND_ENVIRONMENT_VARIABLES] = dict()
        self.kind_store_map[Kinds.KIND_INFRASTRUCTURE_TEMPLATE] = dict()
        self.kind_store_map[Kinds.KIND_SHELL_SCRIPT] = dict()
        self.kind_store_map[Kinds.KIND_TASK] = dict()

    def add_configuration_definition(self, configuration_definition: ConfigurationDefinition):
        if configuration_definition.identifier in self.store:
            raise Exception('COnfiguration Duplication Detected. Ensure every configuration element of the same kind has a unique name')
        if configuration_definition.kind not in self.kind_store_map:
            raise Exception('The configuration kind is not supported')
        self.store[configuration_definition.identifier] = configuration_definition
        self.kind_store_map[configuration_definition.kind][configuration_definition.metadata.name] = configuration_definition.identifier

    def get_configuration_definition(self, kind: Kinds, name: str)->ConfigurationDefinition:
        if kind in self.kind_store_map:
            if name in self.kind_store_map[kind]:
                identifier = self.kind_store_map[kind][name]
                if identifier in self.store:
                    return self.store[identifier]
        raise Exception('Configuration definition "{}" of kind "{}" was not found'.format(name, kind))


class ShellScript:
    def __init__(
        self,
        script_name: str,
        code_reference: str,
        interpreter: Interpreters=Interpreters.SHELL,
        on_fail_return_success: bool = False,
        on_fail_return_value: str = 'The Script Returned an Error',
    )->None:
        self.interpreter = interpreter
        self.on_fail_return_success = on_fail_return_success
        self.on_fail_return_value = on_fail_return_value
        if does_file_exists(code_reference) is True:
            self.script_file = copy_file(source_file=code_reference, tmp_dir=create_tmp_dir(script_name=script_name), file_name=script_name)
        else:
            self.script_file = create_tmp_file(tmp_dir=create_tmp_dir(script_name=script_name), file_name=script_name, data=code_reference)


class Environment:

    def __init__(self, configuration_portion_as_dict: dict) -> None:
        self.raw_configuration = configuration_portion_as_dict


class Credentials:

    def __init__(self, environment: Environment=Environment(), username: str=None, password: str=None) -> None:
        self.username = username
        self.password = password


class AwsKeyBasedCredentials(Credentials):

    def __init__(self, environment: Environment = Environment(), aws_access_key_id: str = None, aws_secret_access_key: str = None, region: str='eu-central-1') -> None:
        super().__init__(environment=environment, username=aws_access_key_id, password=aws_secret_access_key)
        self.region = region


class AwsProfileBasedCredentials(Credentials):

    def __init__(self, environment: Environment = Environment(), profile_name: str='default') -> None:
        super().__init__(environment=environment, username=profile_name, password=None)
        region: str='eu-central-1'




    



