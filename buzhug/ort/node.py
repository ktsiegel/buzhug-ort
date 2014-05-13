class RangeNode(object):

    # children is a sorted list of the node's children in the tree - each
    # child is represented as a (pointer, min, max) tuple.
    def __init__(self, children, linked_node, dim, serializer):
        self.children = children
        self.dimension = dim
        self.linked_node = linked_node
        self.serializer = serializer
        self.build()

    def build(self):
        self.min = self.children[0][1]
        self.max = self.children[-1][2]

        # This stores values for all of the node's children except for the
        # smallest one. This allows searching for a child quickly with >=
        # comparisons.
        self.values = [child[0] for child in self.children[1:]]

    # Return a string representing this node for printing.
    def __repr__(self):
        return "<Branch %s>" % ", ".join([self.dimension, str(self.pos)] +
                map(str, self.children))

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        self.build()

    def __getstate__(self):
        out = self.__dict__.copy()
        tdel = ['max', 'min', 'serializer', 'values']
        for key in tdel:
            del out[key]
        return out

    # Fetch the next child from disk and deserialize it. Use only as necessary.
    def load_child(self, (pointer, min, max)):
        return self.serializer.loads(pointer)

    # Return the child which contains the leaf keyed by "key." return value is a
    # (child, index) tuple; "index" is child's position in values, & child is a
    # (ptr, min, max) tuple. If key is out of our range, return None.
    def get_child_for(self, key):
        if key < self.min or key > self.max:
            return None

        # Get index for the first child whose minimum value is greater than key.
        index = next((idx for idx, val in enumerate(self.values) if val >= key),
                default=len(self.values))

        child = self.children[index]
        return (index, child)

    # Enumerate all the data in the node's children, in order.
    def get_all_data(self):
        data = []
        # traverse in reverse order, because that's how their laid out on disk
        for c in reversed(self.children):
            # Now we actually need to load into memory
            child = self.load_child(c)
            data.extend(child.get_all_data())

        # Possible optimization:
        # data = map(RangeNode.get_all_data, children)

        return data

    # Get all the data in a range of values. A generalization of get_all_data.
    def get_range_data(self, start, end):
        # Get the indices of the children containing the start and end keys, or
        # note that they are out of our range.
        si = self.get_child_for(start)[0] if start >= self.min \
                else -1
        ei = self.get_child_for(end)[0] if end >= self.max \
                else len(self.children)

        data = []

        # First, recurse on the child containing the end key.
        if ei > si:
            child = self.load_child(self.children[i])
            data.extend(self.children[ei].get_range_data(start, end))

        # Next, grab everything from all the children in between start & end.
        if ei >= si + 2:
            for i in reversed(xrange(si + 1, ei)):
                child = self.load_child(self.children[i])
                data.extend(child.get_all_data())

        # Recurse on the child containing the start key.
        if si >= 0:
            child = self.load_child(self.children[si])
            data.extend(self.children[si].get_range_data(start, end))

        return data

    # This is the main function we'll be using. 'ranges' should be a dict of
    # {dimension/column name: (start, end)}. Returns a list of items included in
    # the range from this node's subtree.
    def range_query(self, ranges):
        # First get the left and right keys from the first dimension in
        # sorted order, then find their paths
        if self.dimension in ranges:
            (start, end) = ranges[self.dimension]
        else:
            # If there is no key in our dimension, go to the next tree
            return self.linked_node.range_query(ranges)

        # If the next dimension is ours, search this tree. Otherwise move on to
        # the next dimension's tree and continue. The query in the next
        # dimension is everything other than this one.
        nranges = ranges.copy()
        del nranges[self.dimension]

        # The base case: this tree is in the last dimension, so return all nodes
        # in the range.
        if not self.linked_node:
            return self.get_range_data(start, end)

        # Otherwise, search recursively on the nodes in the range.
        # start_child & end_child are the nodes containing the start and end of
        # the range
        start_child = self.get_child_for(start)
        end_child = self.get_child_for(end)
        si, sc = start_child if start_child else (-1, None)
        ei, ec = end_child if end_child else (len(self.children), None)

        # We want to find all subtrees rooted between the two paths, and
        # recursively search those. Perform a (d-1)-dimensional query on the
        # linked trees of all of this node's children completely within the
        # range, and perform the same d-dimensional query on the nodes at
        # the edge of the range (lchild and rchild).
        results = []

        # Get the results from all children fully contained in the range,
        # in reverse order: that's how they're written to disk.
        # First, recurse on child containing end of range.
        if end_child and ei > si:
            c = self.load_child(ec)
            results.extend(c.range_query(ranges))

        # Now do all of the fully-contained children
        if ei - si >= 2:
            for i in reversed(xrange(si, ei)):
                c = self.load_child(self.children[i])
                results.extend(c.link().range_query(nranges))

        # Last, the child containing the start of the range
        if start_child:
            c = self.load_child(sc)
            results.extend(c.range_query(ranges))

        # BAM
        return results
