from tree import build_tree

class RangeNode(object):
    def __init__(self, children, B):
        # This points to the node's children in the tree - each child is
        # represented as a (pointer, min, max) tuple.
        self.children = children
        self.dimension = None
        self.min = children[0][1]
        self.max = children[-1][2]
        self.B = B

        # This stores values for all of the node's children except for the
        # smallest one. This allows searching for a child quickly with >=
        # comparisons.
        self.values = [child[0] for child in children[1:]]

        # Now we make the tree this node links to in the next dimension,
        # linked_node.  We generate it by passing all of our data into a new
        # RangeTree object.  First, though, we have to re-order the dimensions
        # so that the next level sorts by the correct key.
        new_data = []
        for item in self.get_data():
            # stick the first data item in the back, and we're good
            ni = item[:]
            ni.append(ni.pop(0))
            new_data.append(ni)
            # might as well set our dimension while we're at it
            if not self.dimension:
                self.dimension = item[0][0]

        # Next-level shit
        self.linked_node = build_tree(new_data, B)

    # Return a string representing this node for printing.
    def __repr__(self):
        name = getattr(self, "children", 0) and "Branch" or "Leaf"
        return "<%s %s>" % (name, ", ".join(map(str, self.values)))

    # TODO: This should fetch the next child from disk and deserialize it. Use
    # only as necessary.
    def load_child(self, pointer):
        return api.load_child(pointer[0])

    # Make this node into a file for storage - TODO
    def serialize(self):
        pass

    # Return POINTER to the child which contains the leaf keyed by "key." return
    # value is a (child, index) tuple; "index" is child's position in values.
    # If key is out of our range, return None.
    def get_child_for(self, key):
        if key < self.min or key > self.max:
            return None

        # We want the index of the first child whose minimum value is greater
        # than key.
        index = next(idx for idx, val in enumerate(self.values) if val >= key,
                default=len(self.values))

        child = self.children[index]
        return (index, child)

    # Recursively chain get_child_for commands to make a path
    # TODO: This is never used, keeping it around because
    def get_path(self, key):
        next_c = get_child_for(self, key)
        if next_c:
            child = self.load_child(next_c[1])
            return [next_c] + child.get_path(key)

    # Enumerate all the data in the node's children, in order.
    def get_all_data(self):
        data = []
        for c in self.children:
            # Now we actually need to load into memory
            child = self.load_child(c)
            data.extend(child.get_all_data())

        # possible optimization:
        # data = map(RangeNode.get_all_data, children)

        return data

    # Get all the data in a range of values. A generalization of get_all_data.
    def get_range_data(self, start, end):
        # Get the indices of the children containing the start and end keys, or
        # note that they are out of our range.
        si = self.get_child_for(start)[0] if start >= self.min
                else -1
        ei = self.get_child_for(end)[0] if end >= self.max
                else len(self.children)

        data = []

        # First, recurse on the child containing the start key.
        if si >= 0:
            data.extend(self.children[si].get_range_data(start, end))

        # Next, grab everything from all the children in between start & end.
        if ei >= si + 2:
            for i in range(si + 1, ei):
                data.extend(self.children[i].get_all_data())

        # Recurse on the child containing the end key.
        if ei > si:
            data.extend(self.children[ei].get_range_data(start, end))

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
        # the next dimension's tree and continue.
        # The query in the next dimension is everything other than this one.
        nranges = ranges.copy()
        del nranges[self.dimension]

        # The base case: there are no other dimensions to query, so return
        # all nodes in the range.
        if not nranges:
            return self.get_range_data(start, end)

        # Otherwise, search recursively on the nodes in the range.
        # lchild & rchild are the nodes containing the start and end of the
        # range
        start_child = self.get_child_for(start)
        end_child = self.get_child_for(end)
        si, sc = start_child if start_child else (-1, None)
        ei, ec = end_child if end_child else (len(self.children), None)

        # We want to find all subtrees rooted between the two paths, and
        # recursively search those. Perform a (d-1)-dimensional query on the
        # linked trees of all of this node's children completely within the
        # range, and perform the same d-dimensional query on the nodes at
        # the edge of the range (lchild and rchild).
        res = [[]] * 3

        # First, get the results from all children fully contained in the range
        if ei - si >= 2:
            for i in range(si, ei):
                c = self.load_child(self.children[i])
                res[1].extend(c.linked_node.range_query(nranges))

        # Get the results of the query from the child containing the start of
        # the range
        if start_child:
            c = self.load_child(sc)
            res[0] = c.range_query(ranges)

        # Recurse on child containing end of range
        if end_child and ei > si:
            c = self.load_child(ec)
            res[2] = c.range_query(ranges)

        # join the lists
        res[0].extend(res[1])
        res[0].extend(res[2])
        return res[0]
