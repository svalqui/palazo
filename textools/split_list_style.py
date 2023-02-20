# Copyright 2019-2023 by Sergio Valqui. All rights reserved.

import sys


def split_list(my_list, spaces=8, items_per_line=4):
    edited_list = ''
    if isinstance(my_list, tuple) or isinstance(my_list, list) or isinstance(my_list, str):
        if isinstance(my_list,tuple):
            start_char = "("
            end_char = ")"
            print('This is a tuple')
        elif isinstance(my_list, list):
            start_char = "["
            end_char = "]"
            print('This is a list')
        elif isinstance(my_list, str):  # of type 1,2,3 or '1','2','3'
            start_char = ""
            end_char = ""
            my_list = my_list.split(',')
            print('This is a str')

#        line = " " * spaces + start_char
#        for counter, item in enumerate(my_list):
#            if counter % items_per_line == 0:
#                if counter == 0:
#                    line += '"' + item + '"' + ', '
#                else:
#                    line += '\n'
#                    edited_list += line
#                    line = " " * spaces + '"' + item + '"' + ', '
#            else:
#                line += '"' + item + '"' + ', '
#        line += '\n'
#        edited_list += line
#        edited_list += ' ' * spaces + end_char

        line = " " * spaces + start_char
        for counter, item in enumerate(my_list):
            if counter % items_per_line == 0:
                if counter == 0:
                    line += item.strip() + ', '
                else:
                    line += '\n'
                    edited_list += line
                    line = " " * spaces + item.strip() + ', '
            else:
                line += item.strip() + ', '
        line += '\n'
        edited_list += line
        edited_list += ' ' * spaces + end_char

    else:
        raise ValueError('Only for tuple and list, not for ', type(my_list))

    # print(edited_list)

    return edited_list


def main():
    my_filename = input("Filename :")
    my_line = input("Line :")
    my_spaces = input("Spaces :")
    items_per_line = input("Items per line :")
    print("========================")
    print("========================")
    print("========================")

    f_lines = []
    with open (my_filename, "r") as fh:
        for line in fh:
            f_lines.append(line.strip())

    source_line = f_lines[int(my_line) -1]

    edited_list = split_list(source_line, int(my_spaces), int(items_per_line))
    print(edited_list)


if __name__ == '__main__':
    sys.exit(main())




