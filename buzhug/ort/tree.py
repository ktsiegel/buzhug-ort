import os
from node import *
from serializer.line_serializer import LineSerializer

# Build a tree from a list of generic objects, represented as lists of (key,
# value) tuples. Each object should have the same d keys, each one of which
# maps to a comparable value. They should already be ordered. If they are
# not, everything will fuck up. Don't make everything fuck up.
# seq is the sequence of keys in the first item of the list of data.
def build_tree(data, B, filename):
    serializer = LineSerializer(filename)
    # root will have a block position of 0
    if serialier.read_mode:
        # if we're already in read mode, then the file's already been built, so
        # return the first node in file
        return serializer.loads(0)

    # If the sequence of keys is not the same in every other data item
    # as well, you fucked up. We make it immutable just to be safe.
    seq = tuple(d[0] for d in data[0])
    for item in data:
        if tuple(d[0] for d in item[0]) != seq:
            raise Exception('You fucked up. The sequence of keys is \
                    not the same in every data item.')

    # Now that everything is in order, we can proceed. Let's sort the
    # data by the first key in the sequence, which we'll call the
    # first "dimension."
    data.sort(key=lambda dp: dp[0][1])

    # Now that we've got leaves, let's build their parents, recursively.
    # serialize NOW! :)
    build_upwards(data, B, RangeLeaf, serializer)
    serializer.flush()
    # and output the root
    return serializer.loads(0)

def build_upwards(children, B, NodeClass, serializer):
    """
    Function to build nodes recursively, bottom-up. Takes chunks of B of
    whatever data type you pass into children, puts them into whatever class
    you set as NodeClass, and recurses up
    Tree gets built in reverse order of range query recursion, so after making
    the level with all the parents the serialization order here is:
        for each parent from left to right (okay to do range query from right to
        left on single level):
            - linked tree in next dimension
            - parent
        then recurse with the parents as the children of next level
    """
    parents = []
    
    i = 0
    while (i + 1) * B <= len(children):
        # If there is more than one parent's worth of children, chop
        # off the first B in a chunk
        cluster = children[i * B:(i + 1) * B]

        # serialize parent's linked tree in next dimension
        # TODO: fix this...
        build_tree(data, B)
        parent = NodeClass(cluster)
        # then serialize parent
        serializer.dumps([parent])

        parents.append(parent) # and add it to our collection
        i += 1

    # If we ended up with more than one parent, we need to give them
    # their own parents.
    # R E C U R S E
    if len(parents) > 1:
        # On the recursive steps, the parents are always RangeNodes.
        return build_upwards(parents, B, RangeNode, serializer)

if __name__ == '__main__':
    data = [[(i, random.random()) for i in ['x', 'y', 'z']] for j in
            range(10**6)]
    B = 10
    tree = build_tree(data, B)
