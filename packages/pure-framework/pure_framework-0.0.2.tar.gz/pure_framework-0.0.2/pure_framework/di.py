class Container:
    _services = {}

    @classmethod
    def provide(cls, name, cls_obj):
        cls._services[name] = cls_obj()

    @classmethod
    def inject(cls, name):
        return cls._services.get(name)
