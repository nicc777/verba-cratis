import traceback
from urllib import request
from urllib.parse import urlencode
from verbacratis.notification_providers import NotificationProviderBaseClass


class SendRestMessage(NotificationProviderBaseClass):

    def __init__(self, logger=None)->None:
        super().__init__(logger)

    def _send_message_implementation(self, message: str, parameter_overrides: dict)->bool:
        """
            parameter_overrides will contain the following:

                URL             -> REQUIRED
                method          -> OPTIONAL: Default=POST
                ContentType     -> OPTIONAL: Default="text/plain"

            References:

                * https://realpython.com/urllib-request/
                * https://docs.python.org/3/library/urllib.request.html#urllib.request.Request
        """
        headers = dict()
        url = None
        method = 'POST'
        headers['content-type'] = 'text/plain'
        if 'URL' in parameter_overrides:
            url = parameter_overrides['URL']
        if 'ContentType' in parameter_overrides:
            headers['content-type'] = parameter_overrides['ContentType']
        if 'method' in parameter_overrides:
            method = parameter_overrides['method']
        try:
            binary_data = message if type(message) == bytes else message.encode('utf-8')
            req = request.Request(url=url, data=binary_data, headers=headers, method=method)
            resp = request.urlopen(req)
            self.logger.info('{}'.format(resp.getheaders()))
            self.logger.info('{}'.format(resp.read()))
        except:
            self.logger.error('EXCEPTION Sending HTTP Notification: {}'.format(traceback.format_exc()))
            return False
        return True

