import os
import random

import tree
from serializer.line_serializer import LineSerializer

def build_test():
    data = []

    for j in range(10):
        data_item = [("field" + str(i), int(random.random() * 10)) for i in range(3)]
        data.append(data_item)

    tree_file = 'test-tree'
    if os.path.isfile(tree_file):
        os.remove(tree_file)
    serializer = LineSerializer(tree_file)

    root = tree.build_tree(data, 3, serializer)
    root2 = serializer.loads(root.linked_node) 
    root3 = serializer.loads(root2.linked_node)

    assert len(root.get_all_data()) == len(data) 
    assert len(root2.get_all_data()) == len(data) 
    assert len(root3.get_all_data()) == len(data) 

    print root.children
    
    assert False 
