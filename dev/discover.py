# Discover object
# discloses object types of an object recursively

import builtins


class ThisObject(object):
    def __init__(self, my_object):
        # self.builtin_types = [d for d in dir(builtins) if isinstance(getattr(builtins, d), type)]
        self.builtin_types = [getattr(builtins, d) for d in dir(builtins) if isinstance(getattr(builtins, d), type)]

    def check_obj(self, item, indent=""):
        # if is a builtin type
        if item.__class__ in self.builtin_types:
            # if is iterable
            try:
                iterator = iter(item)
            except TypeError:
                print("item: ", item, "  Not ITERABLE")
            else:
                for sub_item in item:
                    self.check_obj(sub_item)











#References
#https://stackoverflow.com/questions/3210238/how-do-i-get-list-of-all-python-types-programmatically#3222774

