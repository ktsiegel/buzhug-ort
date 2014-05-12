from node import RangeNode
from tree import RangeTree

class RangeLeaf(RangeNode):
    def __init__(self, data, B):
        self.data = data
        self.min = min(data, key=lambda d: d[0][1])
        self.max = max(data, key=lambda d: d[0][1])
        self.B = B

        # Now we make the tree this node links to in the next dimension,
        # linked_tree.  We generate it by passing all of our data into a new
        # RangeTree object.  First, though, we have to re-order the dimensions
        # so that the next level sorts by the correct key.
        new_data = []
        for item in self.get_data():
            # stick the first data item in the back, and we're good
            new_data.append(item[1:] + [item[0]])
            # might as well set our dimension while we're at it
            self.dimension = item[0][0]

        # Next-level shit
        self.linked_leaf = RangeLeaf(new_data, B)

    def get_all_data(self):
        return self.data

    # Get the indices of data points bounded by the start and end values in
    # the first dimension.
    def get_range_data(self, start, end):
        # For each, we want the index of the first child whose minimum value is
        # greater than key.
        enum_values = ((index, point[0][1]) for index, point in
                enumerate(self.data))
        si = next(idx for idx, val in enum_values if val >= start,
                default=len(enum_values))
        ei = next(idx for idx, val in enum_values if val > end,
                default=len(enum_values))

        return self.data[si:ei]

    def range_query(self, ranges):
        # First get the left and right keys from the first dimension in
        # sorted order, then find their paths
        if self.dimension in ranges:
            (start, end) = ranges[self.dimension]
        else:
            # If there is no key in our dimension, go to the next-level leaf
            return self.linked_leaf.range_query(ranges)

        # If the next dimension is ours, search this tree. Otherwise move on to
        # the next dimension's tree and continue.
        # The query in the next dimension is everything other than this one.
        nranges = ranges.copy()
        del nranges[self.dimension]

        # The base case: there are no other dimensions to query, so return
        # all nodes in the range.
        if not nranges:
            return self.get_range_data(start, end)

        # Otherwise, search recursively on the nodes in the range.
        results = sorted(self.linked_leaf.range_query(nranges))

        # si & ei are the nodes containing the start and end of the range
        enum_values = ((index, point[0][1]) for index, point in
                enumerate(results))
        si = next(idx for idx, val in enum_values if val >= start,
                default=len(enum_values))
        ei = next(idx for idx, val in enum_values if val > end,
                default=len(enum_values))

        # We want to find all subtrees rooted between the two paths, and
        # recursively search those. Perform a (d-1)-dimensional query on the
        # linked trees of all of this node's children completely within the
        # range, and perform the same d-dimensional query on the nodes at
        # the edge of the range (lchild and rchild).
        results = []

        if ri > li:
            results.extend(rc.range_query(ranges))

        return results
        pass
