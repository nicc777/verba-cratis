import traceback
import copy
from verbacratis.utils import get_logger


class NotificationProviderBaseClass:

    def __init__(
        self,
        logger=None
    )->None:
        if logger is None:
            logger = get_logger()
        self.logger = logger
        self.parameters = dict()

    def set_parameter(self, name: str, value: str):
        if name in self.parameters:
            raise Exception('Parameter already defined')
        self.parameters[name] = '{}'.format(value)

    def get_parameter_value(self, name)->str:
        if name in self.parameters:
            return self.parameters[name]
        return None

    def _get_final_parameters(self, parameter_overrides: dict)->dict:
        final_parameters = copy.deepcopy(self.parameters)
        for k,v in parameter_overrides.items():
            final_parameters[k] = '{}'.format(v)
        return final_parameters

    def send_message(self, message: str, parameter_overrides: dict=dict())->bool:
        return self._send_message_implementation(
            message=message,
            parameter_overrides=self._get_final_parameters(parameter_overrides=parameter_overrides)
        )

    def _send_message_implementation(self, message: str, parameter_overrides: dict)->bool:
        """
            Implement the actual sending of the message.
        """

        return True

