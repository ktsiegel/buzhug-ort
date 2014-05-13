from node import RangeNode

class RangeLeaf(RangeNode):

    # Initialize a leaf with a *sorted* set of data points
    def __init__(self, data, linked_leaf, dim, prev, full_data=None):
        # [(id, value), ..., ]
        self.data = data
        self.dimension = dim
        self.linked_leaf = linked_leaf
        self.full_data = full_data
        self.build()
        self.prev = prev

    def build(self):
        self.min = min(data_item[1] for data_item in self.data)
        self.max = max(data_item[1] for data_item in self.data)

    # Return a string representing this node for printing.
    def __repr__(self):
        return "<Leaf %s>" % ", ".join([self.dimension, str(self.pos)] +
                map(str, self.data))

    def __getstate__(self):
        out = self.__dict__.copy()
        tdel = ['max', 'min']
        for key in tdel:
            del out[key]
        return out

    def link(self):
        return self.serializer.loads(self.linked_leaf)

    # Get the indices of data points bounded by the start and end values in the
    # first dimension.
    def get_range_data(self, start, end):
        # For each, we want the index of the first child whose minimum value is
        # greater than key.
        enum_values = ((index, point[0][1]) for index, point in
                enumerate(self.data))
        si = next((idx for idx, val in enum_values if val >= start),
                default=len(enum_values))
        ei = next((idx for idx, val in enum_values if val > end),
                default=len(enum_values))

        if self.full_data:
            return self.full_data[si:ei]
        return self.data[si:ei]

    # Return everything in this leaf for the specified ranges
    def range_query(self, ranges):
        # First get the left and right keys from the first dimension in
        # sorted order, then find their paths
        if self.dimension in ranges:
            (start, end) = ranges[self.dimension]
        else:
            # If there is no key in our dimension, go to the next-level leaf
            return self.linked_leaf.range_query(ranges)

        # If the next dimension is ours, search this leaf. Otherwise move on to
        # the next dimension's leaf and continue.
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
        my_indices = set(i[-1] for i in self.get_range_data(start, end))

        # Check each one of the lower level's results to see if it's included in
        # our range.
        return [r for r in their_results if r[-1] in my_indices]
