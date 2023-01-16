"""
    Copyright (c) 2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

from verbacratis.utils import get_logger
from verbacratis.notification_providers.rest import SendRestMessage


def get_notification_providers(logger=get_logger())->dict:
    providers = dict()
    providers['REST'] = SendRestMessage(logger=logger)


