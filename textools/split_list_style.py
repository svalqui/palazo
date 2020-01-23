# Copyright 2019 by Sergio Valqui. All rights reserved.

import sys


def split_list(my_list, spaces=8, items_per_line=4):
    edited_list = ''
    if isinstance(my_list, tuple) or isinstance(my_list,list):
        if isinstance(my_list,tuple):
            start_char = "("
            end_char = ")"
            print('This is a tuple')
        else:
            start_char = "["
            end_char = "]"
            print('This is a list')

        line = " " * spaces + start_char
        for counter, item in enumerate(my_list):
            if counter % items_per_line == 0:
                if counter == 0:
                    line += '"' + item + str(counter) + '"' + ', '
                else:
                    line += '\n'
                    edited_list += line
                    line = " " * spaces + '"' + item + str(counter) + '"' + ', '
            else:
                line += '"' + item + str(counter) + '"' + ', '
        line += '\n'
        edited_list += line
        edited_list += ' ' * spaces + end_char

    else:
        raise ValueError('Only for tuple and list, not for ', type(my_list))

    print(edited_list)

    return edited_list


if __name__ == '__main__':
    sys.exit(main())




