import copy


class Item:

    def __init__(self, name):
        self.name = name
        self.parent_item_names = list()
        self.scopes = list()

    def add_parent_item_name(self, parent_item_name:str):
        if parent_item_name not in self.parent_item_names:
            self.parent_item_names.append(parent_item_name)

    def add_scope(self, scope_name: str):
        if scope_name not in self.scopes:
            self.scopes.append(scope_name)


class Items:

    def __init__(self):
        self.items = dict()

    def add_item(self, item: Item):
        if item.name not in self.items:
            self.items[item.name] = item

    def get_item_by_name(self, name: str)->Item:
        if name in self.items:
            return self.items[name]
        raise Exception('Item named "{}" not found'.format(name))

    def find_first_matching_item_name_by_scope_name(self, scope_name: str)->str:
        for item_name, item_obj in self.items.items():
            if scope_name in item_obj.scopes:
                return item_name
        raise Exception('No matching items found for scope named "{}"'.format(scope_name))


def add_item_parent(item: Item, parent_item: Item)->Item:
    item.add_parent_item_name(parent_item_name=parent_item.name)
    return item


def add_item_scope(item: Item, scope_name: str)->Item:
    item.add_scope(scope_name=scope_name)
    return item


def get_ordered_item_list_in_scope(scope_name: str, start_item: Item, items: Items, ordered_item_names: list=list())->list:
    print('   Evaluating item named "{}"'.format(start_item.name))
    parent_added = False
    if scope_name in start_item.scopes:
        if start_item.name not in ordered_item_names:
            ordered_item_names.append(start_item.name)
            print('      Adding start item "{}" to ordered list'.format(start_item.name))
        for item_name in start_item.parent_item_names:
            item = items.get_item_by_name(name=item_name)
            if scope_name in item.scopes:
                if item.name not in ordered_item_names:
                    start_item_idx = ordered_item_names.index(start_item.name)
                    ordered_item_names.insert(start_item_idx, item.name)
                    print('      Inserting item "{}" to ordered list before "{}"'.format(item.name, start_item.name))
                    parent_added = True
                    ordered_item_names = get_ordered_item_list_in_scope(
                        scope_name=scope_name,
                        start_item=item,
                        items=items,
                        ordered_item_names=copy.deepcopy(ordered_item_names)
                    )
                else:
                    print('      Item "{}" already in ordered list'.format(item.name))
    if parent_added is True:
        print('         Current ordered_item_names: {}'.format(ordered_item_names))
    return ordered_item_names


if __name__ == '__main__':
    item1 = Item(name='1')
    item1 = add_item_scope(item=item1, scope_name="A")
    item1 = add_item_scope(item=item1, scope_name="B")
    
    item2 = Item(name='2')
    item2 = add_item_scope(item=item2, scope_name="A")
    
    item3 = Item(name='3')
    item3 = add_item_scope(item=item3, scope_name="A")
    item3 = add_item_scope(item=item3, scope_name="B")
    
    item4 = Item(name='4')
    item4 = add_item_scope(item=item4, scope_name="A")

    """
    Item Hierarchy in scope A:

        Item 1 parents:
            Item 2
            Item 3

        Item 2 parents:
            Item 4

        Item 3 parent:
            Item 4

    So, when we want to get the order of processing in item order from item 1, we should get:

        Item 4, Item 2, Item 3, Item 1

    Item Hierarchy in scope B:

        Item 1 parents:
            Item 3

    So, when we want to get the order of processing in item order from item 1, we should get:

        Item 3, Item 1
    """
    item1 = add_item_parent(item=item1, parent_item=item2)
    item1 = add_item_parent(item=item1, parent_item=item3)
    item2 = add_item_parent(item=item2, parent_item=item4)
    item3 = add_item_parent(item=item3, parent_item=item4)

    items = Items()
    items.add_item(item = item1)
    items.add_item(item = item2)
    items.add_item(item = item3)
    items.add_item(item = item4)

    print('Item 1 parents: {}'.format(item1.parent_item_names))
    print('Items : Item 1 parents: {}'.format(items.items[item1.name].parent_item_names))

    print('Running Test 1')
    start_item = items.get_item_by_name(name='1')
    ordered_item_names = get_ordered_item_list_in_scope(scope_name='A', start_item=start_item, items=items, ordered_item_names=[start_item.name])
    print('   TEST 1: Scope A, Ordered items for start item {}: {}'.format(start_item.name, ordered_item_names))
    print()

    print('Running Test 2')
    start_item_name = items.find_first_matching_item_name_by_scope_name(scope_name='A')
    start_item = items.items[start_item_name]
    ordered_item_names = get_ordered_item_list_in_scope(scope_name='A', start_item=start_item, items=items, ordered_item_names=[start_item.name])
    print('   TEST 2: Scope A, Ordered items for start item {}: {}'.format(start_item.name, ordered_item_names))
    print()

    print('Running Test 3')
    start_item_name = items.find_first_matching_item_name_by_scope_name(scope_name='B')
    start_item = items.items[start_item_name]
    ordered_item_names = get_ordered_item_list_in_scope(scope_name='B', start_item=start_item, items=items, ordered_item_names=[start_item.name])
    print('   TEST 3: Scope B, Ordered items for start item {}: {}'.format(start_item.name, ordered_item_names))

