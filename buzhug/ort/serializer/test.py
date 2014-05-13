import os

from line_serializer import LineSerializer
from node_class import Node 

serializer = LineSerializer

def basic_flush_test():
    tree_file = 'test'
    print "testing serializer", serializer.__name__

    if os.path.isfile(tree_file):
        os.remove(tree_file)

    s = serializer(tree_file) 
    node1 = Node(s, **{'min' : 10})
    node2 = Node(s, **{'max' : 100})
    s.dumps_many([node1, node2])
    s.flush()
    
    assert node1.pos == 0
    assert node2.pos == 1

    # nodes get written backwards after flush, so on disk it's actually
    # [node2, node1]
    serialized = s.loads(node1.pos)
    assert serialized.min == 10

    serialized = s.loads(node2.pos)
    assert serialized.max == 100

    assert s.back_seeks == 1

    s.kill()

    # check that we can still load nodes after killing and restarting the
    # serializer from a tree file that's already built
    s = serializer(tree_file)

    serialized = s.loads(node1.pos)
    print serialized.__dict__
    assert serialized.min == 10

    serialized = s.loads(node2.pos)
    assert serialized.max == 100

