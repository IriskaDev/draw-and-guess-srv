

def singleton(impl):
    ___instances = {}

    def wrapper():
        if impl not in ___instances:
            ___instances[impl] = impl()
        return ___instances[impl]

    return wrapper