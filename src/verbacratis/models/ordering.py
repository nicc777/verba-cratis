"""
    Copyright (c) 2023. All rights reserved. NS Coetzee <nicc777@gmail.com>

    This file is licensed under GPLv3 and a copy of the license should be included in the project (look for the file 
    called LICENSE), or alternatively view the license text at 
    https://raw.githubusercontent.com/nicc777/verbacratis/main/LICENSE or https://www.gnu.org/licenses/gpl-3.0.txt
"""

import copy
from verbacratis.models import GenericLogger


class Item:

    def __init__(self, name, logger: GenericLogger=GenericLogger(), use_default_scope: bool=True):
        self.name = name
        self.parent_item_names = list()
        self.scopes = list()
        if use_default_scope is True:
            self.scopes.append('default')
        self.logger = logger

    def add_parent_item_name(self, parent_item_name:str):
        if parent_item_name not in self.parent_item_names:
            self.parent_item_names.append(parent_item_name)

    def add_scope(self, scope_name: str, replace_default_if_exists: bool=True):
        if replace_default_if_exists is True and 'default' in self.scopes:
            self.scopes.remove('default')
        if scope_name not in self.scopes:
            self.scopes.append(scope_name)


class Items:

    def __init__(self, logger: GenericLogger=GenericLogger()):
        self.items = dict()
        self.logger = logger

    def add_item(self, item: Item):
        if item.name not in self.items:
            self.items[item.name] = item

    def add_item_scope(self, item_name: str, scope_name: str, replace_default_if_exists: bool=True):
        if item_name in self.items:
            self.items[item_name].add_scope(scope_name=scope_name, replace_default_if_exists=replace_default_if_exists)

    def add_link_to_parent_item(self, parent_item_name: str, sibling_item_name: str):
        if parent_item_name not in self.items:
            raise Exception('No item named "{}" found. Current items: {}'.format(parent_item_name, list(self.items.keys())))
        if sibling_item_name not in self.items:
            raise Exception('No item named "{}" found. Current items: {}'.format(sibling_item_name, list(self.items.keys())))
        any_scope_matches = False
        for parent_scope_name in self.items[parent_item_name].scopes:
            if parent_scope_name in self.items[sibling_item_name].scopes:
                any_scope_matches = True
        if any_scope_matches is False:
            self.logger.info('Parent scopes: {}'.format(self.items[parent_item_name].scopes))
            self.logger.info('Sibling scopes: {}'.format(self.items[sibling_item_name].scopes))
            raise Exception('At least one scope name must be present in both parent and sibling')
        self.items[sibling_item_name].add_parent_item_name(parent_item_name)

    def get_item_by_name(self, name: str)->Item:
        if name in self.items:
            return self.items[name]
        raise Exception('Item named "{}" not found, Current items: {}'.format(name, list(self.items.keys())))

    def find_first_matching_item_name_by_scope_name(self, scope_name: str)->str:
        for item_name, item_obj in self.items.items():
            if scope_name in item_obj.scopes:
                return item_name
        raise Exception('No matching items found for scope named "{}"'.format(scope_name))


def get_ordered_item_list_for_named_scope(items: Items, scope_name: str, start_item: Item, ordered_item_names: list=list(), logger: GenericLogger=GenericLogger())->list:
    logger.debug('   Evaluating item named "{}"'.format(start_item.name))
    parent_added = False
    if scope_name in start_item.scopes:
        if start_item.name not in ordered_item_names:
            ordered_item_names.append(start_item.name)
            logger.debug('      Adding start item "{}" to ordered list'.format(start_item.name))
        for item_name in start_item.parent_item_names:
            item = items.get_item_by_name(name=item_name)
            if scope_name in item.scopes:
                if item.name not in ordered_item_names:
                    start_item_idx = ordered_item_names.index(start_item.name)
                    ordered_item_names.insert(start_item_idx, item.name)
                    logger.debug('      Inserting item "{}" to ordered list before "{}"'.format(item.name, start_item.name))
                    parent_added = True
                    ordered_item_names = get_ordered_item_list_for_named_scope(
                        items=items,
                        scope_name=scope_name,
                        start_item=item,
                        ordered_item_names=copy.deepcopy(ordered_item_names)
                    )
                else:
                    logger.debug('      Item "{}" already in ordered list'.format(item.name))
    if parent_added is True:
        logger.debug('         Current ordered_item_names: {}'.format(ordered_item_names))
    return ordered_item_names

