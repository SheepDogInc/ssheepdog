def read_file(filename):
    """
    Read data from a file and return it
    """
    f = open(filename)
    data = f.read()
    f.close()
    return data

def monkeypatch_class(name, bases, namespace):
    assert len(bases) == 1, "Exactly one base class required"
    base = bases[0]
    for name, value in namespace.iteritems():
        if name != "__metaclass__":
            setattr(base, name, value)
    return base

class DirtyFieldsMixin(object):
    """
    Store original plain fields (not foreign key fields) so that it's easy to
    detect which fields are dirty (i.e., have been altered.)
    """
    def __init__(self, *args, **kwargs):
        super(DirtyFieldsMixin, self).__init__(*args, **kwargs)
        self._original_state = self._as_dict()

    def _as_dict(self):
        return dict([(f.name, getattr(self, f.name)) for f in self._meta.local_fields if not f.rel])

    def get_dirty_fields(self):
        new_state = self._as_dict()
        return dict([(key, value) for key, value in self._original_state.iteritems() if value != new_state[key]])
