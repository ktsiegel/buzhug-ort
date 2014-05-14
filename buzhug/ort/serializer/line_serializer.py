import cPickle as pickle
from base import Serializer

class LineSerializer(Serializer):
    """
    Serialization scheme: variable-length cPickled node on each line
    """
    def flush(self, existing=False):
        Serializer.flush(self, existing)
        self.lines = iter(self.f)

    def _dump_node(self, node):
        # pickle and escape all newline characters
        line = pickle.dumps(node).replace('\n', '\\n')
        return line + '\n'

    def _load_node(self):
        # unenscape newline characters and unpickle
        line = self.lines.next().replace('\\n', '\n')
        self.pos += 1
        return pickle.loads(line)

    def _load_block(self):
        return self.lines.next()

    def _seek(self, position):
        offset = position - self.pos
        if offset < 0:
            # reset file position and iterator to beginning of file
            self.f.seek(0)
            self.pos = 0
            self.lines = iter(self.f)
            offset = position

        for i in range(offset):
            self.lines.next()

    def _get_block_count(self):
        with open(self.filename) as f:
            for i, l in enumerate(f):
                pass
        return i + 1
