"""
    Copyright (c) 2022. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""


class GenericLogger:

    def __init__(self, logger=None):
        self.enable_logging = False
        self.logger = None
        if logger is not None:
            self.logger = logger
            self.enable_logging = True

    def info(self, message):
        if self.enable_logging:
            try:
                self.logger.info(message)
                return
            except:
                self.enable_logging = False
        print('INFO: {}'.format(message))

    def debug(self, message):
        if self.enable_logging:
            try:
                self.logger.debug(message)
                return
            except:
                self.enable_logging = False
        print('DEBUG: {}'.format(message))

    def warn(self, message):
        if self.enable_logging:
            try:
                self.logger.warn(message)
                return
            except:
                self.enable_logging = False
        print('WARN: {}'.format(message))

    def error(self, message):
        if self.enable_logging:
            try:
                self.logger.error(message)
                return
            except:
                self.enable_logging = False
        print('ERROR: {}'.format(message))



