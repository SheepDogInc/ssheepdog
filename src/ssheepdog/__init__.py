from ssh import pkey
from ssheepdog.utils import monkeypatch_class
from StringIO import StringIO

class PKey(pkey.PKey):
    __metaclass__ = monkeypatch_class
    def _read_private_key_file(self, tag, filename, password=None):
        if len(filename) > 300: # Assume it's already a key
            f = StringIO(filename)
        else:
            f = open(filename, 'r')
        data = self._read_private_key(tag, f, password)
        f.close()
        return data
