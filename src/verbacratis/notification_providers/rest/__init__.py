"""
    Copyright (c) 2022-2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

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

