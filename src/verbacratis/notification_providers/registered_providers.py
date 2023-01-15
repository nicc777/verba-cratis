from verbacratis.utils import get_logger
from verbacratis.notification_providers.rest import SendRestMessage


def get_notification_providers(logger=get_logger())->dict:
    providers = dict()
    providers['REST'] = SendRestMessage(logger=logger)


