class Shader:
    def __init__(self, name, **properties):
        self.name = name
        self.properties = properties

    def uniforms(self):
        rv = {}

        for k, v in self.properties.iteritems():
            if callable(v):
                rv[k] = v()
            else:
                rv[k] = v

        return rv
