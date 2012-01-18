def read_file(filename):
    """
    Read data from a file and return it
    """
    f = open(filename)
    data = f.read()
    f.close()
    return data
