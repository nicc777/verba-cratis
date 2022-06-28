"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/acfop/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

from acfop.utils import get_logger
from acfop import BUILD_ID


def main()->dict:
    build_id = BUILD_ID
    logger = get_logger()
    logger.info('Started with build ID {}'.format(build_id))
    result = dict()
    result['BuildId'] = build_id
    return result


if __name__ == '__main__':  # pragma: no cover
    main()
