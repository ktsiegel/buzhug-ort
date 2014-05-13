import os
from node import *
from serializer.line_serializer import LineSerializer

# Build a tree from a list of generic objects, represented as lists of (key,
# value) tuples. Each object should have the same d keys, each one of which
# maps to a comparable value. They should already be ordered. If they are
# not, everything will fuck up. Don't make everything fuck up.
# seq is the sequence of keys in the first item of the list of data.
def build_tree(data, B, serializer, first_dim=False):
    """
    data is list of lists of (k, v) pairs
    """
    serializer = LineSerializer(filename)
    # root will have a block position of 0
    if serialier.read_mode:
        # if we're already in read mode, then the file's already been built, so
        # return the last node in file
        # TODO: allow negative indexing for root node in serializer
        return serializer.loads(-1)

    # sort the fieldnames in each data item before doing field checks
    # last element of each data item is now a unique id for the record
    data = [data_item.sort(key=lambda field: field[0]) + [i] for i, data_item
            in enumerate(data)]    
    # If the sequence of keys is not the same in every other data item
    # as well, you fucked up. We make it immutable just to be safe.
    seq = tuple(d[0] for d in data[0][:-1])
    for item in data:
        if tuple(d[0] for d in item[0][:-1]) != seq:
            raise Exception('You fucked up. The sequence of keys is \
                    not the same in every data item.')

    # Now that we've got leaves, let's build their parents, recursively.
    build_upwards(data, B, RangeLeaf, serializer, first_dim=True)

    # should be done serializing
    serializer.flush()
    # and output the root
    return serializer.loads(0)

def build_upwards(data, B, NodeClass, serializer, children=None, first_dim=False):
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
    # if this is the lowest level, sort by keys and set the children
    if NodeClass == RangeLeaf:
        data.sort(key=lambda dp: dp[0][1])
        # set starts and ends for each child
        # if we're at the leaves, the start and end for a node is just its
        # index, index + 1
        children = [(data_item, i, i + 1) for i, data_item in enumerate(data)]
    parents = []

    num_clusters = len(children) / B
    if len(children) % B != 0:
        num_clusters += 1
    for i in range(num_clusters)
        # If there is more than one parent's worth of children, chop
        # off the first B in a chunk
        # TODO: this is a tuple...
        cluster = children[i * B:(i + 1) * B]
        cluster_start = cluster[0].start
        cluster_end = cluster[-1].end

        # serialize parent's linked tree in next dimension
        linked_root = None
        # if there's still another dimension, and the unique id in the data
        # items
        if len(data[0]) > 2:
            # build the next dimension
            # TODO: take only the data items corresponding to these children
            linked_data = [data_item[1:] for data_item in data[cluster_start : cluster_end]]
            linked_root = build_upwards(linked_data, B, RangeLeaf, serializer)
        parent = NodeClass(cluster, B, linked_root)

        # then serialize parent
        serializer.dumps(parent)

        # TODO: make sure that parents get accessed in right->left order on one
        # level
        parents.append((parent, cluster_start, cluster_end)) # and add it to our collection
        i += 1

    # If we ended up with more than one parent, we need to give them
    # their own parents.
    # R E C U R S E
    if len(parents) > 1:
        # On the recursive steps, the parents are always RangeNodes.
        return build_upwards(data, B, RangeNode, serializer, parents)

    return parents[0]

if __name__ == '__main__':
    data = [[(i, random.random()) for i in ['x', 'y', 'z']] for j in
            range(10**6)]
    B = 10
    tree = build_tree(data, B)
