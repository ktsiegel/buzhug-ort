from node import *

class RangeTree(object):
    # Build a tree from a list of generic objects, represented as lists of (key,
    # value) tuples. Each object should have the same d keys, each one of which
    # maps to a comparable value. They should already be ordered. If they are
    # not, everything will fuck up. Don't make everything fuck up.
    # seq is the sequence of keys in the first item of the list of data.
    def __init__(self, data, B):
        self.B = B
        self.build_tree(data)

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
        # The output of the function is a single node: the root.
        self.root = build_upwards(data, RangeLeaf)

    # This is a function to build nodes recursively, bottom-up. It takes
    # chunks of B of whatever data type you pass into children, puts
    # them into whatever class you set as NodeClass, and recurses up.
    # I think bottom-up should minimize the total number of file blocks
    # the system uses compared to top-down, but could be wrong.
    def build_upwards(self, children, NodeClass):
        parents = []
        B = self.B # shortcutz
        while children:
            # If there are more than one parent's worth of children, chop
            # off the first B in a chunk
            if len(children) > B:
                cluster = children[:B]
                children = children[B:]
            else:
                cluster = children[:]
                children = []

            # actually make a parent
            parent = NodeClass(cluster[:]) # with a copy, no references
            parents.append(parent)  # and add it to our collection

        # If we ended up with more than one parent, we need to give them
        # their own parents.
        # R E C U R S E
        if len(parents) > 1:
            # On the recursive steps, the parents are always RangeNodes.
            return build_upwards(parents, RangeNode)

        # Otherwise, we've got the root. Bam.
        return parents[0]

    # This is the job of the node, not the tree. Hand off.
    def range_query(self, ranges):
        return self.root.range_query(ranges)


if __name__ == '__main__':
    data = [[(i, random.random()) for i in ['x', 'y', 'z']] for j in
            range(10**6)]
    B = 10
    tree = RangeTree(data, B)
