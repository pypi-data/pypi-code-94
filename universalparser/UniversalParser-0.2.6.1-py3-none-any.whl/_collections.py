from collections import OrderedDict
from typing import Any, Union
from ._tools import find_intersection
from ._ntype import SM
from functools import reduce

class ChainDict(OrderedDict):

    cdata_key = 'text_'
    switch_loc = True

    def __init__(self, objects):
        super(ChainDict, self).__init__()
        self.__objects__ = objects

    def __node_num(self):
        if self.switch_loc:
            return 2
        else:
            return 1

    def __getattr__(self, name):
        if not name.startswith('_'):
            if isinstance(self[name], dict) and self.__node_num() == len(self[name]) and self.cdata_key in self[name]:
                return self[name][self.cdata_key]
            else:
                return self[name]
        return super(ChainDict, self).__getattr__(name)

    def __setattr__(self, name, value):
        if name == self.cdata_key:
            pass
        if not name.startswith('_'):
            self[name] = value
        else:
            super(ChainDict, self).__setattr__(name, value)

    def __and__(self, mode: int) -> Any: # &
        mode_ways = {
            SM.text: self.__objects__.find_text,
            SM.attr_names: self.__objects__.get_attr_names,
            SM.tag: self.__objects__.get_tag,
            SM.ancestor: self.__objects__.get_ancestor,
            SM.descendants: self.__objects__.get_descendants,
            SM.siblings: self.__objects__.get_siblings,
            SM.children: self.__objects__.get_children,
            SM.parent: self.__objects__.get_parent,
        }
        if mode in mode_ways:
            return mode_ways[mode](self)
        else:
            raise TypeError('Output mode error.')

class ChainExpressionManager:

    SEARCH_ATTR_KEY: str = 'id'

    def __init__(self, manager, objects, nodes) -> None:
        self.manager = manager
        self.objects = objects

        self.index: int = 0
        self.nodes = nodes

    def __iter__(self):
        return self

    def __next__(self):
        if self.index < len(self.nodes):
            self.index += 1
            return self.nodes[self.index-1]
        else:
            raise StopIteration

    def __truediv__(self, text: str): # /
        self.index = 0
        temp_nodes = self.manager.find_nodes_by_text(text)
        descendants = reduce(lambda x,y:x+y, [_node&SM.descendants for _node in self.nodes]) if self.nodes else []
        self.nodes = find_intersection([self.nodes+descendants, temp_nodes])
        return self

    def __mod__(self, cdata: str): # %
        self.index = 0
        temp_nodes = self.manager.find_nodes_by_cdata(cdata)
        descendants = reduce(lambda x,y:x+y, [_node&SM.descendants for _node in self.nodes]) if self.nodes else []
        self.nodes = find_intersection([self.nodes+descendants, temp_nodes])
        return self

    def __floordiv__(self, comment: str): # //
        self.index = 0
        temp_nodes = self.manager.find_nodes_by_comment(comment)
        descendants = reduce(lambda x,y:x+y, [_node&SM.descendants for _node in self.nodes]) if self.nodes else []
        self.nodes = find_intersection([self.nodes+descendants, temp_nodes])
        return self

    def __or__(self, tag: str): # |
        self.index = 0
        temp_nodes = self.manager.find_nodes_by_tag(tag)
        descendants = reduce(lambda x,y:x+y, [_node&SM.descendants for _node in self.nodes]) if self.nodes else []
        self.nodes = find_intersection([self.nodes+descendants, temp_nodes])
        return self

    def __matmul__(self, attrs: Union[dict, str]): # @
        self.index = 0
        if isinstance(attrs, dict):
            temp_nodes = self.manager.find_nodes_by_attrs(**attrs)
        elif isinstance(attrs, str):
            temp_nodes = self.manager.find_nodes_by_attrs(**{self.SEARCH_ATTR_KEY: attrs})
        else:
            raise TypeError('`attrs` must be dict or str.')
        descendants = reduce(lambda x,y:x+y, [_node&SM.descendants for _node in self.nodes]) if self.nodes else []
        self.nodes = find_intersection([self.nodes+descendants, temp_nodes])
        return self

    def __xor__(self, count: int): # ^
        if 1 == count:
            if len(self.nodes) > 1:
                raise IndexError('More than one result.')
            if 0 <= count-1 < len(self.nodes):
                return self.nodes[count-1]
            else:
                raise IndexError('No nodes found.')
        elif count > 1:
            return self.nodes[:count]
        else:
            raise IndexError('`count` must be greater than or equal to 1.')
