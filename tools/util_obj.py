# Copyright 2021-2023 by Sergio Valqui. All rights reserved.

# Navigating Object structures


def look_for_obj_by_att_val(my_obj_list, my_att, my_value):
    """Search for an Obj with an attribute of a given value, for methods that return list of Obj."""

    ret_obj = None
    for my_obj in my_obj_list:
        if my_att in dir(my_obj):
            # print(getattr(my_obj, my_att), my_value)
            if getattr(my_obj, my_att) == my_value:
                ret_obj = my_obj
                break
    return ret_obj


def print_structure(my_obj, geta=True, my_space=''):
    """Prints attributes of an Obj."""
    for att in dir(my_obj):
        if geta:
            print(my_space, att, getattr(my_obj, att), type(getattr(my_obj, att)).__name__)
            if type(getattr(my_obj, att)).__name__ == 'dict':
                my_space += '  '
                print_structure(att,True, my_space)

        else:
            print(att, type(getattr(my_obj, att)).__name__)

def print_structure_det(my_obj, geta=True, my_space=''):
    """Prints attributes of an Obj."""
    abs_type = type(my_obj).__name__
    print("OBJ type :", abs_type)

    if abs_type == 'list':
        for i in my_obj:
            list_obj = i
            list_obj_type = type(list_obj).__name__
            # print(list_obj, list_obj_type, " in abs list")
            if list_obj_type == 'list':
                # print(my_space, "-- abs list in list")
                # print(my_space, list_obj_type)
                my_space += "  "
                print_structure_det(list_obj, True, my_space)

            elif list_obj_type == 'dict':
                # print(my_space, "-- abs dict in list")
                # print(my_space, list_obj_type)
                # print(list_obj.keys())
                my_space += "  "
                print_structure_det(list_obj, True, my_space)
            else:
                print(my_space, list_obj, list_obj_type)

    elif abs_type == 'dict':
        if len(my_obj) > 0:
            print(my_space, "-- abs dict")
            # print(my_obj.keys())
            my_space += "  "
            for k in my_obj.keys():
                val_obj = my_obj[k]
                my_val_type = type(val_obj).__name__
                # print(my_space, k, val_obj, my_val_type)
                if my_val_type == 'dict':
                    # print(my_space, "-- abs dict in dict")
                    # print(my_space, k, val_obj, my_val_type)
                    if len(val_obj) > 0:
                        my_space += "  "
                        print(my_space, "-- abs dict in dict - sending ", k, my_val_type, " to print_structure")
                        print_structure_det(val_obj, True, my_space)
                elif my_val_type == 'list':
                    # print(my_space, "-- abs list in dict")
                    # print(my_space, k, val_obj, my_val_type)
                    if len(val_obj) > 0:
                        my_space += "  "
                        print(my_space, "-- abs list in dict - sending ", k, my_val_type,
                              " to print_structure")
                        print_structure_det(val_obj, True, my_space)
                elif my_val_type == 'str':
                    print(my_space, k, val_obj, my_val_type)
                elif my_val_type == 'int':
                    print(my_space, k, val_obj, my_val_type)
                elif my_val_type == 'float':
                    print(my_space, k, val_obj, my_val_type)
                elif my_val_type == 'bool':
                    print(my_space, k, val_obj, my_val_type)
                elif my_val_type == 'NoneType':
                    print(my_space, k, val_obj, my_val_type)
                else:
                    print(my_space, '=> ', k, val_obj, my_val_type)

    else: # If is a Class

        for att in dir(my_obj):
            if geta:
                new_obj = getattr(my_obj, att)
                my_obj_type = type(new_obj).__name__
                # print(my_space, att, new_obj, my_obj_type)
                if not att.startswith('__'): # not builtin
                    #if my_obj_type != 'builtin_function_or_method':
                    #   print("++", my_obj_type)
                    if my_obj_type == 'dict':
                        if len(new_obj) > 0:
                            # print(my_space,"-- dict")
                            # print(my_space, att, new_obj, my_obj_type, "Class - dict in class")
                            # print(new_obj.keys())
                            my_space += "  "
                            for k in new_obj.keys():
                                val_obj = new_obj[k]
                                my_val_type = type(val_obj).__name__
                                # print(my_space, k, val_obj, my_val_type)
                                if my_val_type == 'dict':
                                    # print(my_space, "-- dict in dict")
                                    # print(my_space, k, val_obj, my_val_type)
                                    if len(val_obj) > 0:
                                        my_space += "  "
                                        print(my_space, "sending ", k, my_val_type, " to print_structure, Class dict in dict")
                                        print_structure_det(val_obj, True, my_space)
                                elif my_val_type == 'list':
                                    # print(my_space, "-- list in dict")
                                    # print(my_space, k, val_obj, my_val_type)
                                    if len(val_obj) > 0:
                                        my_space += "  "
                                        print(my_space, "-- list in dict - sending ", k, my_val_type,
                                              " to print_structure, Class list in dict")
                                        print_structure_det(val_obj, True, my_space)
                                elif my_val_type == 'str':
                                    print(my_space, k, val_obj, my_val_type)
                                elif my_val_type == 'int':
                                    print(my_space, k, val_obj, my_val_type)
                                elif my_val_type == 'float':
                                    print(my_space, k, val_obj, my_val_type)
                                elif my_val_type == 'bool':
                                    print(my_space, k, val_obj, my_val_type)
                                elif my_val_type == 'NoneType':
                                    print(my_space, k, val_obj, my_val_type)
                                else:
                                    print(my_space, '=> ', k, val_obj, my_val_type)


                    elif my_obj_type == 'list':
                        for i in new_obj:
                            list_obj = i
                            list_obj_type = type(list_obj).__name__
                            print(my_space, list_obj, list_obj_type, "Class list in class")
                            if list_obj_type == 'dict':
                                # print(my_space, "-- dict in list")
                                # print(my_space, att, i, list_obj_type)
                                # print(new_obj.keys())
                                my_space += "  "
                                print(my_space, att, "sending dict",
                                      " to print_structure, Class dict in list")
                                print_structure_det(list_obj, True, my_space)
                            elif list_obj_type == 'list':
                                if len(list_obj) > 0:
                                    my_space += "  "
                                    print(my_space, "-- list in list - sending list to print_structure, Class list in list")
                                    print_structure_det(list_obj, True, my_space)
                            elif list_obj_type == 'str':
                                print(my_space, list_obj, list_obj_type)
                            elif list_obj_type == 'int':
                                print(my_space, list_obj, list_obj_type)
                            elif list_obj_type == 'float':
                                print(my_space, list_obj, list_obj_type)
                            elif list_obj_type == 'bool':
                                print(my_space, list_obj, list_obj_type)
                            elif list_obj_type == 'NoneType':
                                print(my_space, list_obj, list_obj_type)
                            else:
                                print(my_space, '=> ', k, val_obj, my_val_type, "Class list member")

                    elif my_obj_type == 'str':
                        print(my_space, att, new_obj, my_obj_type)
                    elif my_obj_type == 'NoneType':
                        print(my_space, att, new_obj, my_obj_type)
                    elif my_obj_type == 'int':
                        print(my_space, att, new_obj, my_obj_type)
                    elif my_obj_type == 'float':
                        print(my_space, att, new_obj, my_obj_type)
                    elif my_obj_type == 'bool':
                        print(my_space, att, new_obj, my_obj_type)
                    elif my_obj_type == 'builtin_function_or_method':
                        continue
                    else:
                        print(my_space, '-> ' , att, new_obj, my_obj_type)

            else:
                print(att, type(getattr(my_obj, att)).__name__)
