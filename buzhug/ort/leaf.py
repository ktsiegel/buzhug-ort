from node import RangeNode
from tree import RangeTree

class RangeLeaf(RangeNode):

    # Initialize a leaf with a sorted set of data points
    def __init__(self, data, B, dim):
        self.data = map(lambda p: {k: v for k, v in p}, data)
        self.dimension = data[0][0][0]  # ewwww
        self.min = min(data, key=lambda d: d[0][1])
        self.max = max(data, key=lambda d: d[0][1])
        self.B = B

        # Now we make the leaf this node links to in the next dimension.
        # Generate it by passing all of our data into a new RangeLeaf object.
        # First, though, we have to re-order the dimensions so that the next
        # level sorts by the correct key.
        for item in data:
            # stick the first data item in the back, and we're good
            item.append(item.pop(0))

        # Next-level shit
        self.linked_leaf = RangeLeaf(data, B)

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

        # We want to recurse down to the last dimension, and return everything
        # that fits all the ranges. Perform a (d-1)-dimensional query on our
        # linked leaf, and return the union of that result and our range.
        their_results = self.linked_leaf.range_query(nranges)
        my_results = set(self.get_range_data(start, end))

        # TODO: make this better?
        return = [r for r in their_results if r in my_results]
