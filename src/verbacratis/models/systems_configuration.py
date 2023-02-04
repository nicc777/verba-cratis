"""
    Copyright (c) 2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import os
import yaml
import traceback
from verbacratis.models import AWS_REGIONS
from verbacratis.utils.parser2 import parse_yaml_file
from verbacratis.utils.git_integration import random_word, git_clone_checkout_and_return_list_of_files
from verbacratis.utils.file_io import create_tmp_dir, remove_tmp_dir_recursively


class Authentication:

    def __init__(self, name: str='no-auth'):
        self.authentication_type = None
        self.username = None
        self.name = name

    def as_dict(self):
        root = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'Authentication'
        root['metadata'] = dict()
        root['metadata']['name'] = self.name
        if self.authentication_type is not None:
            root['spec'] = dict()
            root['spec']['authenticationType'] = '{}'.format(self.authentication_type)
        return root

    def __str__(self)->str:
        return yaml.dump(self.as_dict())


class UnixHostAuthentication(Authentication):
    """Base class for remote Unix host authentication

    Typical minimal configuration manifest:

        apiVersion: v1-alpha
        kind: UnixHostAuthentication
        metadata:
            name: localhost

    Attributes:
        hostname: A string containing the hostname or IP address of the remote host
    
    """
    def __init__(self, hostname: str='localhost'):
        super().__init__(name=hostname)
        self.authentication_type = 'DefaultHostBasedAuthentication'
    
    def __str__(self)->str:
        return yaml.dump(self.as_dict())


class SshHostBasedAuthenticationConfig(UnixHostAuthentication): 
    """For hosts with configuration defined in /etc/ssh
    
    This would be similar to SSH to a host using the command `ssh username@hostname`

    Attributes:
        hostname: A string containing the hostname or IP address of the remote host
        username: The username to authenticate against
    """

    def __init__(self, hostname: str, username: str) -> None:
        super().__init__(hostname)
        if username is None:
            raise Exception('username is required')
        if not isinstance(username, str):
            raise Exception('username must be a string value')
        if len(username) == 0:
            raise Exception('username is required')
        self.authentication_type = 'SshUsingHostConfig'
        self.username = username

    def as_dict(self):
        root = dict()
        root['spec'] = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'SshHostBasedAuthenticationConfig'
        root['metadata'] = dict()
        root['metadata']['name'] = '{}@{}'.format(self.username, self.name)
        if self.authentication_type is not None:
            root['spec'] = dict()
            root['spec']['authenticationType'] = '{}'.format(self.authentication_type)
        return root


class SshCredentialsBasedAuthenticationConfig(SshHostBasedAuthenticationConfig):
    """For hosts requiring SSH with password based authentication
    
    The password attribute can contain an environment variable directive for example: 
    `{EnvironmentVariables:computed:systemXyzPassword}` - this environment variable will have to be defined in the 
    `EnvironmentVariables` kind manifest.

    Attributes:
        hostname: A string containing the hostname or IP address of the remote host
        username: The username to authenticate against
        password: The password for authentication WARNING: Never store password in version control or in clear text files!
    """
    def __init__(self, hostname: str, username: str, password: str) -> None:
        super().__init__(hostname, username)
        self.password = password
        self.password_is_final = True
        if password.startswith('${') and password.endswith('}'):
            self.password_is_final = False                          # Password still needs to be resolved via Environment...
        self.authentication_type = 'SshUsingCredentials'

    def as_dict(self):
        root = dict()
        root['spec'] = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'SshCredentialsBasedAuthenticationConfig'
        root['metadata'] = dict()
        root['metadata']['name'] = '{}@{}'.format(self.username, self.name)
        root['spec'] = dict()
        data = dict()
        data['authenticationType'] = self.authentication_type
        if len(self.password) > 0:
            data['password'] = '*'*len(self.password)
            if self.password_is_final is False:
                data['password'] = self.password
        root['spec'] = data
        return root


class SshPrivateKeyBasedAuthenticationConfig(SshHostBasedAuthenticationConfig):
    """For hosts requiring SSH with authentication using a private key
    
    Attributes:
        hostname: A string containing the hostname or IP address of the remote host
        username: The username to authenticate against
        private_key_path: Path to the private key

    Raises:
        Exception: If the private key value is not valid or the file cannot be read when creating an instance of this object, and exception will be thrown
    """
    def __init__(self, hostname: str, username: str, private_key_path: str) -> None:
        super().__init__(hostname, username)
        if os.path.isfile(private_key_path) is False:
            raise Exception('Private Key file "{}" does not exist'.format(private_key_path))
        if os.access(private_key_path, os.R_OK) is False:
            raise Exception('Private Key file "{}" cannot be read'.format(private_key_path))
        self.private_key_path = private_key_path
        self.authentication_type = 'SshUsingPrivateKey'

    def as_dict(self):
        root = dict()
        root['spec'] = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'SshPrivateKeyBasedAuthenticationConfig'
        root['metadata'] = dict()
        root['metadata']['name'] = '{}@{}'.format(self.username, self.name)
        root['spec'] = dict()
        data = dict()
        data['authenticationType'] = self.authentication_type
        data['privateKeyPath'] = self.private_key_path
        root['spec'] = data
        return root


class AwsAuthentication(Authentication):

    def __init__(
        self,
        name: str='default',
        region: str=os.getenv('AWS_DEFAULT_REGION', 'eu-central-1')
    ):
        super().__init__(name=name)
        self.region = region.lower()
        if os.getenv('AWS_REGION', None) is not None:
            if os.getenv('AWS_REGION').lower() in AWS_REGIONS:
                self.region = os.getenv('AWS_REGION').lower()
        self.authentication_type = 'AwsDefaultAuthentication'

    def as_dict(self):
        root = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'AwsAuthentication'
        root['metadata'] = dict()
        root['metadata']['name'] = '{}'.format(self.name)
        root['spec'] = dict()
        root['spec']['region'] = self.region
        return root

    def __str__(self)->str:
        return yaml.dump(self.as_dict())


class AwsKeyBasedAuthentication(AwsAuthentication):
    """For AWS accounts not defined as profiles and not using environment variables but access and secret keys instead
    
    The secret_key attribute can contain an environment variable directive for example: 
    `${EnvironmentVariables:computed:someSecret}` - this environment variable will have to be defined in the 
    `EnvironmentVariables` kind manifest.

    Manifest Format:

        apiVersion: v1-alpha
        kind: AwsKeyBasedAuthentication
        metadata:
            name: default
        spec:
            access_key: abc
            region: eu-central-1
            secret_key: ${{EnvironmentVariables:computed:someSecret}}

    Attributes:
        account_reference: A string with a name that can be referenced by other resources
        access_key: A string containing the access key value
        secret_key: A string containing the secret key value
        region: The AWS region for this config. Must be one as defined in `AWS_REGIONS`
    """
    def __init__(
        self,
        name: str,
        access_key: str = os.getenv('AWS_ACCESS_KEY_ID', ''),
        secret_key: str = os.getenv('AWS_SECRET_ACCESS_KEY', ''),
        region: str = os.getenv('AWS_DEFAULT_REGION', 'eu-central-1')
    ):
        super().__init__(name, region)
        self.access_key = access_key
        self.secret_key = secret_key
        self.secret_key_is_final = True
        if secret_key.startswith('${') and secret_key.endswith('}'):
            self.secret_key_is_final = False                        # Secret key still needs to be resolved via Environment...
        self.authentication_type = 'AwsKeyBasedAuthentication'

    def as_dict(self):
        root = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'AwsKeyBasedAuthentication'
        root['metadata'] = dict()
        root['metadata']['name'] = '{}'.format(self.name)
        root['spec'] = dict()
        root['spec']['region'] = self.region
        root['spec']['access_key'] = self.access_key
        if len(self.secret_key) > 0:
            root['spec']['secret_key'] = '*'*len(self.secret_key)
            if self.secret_key_is_final is False:
                root['spec']['secret_key'] = self.secret_key
        return root

    def __str__(self)->str:
        return yaml.dump(self.as_dict())


class AwsProfileBasedAuthentication(AwsAuthentication):
    """For AWS accounts not defined as profiles and not using environment variables but access and secret keys instead
    
    The secret_key attribute can contain an environment variable directive for example: 
    `{EnvironmentVariables:computed:someSecret}` - this environment variable will have to be defined in the 
    `EnvironmentVariables` kind manifest.

    Manifest format:

        apiVersion: v1-alpha
        kind: AwsProfileBasedAuthentication
        metadata:
            name: abc
        spec:
            profile_name: default
            region: eu-central-1

    Attributes:
        account_reference: A string with a name that can be referenced by other resources
        access_key: A string containing the access key value
        secret_key: A string containing the secret key value
        region: The AWS region for this config. Must be one as defined in `AWS_REGIONS`
    """
    def __init__(
        self,
        name: str,
        profile_name: str = os.getenv('AWS_PROFILE', ''),
        region: str = os.getenv('AWS_DEFAULT_REGION', 'eu-central-1')
    ):
        super().__init__(name, region)
        self.profile_name = profile_name
        if len(self.profile_name) == 0:
            raise Exception('Profile name cannot have zero length')
        self.authentication_type = 'AwsProfileBasedAuthentication'

    def as_dict(self):
        root = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'AwsProfileBasedAuthentication'
        root['metadata'] = dict()
        root['metadata']['name'] = '{}'.format(self.name)
        root['spec'] = dict()
        root['spec']['region'] = self.region
        root['spec']['profile_name'] = self.profile_name
        return root

    def __str__(self)->str:
        return yaml.dump(self.as_dict())



class InfrastructureAccount:
    """Defines an Infrastructure account

    There are a couple of types of Infrastructure accounts, and they may have a number of different configuration attributes:

    * ShellScript type accounts: These are accounts that represent a Unix type host, and can be either the localhost on which the deployment script is run, or a remote host with SSH access
    * AWS type account: Represents an AWS account (see https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html)

    ShellScript type accounts on remote hosts with SSH access requires the following values in the "authentication_config" attribute:

    * "authenticationType" (must be set to "SSH" as the only value for now)
    * "username"
    * "privateKeyLocation" (location to the private key file) OR "password" (the actual password, which can be securely obtained with the value "${EnvironmentVariables:computed:systemXyzPassword}")

    AWS type accounts requires the following values in the "authentication_config" attribute:

    * For authentication using AWS profiles:
            * useProfile - Boolean Value - OPTIONAL: Default=false assuming then that the standard AWS CLI Environment Variables are used
            * profileName - String - OPTIONAL, but required if "useProfile" is "true" - Automatically sets the environment variable "PROFILE". Used by the cloud provider code.
            * region - String - OPTIONAL, default=eu-central-1
    * For authentication using keys, used when "useProfile" is FALSE (and therefore requiring the following values to be set):
            * awsAccessKeyId - String - can be securely set with the value "${EnvironmentVariables:computed:awsAccessKeyId}"
            * awsSecretAccessKey - String - can be securely set with the value "${EnvironmentVariables:computed:awsSecretAccessKey}"

    By default there is always at least ONE InfrastructureAccount account with the following configuration:

    * account_name='deployment-host',
    * account_provider='RunOnLocalhost',
    * authentication_config=UnixHostAuthentication(hostname='localhost'),
    * environments=['default',]

    Attributes:
        account_name: A string containing a unique account name that can be referenced in the deployment configuration
        environments: A list of environments for which this infrastructure account is used
    """

    def __init__(
        self,
        account_name: str='deployment-host',
        environments: list=['default',],
        authentication_config: Authentication = Authentication(name='no-auth')
    ):
        self.account_name = account_name
        self.environments = environments
        self.account_provider = 'RunOnLocalhost'    # OPTIONS: "RunOnLocalhost" or "RunOnRemoteHost"
        self.authentication_config = authentication_config
        self.authentication_config_type = authentication_config.__class__.__name__

    def as_dict(self)->dict:
        root = dict()
        
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'InfrastructureAccount'
        root['metadata'] = dict()
        root['metadata']['name'] = self.account_name
        root['spec'] = dict()
        root['spec']['provider'] = self.account_provider
        if self.authentication_config is not None:
            root['spec']['authentication'] = dict()
            root['spec']['authentication']['authenticationReference'] = self.authentication_config.as_dict()['metadata']['name']
            root['spec']['authentication']['type'] = self.authentication_config.__class__.__name__
        if len(self.environments) == 0:
            self.environments = ['default',]
        root['metadata']['environments'] = self.environments
        return root

    def auth_id(self)->str:
        return None

    def __str__(self)->str:
        return yaml.dump(self.as_dict())


class UnixInfrastructureAccount(InfrastructureAccount):
    """Defines an Infrastructure account

    There are a couple of types of Infrastructure accounts, and they may have a number of different configuration attributes:

    * ShellScript type accounts: These are accounts that represent a Unix type host, and can be either the localhost on which the deployment script is run, or a remote host with SSH access
    * AWS type account: Represents an AWS account (see https://docs.aws.amazon.com/organizations/latest/userguide/orgs_getting-started_concepts.html)

    ShellScript type accounts on remote hosts with SSH access requires the following values in the "authentication_config" attribute:

    * "authenticationType" (must be set to "SSH" as the only value for now)
    * "username"
    * "privateKeyLocation" (location to the private key file) OR "password" (the actual password, which can be securely obtained with the value "${EnvironmentVariables:computed:systemXyzPassword}")

    AWS type accounts requires the following values in the "authentication_config" attribute:

    * For authentication using AWS profiles:
            * useProfile - Boolean Value - OPTIONAL: Default=false assuming then that the standard AWS CLI Environment Variables are used
            * profileName - String - OPTIONAL, but required if "useProfile" is "true" - Automatically sets the environment variable "PROFILE". Used by the cloud provider code.
            * region - String - OPTIONAL, default=eu-central-1
    * For authentication using keys, used when "useProfile" is FALSE (and therefore requiring the following values to be set):
            * awsAccessKeyId - String - can be securely set with the value "${EnvironmentVariables:computed:awsAccessKeyId}"
            * awsSecretAccessKey - String - can be securely set with the value "${EnvironmentVariables:computed:awsSecretAccessKey}"

    By default there is always at least ONE InfrastructureAccount account with the following configuration:

    * account_name='deployment-host',
    * authentication_config=dict(),
    * environments=['default',]

    Attributes:
        account_name: A string containing a unique account name that can be referenced in the deployment configuration
        run_on_deployment_host: a boolean value. Only ONE InfrastructureAccount can have the value of TRUE and it must be of type "ShellScript"
        authentication_config: The authentication parameters depending on the "account_provider" type
        environments: A list of environments for which this infrastructure account is used
    """
    def __init__(
        self,
        account_name: str='deployment-host',
        authentication_config: Authentication = Authentication(name='no-auth'),
        environments: list=['default',]
    ):
        super().__init__(account_name, environments, authentication_config=authentication_config)
        self.account_provider = 'ShellScript'
        self.authentication_config = authentication_config

    def as_dict(self)->dict:
        root = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'UnixInfrastructureAccount'
        root['metadata'] = dict()
        root['metadata']['name'] = self.account_name
        root['spec'] = dict()
        root['spec']['provider'] = self.account_provider
        if self.authentication_config is not None:
            root['spec']['authentication'] = dict()
            root['spec']['authentication']['authenticationReference'] = self.authentication_config.as_dict()['metadata']['name']
            root['spec']['authentication']['type'] = self.authentication_config.__class__.__name__
        if len(self.environments) == 0:
            self.environments = ['default',]
        root['metadata']['environments'] = self.environments
        return root

    def auth_id(self)->str:
        if self.authentication_config is None:
            return None
        if self.authentication_config.username is None:
            return '{}'.format(self.authentication_config.name)
        else:
            return '{}@{}'.format(self.authentication_config.username, self.authentication_config.name)

    def __str__(self)->str:
        return '---\n{}---\n{}'.format(
            str(self.authentication_config),
            yaml.dump(self.as_dict())
        )
        # return yaml.dump(self.as_dict())


class AwsInfrastructureAccount(InfrastructureAccount):

    def __init__(
        self,
        account_name: str = 'default',
        environments: list = ['default',],
        authentication_config: AwsAuthentication = AwsAuthentication(name='default'),
    ):
        super().__init__(account_name, environments, authentication_config=authentication_config)
        self.account_provider = 'AWS'
        self.authentication_config = authentication_config

    def as_dict(self)->dict:
        root = dict()
        root['apiVersion'] = 'v1-alpha'
        root['kind'] = 'AwsInfrastructureAccount'
        root['metadata'] = dict()
        root['metadata']['name'] = self.account_name
        root['spec'] = dict()
        root['spec']['provider'] = self.account_provider
        if self.authentication_config is not None:
            root['spec']['authentication'] = dict()
            root['spec']['authentication']['authenticationReference'] = self.authentication_config.as_dict()['metadata']['name']
            root['spec']['authentication']['type'] = self.authentication_config.__class__.__name__
        if len(self.environments) == 0:
            self.environments = ['default',]
        root['metadata']['environments'] = self.environments
        return root

    def __str__(self)->str:
        return '---\n{}---\n{}'.format(
            str(self.authentication_config),
            yaml.dump(self.as_dict())
        )


class SystemConfigurations:
    """Keeps a collection of Unix and AWS Cloud Infrastructure Accounts and Credentials
    """
    def __init__(self):    
        self.parsed_configuration = dict()
        self.parsed_configuration['Authentication'] = dict()
        self.parsed_configuration['UnixHostAuthentication'] = dict()
        self.parsed_configuration['SshHostBasedAuthenticationConfig'] = dict()
        self.parsed_configuration['SshCredentialsBasedAuthenticationConfig'] = dict()
        self.parsed_configuration['SshPrivateKeyBasedAuthenticationConfig'] = dict()
        self.parsed_configuration['AwsAuthentication'] = dict()
        self.parsed_configuration['AwsKeyBasedAuthentication'] = dict()
        self.parsed_configuration['AwsProfileBasedAuthentication'] = dict()
        self.parsed_configuration['InfrastructureAccount'] = dict()
        self.parsed_configuration['UnixInfrastructureAccount'] = dict()
        self.parsed_configuration['AwsInfrastructureAccount'] = dict()

        # Create a run-on-localhost account
        self.parsed_configuration['Authentication']['no-auth'] = Authentication()
        self.parsed_configuration['UnixInfrastructureAccount']['deployment-host'] = UnixInfrastructureAccount()

    def _create_Authentication_instance_from_data(self, data:dict)->Authentication: # pragma: no cover
        o = Authentication(name=data['metadata']['name'])
        if 'spec' in data:
            if 'authenticationType' in data['spec']:
                o.authentication_type = data['spec']['authenticationType']
            else:
                raise Exception('Expected .spec.authenticationType but got nothing.')
        o.username = None
        return o

    def _create_UnixHostAuthentication_instance_from_data(self, data:dict)->UnixHostAuthentication: # pragma: no cover
        o = UnixHostAuthentication(hostname=data['metadata']['name'])
        if 'spec' in data:
            if 'authenticationType' in data['spec']:
                o.authentication_type = data['spec']['authenticationType']
            else:
                raise Exception('Expected .spec.authenticationType but got nothing.')
        o.username = None
        return o

    def _create_SshHostBasedAuthenticationConfig_instance_from_data(self, data:dict)->SshHostBasedAuthenticationConfig: # pragma: no cover
        if '@' in data['metadata']['name']:
            o = SshHostBasedAuthenticationConfig(hostname=data['metadata']['name'].split('@')[1], username=data['metadata']['name'].split('@')[0])
            if 'spec' in data:
                if 'authenticationType' in data['spec']:
                    o.authentication_type = data['spec']['authenticationType']
                else:
                    raise Exception('Expected .spec.authenticationType but got nothing.')
            return o
        raise Exception('Expected "username@hostname format but got "{}""'.format(data['metadata']['name']))

    def _create_SshCredentialsBasedAuthenticationConfig_instance_from_data(self, data:dict)->SshCredentialsBasedAuthenticationConfig:   # pragma: no cover
        if '@' in data['metadata']['name']:
            o = SshCredentialsBasedAuthenticationConfig(hostname=data['metadata']['name'].split('@')[1], username=data['metadata']['name'].split('@')[0], password=data['spec']['password'])
            if 'authenticationType' in data['spec']:
                o.authentication_type = data['spec']['authenticationType']
            else:
                raise Exception('Expected .spec.authenticationType but got nothing.')
            return o
        raise Exception('Expected "username@hostname format but got "{}""'.format(data['metadata']['name']))

    def _create_SshPrivateKeyBasedAuthenticationConfig_instance_from_data(self, data:dict)->SshPrivateKeyBasedAuthenticationConfig: # pragma: no cover
        if '@' in data['metadata']['name']:
            o = SshPrivateKeyBasedAuthenticationConfig(hostname=data['metadata']['name'].split('@')[1], username=data['metadata']['name'].split('@')[0], private_key_path=data['spec']['privateKeyPath'])
            if 'authenticationType' in data['spec']:
                o.authentication_type = data['spec']['authenticationType']
            else:
                raise Exception('Expected .spec.authenticationType but got nothing.')
            return o
        raise Exception('Expected "username@hostname format but got "{}""'.format(data['metadata']['name']))

    def _create_AwsAuthentication_instance_from_data(self, data:dict)->AwsAuthentication:   # pragma: no cover
        o = AwsAuthentication(name=data['metadata']['name'])
        if 'spec' in data:
            if 'authenticationType' in data['spec']:
                o.authentication_type = data['spec']['authenticationType']
            else:
                raise Exception('Expected .spec.authenticationType but got nothing.')
            if 'region' in data['spec']:
                o.region = data['spec']['region']
        return o

    def _create_AwsKeyBasedAuthentication_instance_from_data(self, data:dict)->AwsAuthentication:   # pragma: no cover
        o = AwsKeyBasedAuthentication(name=data['metadata']['name'])
        if 'spec' in data:
            if 'authenticationType' in data['spec']:
                o.authentication_type = data['spec']['authenticationType']
            else:
                raise Exception('Expected .spec.authenticationType but got nothing.')
            if 'region' in data['spec']:
                o.region = data['spec']['region']
            if 'access_key' in data['spec']:
                o.access_key = data['spec']['access_key']
            if 'secret_key' in data['spec']:
                o.secret_key = data['spec']['secret_key']
        return o

    def _create_AwsProfileBasedAuthentication_instance_from_data(self, data:dict)->AwsAuthentication:
        o = AwsProfileBasedAuthentication(name=data['metadata']['name'], profile_name='default')
        if 'spec' in data:
            if 'authentication' in data['spec']:
                if 'authenticationType' in data['spec']['authentication']:
                    o.authentication_type = data['spec']['authentication']['authenticationType']
                else:
                    raise Exception('Expected .spec.authenticationType but got nothing.')
            if 'region' in data['spec']:
                o.region = data['spec']['region'] 
            if 'profile_name' in data['spec']:
                o.profile_name = data['spec']['profile_name']
        o.username = None
        return o

    def _create_InfrastructureAccount_instance_from_data(self, data:dict)->InfrastructureAccount:   # pragma: no cover
        o = InfrastructureAccount(account_name=data['metadata']['name'])
        if 'environments' in data['metadata']:
            o.environments = data['metadata']['environments']
        if 'provider' in data['spec']:
            o.account_provider = data['spec']['provider']
        if 'authentication' in data['spec']:
            if 'type' in data['spec']['authentication'] and 'authenticationReference' in data['spec']['authentication']:
                o.authentication_config = Authentication(name=data['spec']['authentication']['authenticationReference'])
                o.authentication_config_type = data['spec']['authentication']['type']
        return o

    def _create_UnixInfrastructureAccount_instance_from_data(self, data:dict)->UnixInfrastructureAccount:
        o = UnixInfrastructureAccount(account_name=data['metadata']['name'])
        if 'environments' in data['metadata']:
            o.environments = data['metadata']['environments']
        if 'provider' in data['spec']:
            o.account_provider = data['spec']['provider']
        if 'authentication' in data['spec']:
            if 'type' in data['spec']['authentication'] and 'authenticationReference' in data['spec']['authentication']:
                o.authentication_config = Authentication(name=data['spec']['authentication']['authenticationReference'])
                o.authentication_config_type = data['spec']['authentication']['type']
        return o

    def _create_AwsInfrastructureAccount_instance_from_data(self, data:dict)->AwsInfrastructureAccount:
        o = AwsInfrastructureAccount(account_name=data['metadata']['name'])
        if 'environments' in data['metadata']:
            o.environments = data['metadata']['environments']
        if 'provider' in data['spec']:
            o.account_provider = data['spec']['provider']
        if 'authentication' in data['spec']:
            if 'type' in data['spec']['authentication'] and 'authenticationReference' in data['spec']['authentication']:
                o.authentication_config = Authentication(name=data['spec']['authentication']['authenticationReference'])
                o.authentication_config_type = data['spec']['authentication']['type']
        return o


    def parse_yaml(self, raw_data: dict):
        """Parse data into the various Objects.

        Use something like parse_yaml_file() from `verbacratis.utils.parser2` to obtain the dictionary value from a parsed YAML file
        """
        # Create individual class instances and add to the parsed_configuration for each type
        for part, data in raw_data.items():
            if isinstance(data, dict):
                converted_data = dict((k.lower(),v) for k,v in data.items()) # Convert keys to lowercase
                if 'kind' in converted_data:
                    if converted_data['kind'].lower() == 'Authentication'.lower():
                        self.add_configuration(item=self._create_Authentication_instance_from_data(data=converted_data))
                    elif converted_data['kind'].lower() == 'UnixHostAuthentication'.lower():
                        self.add_configuration(item=self._create_UnixHostAuthentication_instance_from_data(data=converted_data))
                    elif converted_data['kind'].lower() == 'SshHostBasedAuthenticationConfig'.lower():
                        self.add_configuration(item=self._create_SshHostBasedAuthenticationConfig_instance_from_data(data=converted_data))
                    elif converted_data['kind'].lower() == 'SshCredentialsBasedAuthenticationConfig'.lower():
                        self.add_configuration(item=self._create_SshCredentialsBasedAuthenticationConfig_instance_from_data(data=converted_data))
                    elif converted_data['kind'].lower() == 'SshPrivateKeyBasedAuthenticationConfig'.lower():
                        self.add_configuration(item=self._create_SshPrivateKeyBasedAuthenticationConfig_instance_from_data(data=converted_data))
                    elif converted_data['kind'].lower() == 'AwsAuthentication'.lower():
                        self.add_configuration(item=self._create_AwsAuthentication_instance_from_data(data=converted_data))
                    elif converted_data['kind'].lower() == 'AwsKeyBasedAuthentication'.lower():
                        self.add_configuration(item=self._create_AwsKeyBasedAuthentication_instance_from_data(data=converted_data))
                    elif converted_data['kind'].lower() == 'AwsProfileBasedAuthentication'.lower():
                        self.add_configuration(item=self._create_AwsProfileBasedAuthentication_instance_from_data(data=converted_data))
                    elif converted_data['kind'].lower() == 'InfrastructureAccount'.lower():
                        self.add_configuration(item=self._create_InfrastructureAccount_instance_from_data(data=converted_data))
                    elif converted_data['kind'].lower() == 'UnixInfrastructureAccount'.lower():
                        self.add_configuration(item=self._create_UnixInfrastructureAccount_instance_from_data(data=converted_data))
                    elif converted_data['kind'].lower() == 'AwsInfrastructureAccount'.lower():
                        self.add_configuration(item=self._create_AwsInfrastructureAccount_instance_from_data(data=converted_data))
        
        # Go through all the InfrastructureAccount's and link their proper authentication classes based on the Authentication class name.
        for object_class_type, objects in self.parsed_configuration.items():
            if object_class_type in ('InfrastructureAccount', 'UnixInfrastructureAccount', 'AwsInfrastructureAccount',):
                for object_name, object_def in objects.items():
                    object_def.authentication_config = self.get_configuration_instance(
                        class_type_name=object_def.authentication_config_type,
                        instance_name=object_def.authentication_config.name
                    )

        # Update all our environments in our local deployment host
        self.update_local_deployment_host_with_all_environments()

    def get_configuration_instance(self, class_type_name: str, instance_name: str):
        if class_type_name in self.parsed_configuration:
            for object_name, object_instance in self.parsed_configuration[class_type_name].items():
                if object_name == instance_name:
                    return object_instance
        raise Exception('"{}" of type "{}" NOT FOUND'.format(instance_name, class_type_name))

    def get_infrastructure_account_names(self)->tuple:
        names = list()
        for object_class_type, objects in self.parsed_configuration.items():
            for object_name, object_def in objects.items():
                names.append({'ObjectClassType': object_class_type, 'ObjectName': object_name}) # Something like {'ObjectClassType': 'Authentication', 'ObjectName': 'some-name'}
        return tuple(names)

    def get_infrastructure_account_auth_config(self, infrastructure_account_name: str, search_scope: tuple=('InfrastructureAccount', 'UnixInfrastructureAccount', 'AwsInfrastructureAccount',))->list:
        authentication_configurations = list
        for object_class_type, objects in self.parsed_configuration.items():
            if object_class_type in search_scope:
                for object_name, object_def in objects.items():
                    if object_name == infrastructure_account_name:
                        authentication_configurations.append({'ObjectClassType': object_class_type, 'ObjectInstance': object_def})
        return authentication_configurations

    def find_local_deployment_host_account_name(self)->str:
        if 'deployment-host' in self.parsed_configuration['UnixInfrastructureAccount']:
            return self.parsed_configuration['UnixInfrastructureAccount']['deployment-host'].account_name
        for object_name, object_def in self.parsed_configuration['UnixInfrastructureAccount'].items():
            if object_def.account_provider == 'RunOnLocalhost':
                return object_name
        raise Exception('Critical error: No account found for running on local host')

    def add_configuration(self, item: object):
        if item.__class__.__name__ == 'Authentication':
            self.parsed_configuration['Authentication'][item.name] = item
        elif item.__class__.__name__ == 'UnixHostAuthentication':
            self.parsed_configuration['UnixHostAuthentication'][item.name] = item
        elif item.__class__.__name__ == 'SshHostBasedAuthenticationConfig':
            self.parsed_configuration['SshHostBasedAuthenticationConfig'][item.as_dict()['metadata']['name']] = item
        elif item.__class__.__name__ == 'SshCredentialsBasedAuthenticationConfig':
            self.parsed_configuration['SshCredentialsBasedAuthenticationConfig'][item.as_dict()['metadata']['name']] = item
        elif item.__class__.__name__ == 'SshPrivateKeyBasedAuthenticationConfig':
            self.parsed_configuration['SshPrivateKeyBasedAuthenticationConfig'][item.as_dict()['metadata']['name']] = item
        elif item.__class__.__name__ == 'AwsAuthentication':
            self.parsed_configuration['AwsAuthentication'][item.name] = item
        elif item.__class__.__name__ == 'AwsKeyBasedAuthentication':
            self.parsed_configuration['AwsKeyBasedAuthentication'][item.name] = item
        elif item.__class__.__name__ == 'AwsProfileBasedAuthentication':
            self.parsed_configuration['AwsProfileBasedAuthentication'][item.name] = item
        elif item.__class__.__name__ == 'InfrastructureAccount':
            self.parsed_configuration['InfrastructureAccount'][item.account_name] = item
        elif item.__class__.__name__ == 'UnixInfrastructureAccount':
            self.parsed_configuration['UnixInfrastructureAccount'][item.account_name] = item
        elif item.__class__.__name__ == 'AwsInfrastructureAccount':
            self.parsed_configuration['AwsInfrastructureAccount'][item.account_name] = item
        else:
            raise Exception('Item type "{}" not recognized'.format(item.__class__.__name__))

    def get_all_environments(self)->tuple:
        environments = list()
        for object_class_type, objects in self.parsed_configuration.items():
            if object_class_type in ('InfrastructureAccount', 'UnixInfrastructureAccount', 'AwsInfrastructureAccount',):
                for object_name, object_def in objects.items():
                    for environment in object_def.environments:
                        if environment not in environments:
                            environments.append(environment)
        return tuple(environments)

    def update_local_deployment_host_with_all_environments(self):
        environments = self.get_all_environments()
        if len(environments) is None:
            raise Exception('At least one environment name must be set')
        if len(environments) == 0:
            raise Exception('At least one environment name must be set')
        self.parsed_configuration['UnixInfrastructureAccount'][self.find_local_deployment_host_account_name()].environments = environments

    def get_infrastructure_Accounts_for_named_environment(self, environment_name: str, search_scope: tuple=('InfrastructureAccount', 'UnixInfrastructureAccount', 'AwsInfrastructureAccount',))->list:
        """Get all Infrastructure Accounts scoped for a certain environment, for example sandbox
        """
        infrastructure_accounts = list
        for object_class_type, objects in self.parsed_configuration.items():
            if object_class_type in search_scope:
                for object_name, object_def in objects.items():
                    if environment_name in object_def.environments:
                        infrastructure_accounts.append({'ObjectClassType': object_class_type, 'ObjectInstance': object_def})
        return infrastructure_accounts

    def __str__(self)->str:
        config_as_str = ''
        for object_class_type, objects in self.parsed_configuration.items():
            for object_name, object_def in objects.items():
                config_as_str = '{}\n---\n{}'.format(config_as_str, str(object_def))
        return config_as_str


def get_system_configuration_from_files(files: list)->SystemConfigurations:
    sc = SystemConfigurations()
    try:
        for file in files:
            sc.parse_yaml(raw_data=parse_yaml_file(file_path=file))
    except:
        traceback.print_exc()
    return sc


def get_yaml_configuration_from_url(urls: list, set_no_verify_ssl: bool=False, system_configurations: SystemConfigurations=SystemConfigurations())->SystemConfigurations:
    """Parse the file specified in the URL to return a SystemConfigurations instance

    Args:
        urls: A list of strings containing the URLs to the YAML files to download and parse
        set_no_verify_ssl: A boolean that will not check SSL certificates if set to True (default=`False`). Useful when using self-signed certificates, but use with caution!!
        system_configurations: An existing SystemConfigurations object, if it exists. By default a new instance will be created

    Returns:
        `SystemConfigurations` instance with the parsed configuration
    """
    # system_configurations.parse_yaml(raw_data=parse_yaml_file(file_path=file_path))
    tmp_dir = create_tmp_dir(sub_dir=random_word(length=32))

    return system_configurations


def get_yaml_configuration_from_git(
    git_clone_url: str,
    branch: str='main',
    relative_start_directory: str='/',
    include_files_regex: str='.*\.yaml$|.*\.yml$',
    ssh_private_key_path: str=None,
    set_no_verify_ssl: bool=False
)->SystemConfigurations:
    """Parse files from a Git repository matching a file pattern withing a branch and directory to return a SystemConfigurations instance

    Args:
        git_clone_url: A string containing the Git repository clone URL, for example `git@github.com:nicc777/verba-cratis-test-infrastructure.git`
        branch: String containing the branch name to check out. Default is `main`
        relative_start_directory: String containing the sub-directory in the cloned repository to look for file. Default is the root of the cloned repository
        include_files_regex: A regular expression string for files to match. Default is matching YAML files.
        ssh_private_key_path: A string containing the SSH private key to use. Optional, and if value is `None`, the default transport (HTTPS) will be used.
        set_no_verify_ssl: A boolean that will not check SSL certificates if set to True (default=`False`). Useful when using self-signed certificates, but use with caution!!

    Returns:
        `SystemConfigurations` instance with the parsed configuration
    """
    tmp_dir = create_tmp_dir(sub_dir=random_word(length=32))
    files = git_clone_checkout_and_return_list_of_files(
        git_clone_url=git_clone_url,
        branch=branch,
        relative_start_directory=relative_start_directory,
        include_files_regex=include_files_regex,
        target_dir=tmp_dir,
        ssh_private_key_path=ssh_private_key_path,
        set_no_verify_ssl=set_no_verify_ssl
    )
    sc = get_system_configuration_from_files(files=files)
    remove_tmp_dir_recursively(dir=tmp_dir)
    return sc
