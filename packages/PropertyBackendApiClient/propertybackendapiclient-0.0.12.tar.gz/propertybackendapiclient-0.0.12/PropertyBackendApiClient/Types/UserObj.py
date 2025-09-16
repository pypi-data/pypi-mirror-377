


class UserObj():
    jsondict = None
    def __init__(self, jsondict):
        self.jsondict = jsondict

    def getId(self):
        return self.jsondict["id"]
