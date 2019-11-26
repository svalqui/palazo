# Copyright 2019 by Sergio Valqui. All rights reserved.


def split_list(my_list, indentation_spaces=8, items_per_line=4):
    edited_list = ''
    if isinstance(my_list, tuple):
        line = " " * indentation_spaces + "("
        for counter, item in enumerate(my_list):
            if (counter + 1) % items_per_line != 0:
                line += '"' + item + '"' + ', '
            else:
                line += '\n'
                edited_list += line
                line = " " * indentation_spaces + '"' + item + '"' + ', '





