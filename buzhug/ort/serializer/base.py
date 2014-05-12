import cPickle

class Serializer:
    def __init__(self, filename, node_class):
        self.filename = filename
        self.node_class = node_class
        self.f = open(filename, 'a+')
        self.pos = 0
        # for testing: record how many backwards seeks are needed
        self.back_seeks = 0

    def dumps(self, nodes):
        """
        API call to serialize nodes and append them to file
        Sets positions of all nodes
        NOTE: this is going to be a dumb method...we should write nodes
        intelligently and call this method to write chunks of nodes at a time
        """
        [f.write(self._dump_node(node)) for node in nodes]
        for i, node in enumerate(nodes):
            node.pos = self.pos + i
        self.pos += len(nodes)

    def _dump_node(self, node):
        """
        given an instance of self.node_class, serialize it and return string 
        Override this method for different ways of serializing
        """
        # TODO: override here

        return "" 

    def finish_write(self):
        """
        API call when finished building tree
        can't read while still building
        """
        self.f.close()
        self.f = open(filename, 'r')
        self.pos = 0

    def loads(self, positions):
        """
        api call to load the nodes at a list of positions
        for now sort positions coming in
        """
        nodes = []
        for position in sorted(positions):
            if self.pos > position:
                self.back_seeks++
            self._seek(position - self.pos)
            nodes.append(self._load_node())
        return nodes

    def _load_node(self):
        """
        deserialize the bytes stored at offset in the tree file into
        self.node_class
        if no offset is specified, offset defaults to 0, the root
        """
        # TODO: override here
        
        return None 

    def _seek(self, offset):
        """
        Move from current position by given offset
        offset may be negative - seek backwards
        """
        # TODO: override here

        # always update current position in file 
        self.pos += offset
