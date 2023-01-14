import boto3


class Kinds:
    UNSUPPORTED = None
    KIND_ENVIRONMENT = 'Environment'
    KIND_SHELL_SCRIPT = 'ShellScript'
    KIND_ENVIRONMENT_VARIABLES = 'EnvironmentVariables'
    KIND_INFRASTRUCTURE_TEMPLATE = 'InfrastructureTemplate'
    KIND_TASK = 'Task'
    KIND_DEPLOYMENT = 'Deployment'


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


class ShellScripts:

    def __init__(self) -> None:
        pass


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




    



