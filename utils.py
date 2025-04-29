class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False



class StringArrayProxy(str):
    def __eq__(self, _):
        return isinstance(_, list) and all(isinstance(i, str) for i in _)

    def __ne__(self, _):
        return not self.__eq__(_)