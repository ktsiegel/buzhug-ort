import os
import tree
from serializer.line_serializer import LineSerializer

def build_test():
    data = []

    for j in range(10):
        data_item = [("field" + str(i), i * j) for i in range(3)]
        data.append(data_item)

    tree_file = 'test-tree'
    if os.path.isfile(tree_file):
        os.remove(tree_file)
    serializer = LineSerializer(tree_file)

    root = tree.build_tree(data, 3, serializer)
    print root
    raise Exception
