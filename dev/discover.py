# Copyright 2019 by Sergio Valqui. All rights reserved.
# Discover object
# dicloses object types of an object recursively

class My_Object(object):
    def __init__(self):

    def show_me(self, item, indent="" ):
        if isinstance(item, dict):
            print(indent, "Dict Here")




