# Copyright 2021 by Sergio Valqui. All rights reserved.

# Navigating Object structures

def obj_struct(my_obj):

    for att in dir(my_obj):
        print(att, getattr(my_obj, att), type(getattr(my_obj, att)).__name__)
        #  TODO: Differentiate methods, other objects, known structures
        #  TODO: show values of known structures
        # TODO: make it recursive
