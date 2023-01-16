"""
    Copyright (c) 2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import copy
from verbacratis.utils import get_logger


class NotificationProviderBaseClass:
    """Base class for notifications.

    Notifications can be sent to various back-ends exposing various different API's. This base class enables a 
    consistent way to send notifications to virtually and service in a consistent way.

    This class contains no implementation logic of any backend or API.

    Attributes:
        logger: The logger class
    """

    def __init__(
        self,
        logger=None
    )->None:
        """Initializes the class with a logger. If no logger is supplied, the default logger is used."""
        if logger is None:          # pragma: no cover
            logger = get_logger()
        self.logger = logger
        self.parameters = dict()

    def set_parameter(self, name: str, value: str):
        """Sets a parameter that can be used by the implementation, for example a URL.

        Each parameter must have a name, and each name must be unique for each implementation of this base class.

        Each parameter must have a STRING value. It is up to the implementation class to convert the string value to a
        usable value for the implementation of the notification logic.

        Args:
            name: (required) The name of the parameter
            value: (required) The String value of the parameter.

        Raises:
            Exception: If a duplicate parameter name is used.
        """
        if name in self.parameters:
            raise Exception('Parameter already defined')
        self.parameters[name] = '{}'.format(value)

    def get_parameter_value(self, name)->str:
        """Get a named parameter value

        Args:
            name: (required) The name of the parameter

        Returns:
            A STRING with the value of the named parameter. If the named parameter is not found, a None value will be 
            returned
        """
        if name in self.parameters:
            return self.parameters[name]
        return None

    def _get_final_parameters(self, parameter_overrides: dict)->dict:
        final_parameters = copy.deepcopy(self.parameters)
        for k,v in parameter_overrides.items():
            final_parameters[k] = '{}'.format(v)
        return final_parameters

    def send_message(self, message: str, parameter_overrides: dict=dict())->bool:
        """Get a named parameter value

        Args:
            message: (required) A STRING containing the message to be send.
            parameter_overrides: (optional, default=dict()) A dictionary of string key and values that can be used to 
                override existing parameters

        Returns:
            A boolean based on the success or failure to send the notification.
        """
        return self._send_message_implementation(
            message=message,
            parameter_overrides=self._get_final_parameters(parameter_overrides=parameter_overrides)
        )

    def _send_message_implementation(self, message: str, parameter_overrides: dict)->bool:  # pragma: no cover
        """
            Implement the actual sending of the message.
        """

        return True

