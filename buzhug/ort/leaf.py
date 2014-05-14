from node import RangeNode

class RangeLeaf(RangeNode):

    # Initialize a leaf with a *sorted* set of data points
    def __init__(self, data, linked_node, dim, prev):
        # [(id, value), ..., ]
        self.data = data
        self.dimension = dim
        self.linked_node = linked_node
        self.prev = prev
        self.build()

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
        return self.serializer.loads(self.linked_node)

    def load_prev(self):
        if self.prev:
            return self.serializer.loads(self.prev)
        else:
            return None

    # Get all data in the specified range - recurse on the previous leaf if this
    # one doesn't have the start value in its range.
    def get_range_data(self, start, end, recurse=True):
        # Figure out how much of our data falls in the given range.
        enum_values = enumerate(self.data)
        si = next((idx for idx, val in enum_values if val[1] >= start),
                  len(self.data))
        ei = next((idx for idx, val in enum_values if val[1] > end),
                  len(self.data))

        # Get our slice of the data.
        data = self.data[si:ei]

        # Either return what we have, or recurse on our predecessor node.
        if recurse and start <= self.min and self.prev:
            ret = self.load_prev().get_range_data(start, end)
            ret.extend(data)
            return ret
        return data

    # Return everything in this leaf for the specified ranges
    def range_query(self, ranges):
        # If the next dimension is ours, search this leaf.
        if self.dimension in ranges:
            (start, end) = ranges[self.dimension]
        else:
            # If there is no key in our dimension, go to the next-level leaf
            return self.link().range_query(ranges)

        # The query in the next dimension includes all ranges minus this one.
        nranges = ranges.copy()
        del nranges[self.dimension]

        # The base case: there are no other dimensions to query, so return
        # all nodes in the range.
        if not self.linked_node:
            return self.get_range_data(start, end)

        # We want to recurse down to the last dimension, and return everything
        # that fits all the ranges. Perform a (d-1)-dimensional query on our
        # linked leaf, and return the union of that result and our range.
        lleaf = self.link()
        their_results = map(lambda r: [r[0], (lleaf.dimension, r[1])],
                            lleaf.range_query(nranges))
        my_indices = set(i[0] for i in self.get_range_data(
                         start, end, recurse=False))

        # Check each one of the lower level's results to see if it's included in
        # our range. If so, stick on our data item and return.
        filtered = [r for r in their_results if r[0] in my_indices]
        mapped = map(lambda r: [r[0], (self.dimension, ), r[1]], their_results)

        return mapped
