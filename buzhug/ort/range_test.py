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

    root1 = tree.build_tree(data, 3, serializer)
    root2 = serializer.loads(root1.linked_node) 
    root3 = serializer.loads(root2.linked_node)

    dim1 = [data_item[1] for data_item in
            sorted((data_item[0] for data_item in data), key=lambda d: d[1])]
    dim2 = [data_item[1] for data_item in
            sorted((data_item[1] for data_item in data), key=lambda d: d[1])]
    dim3 = [data_item[1] for data_item in
            sorted((data_item[2] for data_item in data), key=lambda d: d[1])]

    # make sure all the roots have all values at bottom
    assert len(root1.get_all_data()) == len(data) 
    assert len(root2.get_all_data()) == len(data) 
    assert len(root3.get_all_data()) == len(data) 

    for root, dim in zip([root1, root2, root3], [dim1, dim2, dim3]):
        root_children = [root.load_child(child) for child in root.children]
        root_grandchildren = [child.load_child(grandchild) for child in
                root_children for grandchild in child.children]

        # test the intervals of the root's children
        assert root_children[0].min == dim[0]
        assert root_children[0].max == dim[8]
        assert root_children[1].min == dim[9]
        assert root_children[1].max == dim[9]

        for i in range(3):
            # test the intervals of the root's grandchildren: leaves
            assert root_grandchildren[i].min == dim[i * 3]
            assert root_grandchildren[i].max == dim[i * 3 + 2]

            # test the linked list at the leaves
            if i != 0:
                assert root_grandchildren[i].prev == \
                    root_grandchildren[i - 1].pos

    print serializer.back_seeks
