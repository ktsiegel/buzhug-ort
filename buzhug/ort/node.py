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
        #self.values = [child[1] for child in self.children[1:]]

    # Return a string representing this node for printing.
    def __repr__(self):
        return "<Branch %s>" % ", ".join([self.dimension, str(self.pos)] +
                map(str, self.children))

    def __setstate__(self, dict):
        self.__dict__.update(dict)
        self.build()

    def __getstate__(self):
        out = self.__dict__.copy()
        tdel = ['max', 'min', 'serializer']
        for key in tdel:
            del out[key]
        return out

    # Fetch the next child from disk and deserialize it. Use only as necessary.
    def load_child(self, (pointer, min, max)):
        return self.serializer.loads(pointer)

    def link(self):
        return self.serializer.loads(self.linked_node)

    # Return the child which contains the leaf keyed by "key." return value is a
    # (child, index) tuple; "index" is child's position in values, & child is a
    # (ptr, min, max) tuple. If key is out of our range, return None.
    def successor(self, key, suc):
        #if suc and key < self.min:
        #    return -1 
        #if not suc and key > self.max:
        #    return len(self.children)

        # Get index for the first child whose minimum value is greater than key.
        enums = enumerate(self.children)
        if suc:
            enums = reversed(list(enums))

        for idx, (p, min, max) in enums:
            if suc and max >= key:
                return idx
            if not suc and min <= key:
                return idx

        return None 

    # Returns all data in the tree. Not used except for debugging.
    def get_all_data(self):
        print self.min - 1, self.max + 1
        return self.get_range_data(self.min - 1, self.max + 1)

    # Get all the data in a range of values.
    def get_range_data(self, start, end):
        #if start > self.max:
        #    return []

        # Get the index of the child containing the end key, or note that it's
        # out of our range.
        # TODO
        idx = self.successor(end, True)
        if idx is None:
            idx = -1
        #if end > self.max:
        #    idx = -1
        #else:
        #    idx = self.successor(end)[0]

        # Recurse on the child containing the end key.
        child = self.load_child(self.children[idx])
        return child.get_range_data(start, end)

    # This is the main function we'll be using. 'ranges' should be a dict of
    # {dimension/column name: (start, end)}. Returns a list of items included in
    # the range from this node's subtree.
    def range_query(self, ranges):
        print 'Me! dim =', self.dimension, 'children =', len(self.children), \
                'values =', self.values

        # First get the left and right keys from the first dimension in
        # sorted order, then find their paths
        if self.dimension in ranges:
            (start, end) = ranges[self.dimension]
        else:
            # If there is no key in our dimension, go to the next tree
            if self.linked_node is None:
                return self.get_all_data()
            else:
                return self.link().range_query(ranges)

        # If the next dimension is ours, search this tree. Otherwise move on to
        # the next dimension's tree and continue. The query in the next
        # dimension is everything other than this one.
        nranges = ranges.copy()
        del nranges[self.dimension]

        # The base case: this tree is in the last dimension, so return all nodes
        # in the range.
        if self.linked_node is None:
            print self.dimension
            return self.get_range_data(start, end)

        # Otherwise, search recursively on the nodes in the range.
        # start_child & end_child are the nodes containing the start and end of
        # the range
        # TODO
        si = self.successor(start, True)
        ei = self.successor(end, False)

        # We want to find all subtrees rooted between the two paths, and
        # recursively search those. Perform a (d-1)-dimensional query on the
        # linked trees of all of this node's children completely within the
        # range, and perform the same d-dimensional query on the nodes at
        # the edge of the range (lchild and rchild).
        results = []

        # Get the results from all children fully contained in the range,
        # in reverse order: that's how they're written to disk.

        # First do all of the fully-contained children
        if ei - si >= 2:
            for i in reversed(xrange(si, ei)):
                c = self.load_child(self.children[i])
                # We know the child has a link because it's the same dimension
                results.extend(c.link().range_query(nranges))

        # Then recurse on child containing end of range.
        if ei < len(self.children):
        #if end_child and ei > si:
            c = self.load_child(self.children[ei])
            results.extend(c.range_query(ranges))

        # Last, the child containing the start of the range
        #if start_child:
        if si > -1 and si != ei:
            c = self.load_child(self.children[si])
            results.extend(c.range_query(ranges))

        # BAM
        return results
