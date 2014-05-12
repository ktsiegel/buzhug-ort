"""
A dummy class to use for serializer testing
"""
from base import Serializer

class Tree:
    def __init__(self, data_items, filename):
        self.serializer = Serializer(filename, Node)
        def nodes():
            for data_item in data_items:
                yield Node(serializer, **data_item)

        # first item in data_items is the root
        if data_items[0].get("pos") == None:
            # write all the nodes to disk for the first time
            self.root = serializer.write_nodes(nodes)
        else:
            self.root = serializer.deserialize_node(data_items[0]["pos"])


class Node:
    def __init__(self, serializer, value, data, min, max, children_pointers, 
            children, B, is_leaf, pos=None):

        for attr in ["serializer", "value", "data", "min", "max",
                "children_pointers", "children", "B", "is_leaf", "pos"]:
            # being lazy...
            setattr(self, attr, locals()[attr])

    def get_children(indices):
        pointers = [self.children_pointers[index] for index in indices]
        return serializer.loads(pointers)
