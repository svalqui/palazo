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
                print(att, my_obj.attr)

        else:
            print(att, getattr(my_obj, att), type(getattr(my_obj, att)).__name__)

def print_structure_det(my_obj, geta=True, my_cosmetic='', my_name=''):
    """Prints attributes of an Obj."""
    # TODO choose to print builtins or not __something
    # TODO review private attrs, choose print them or not, _something
    abs_type = type(my_obj).__name__
    # print("OBJ Name: ", my_name, " OBJ type: ", abs_type)

    if abs_type == 'list':
        print("OBJ Name: ", my_name, " OBJ type: List")
        if len(my_obj) > 0:
            for i in my_obj:
                list_obj = i
                list_obj_type = type(list_obj).__name__
                # print(list_obj, list_obj_type, " in abs list")
                if list_obj_type == 'list':
                    # print(my_space, "-- abs list in list")
                    # print(my_space, list_obj_type)
                    print(my_cosmetic, "-- abs list in List - sending list to print_structure")
                    my_cosmetic += "L->"  # List
                    print_structure_det(list_obj, True, my_cosmetic)

                elif list_obj_type == 'dict':
                    # print(my_space, "-- abs dict in list")
                    # print(my_space, list_obj_type)
                    # print(list_obj.keys())
                    print(my_cosmetic, i, "is a dict -- abs dict in List - sending dict to print_structure")
                    my_cosmetic += "D->"  # Dictionary
                    print_structure_det(list_obj, True, my_cosmetic)
                else:
                    print(my_cosmetic, list_obj, list_obj_type)
        else:
            print(my_cosmetic + "[]")

    elif abs_type == 'dict':
        print("OBJ Name: ", my_name, " OBJ type: ", abs_type, " Dict")
        if len(my_obj) > 0:
            # print(my_cosmetic, "-- abs dict")
            # print(my_obj.keys())
            for k in my_obj.keys():
                val_obj = my_obj[k]
                my_val_type = type(val_obj).__name__
                # print(my_space, k, val_obj, my_val_type)
                if my_val_type == 'dict':
                    # print(my_space, "-- abs dict in dict")
                    # print(my_space, k, val_obj, my_val_type)
                    if len(val_obj) > 0:
                        print(my_cosmetic, " abs dict in k value - sending ", k, my_val_type, " to print_structure")
                        my_cosmetic += "['" + k + "']"  # Dictionary in key value
                        print_structure_det(val_obj, True, my_cosmetic, k)
                elif my_val_type == 'list':
                    # print(my_space, "-- abs list in dict")
                    # print(my_space, k, val_obj, my_val_type)
                    if len(val_obj) > 0:
                        print(my_cosmetic, k, "is a List -- abs list in Dict att - sending ", my_val_type,
                              " to print_structure")
                        my_cosmetic += "['" + k + "']"  # List in key value
                        print_structure_det(val_obj, True, my_cosmetic)
                elif my_val_type == 'str':
                    print(my_cosmetic, k, val_obj, my_val_type)
                elif my_val_type == 'int':
                    print(my_cosmetic, k, val_obj, my_val_type)
                elif my_val_type == 'float':
                    print(my_cosmetic, k, val_obj, my_val_type)
                elif my_val_type == 'bool':
                    print(my_cosmetic, k, val_obj, my_val_type)
                elif my_val_type == 'NoneType':
                    print(my_cosmetic, k, val_obj, my_val_type)
                else:
                    print(my_cosmetic, '=> ', k, val_obj, my_val_type)
        else: # if dict is empty
            print(my_cosmetic + "[]")

    else: # If is a Class
        print("OBJ Name: ", my_name, " OBJ type: ", abs_type, " Class")
        for att in dir(my_obj):
            if geta:
                new_obj = getattr(my_obj, att)
                my_obj_type = type(new_obj).__name__
                # print(my_cosmetic, att, new_obj, my_obj_type)
                if not att.startswith('__'): # not builtins
                    #if my_obj_type != 'builtin_function_or_method':
                    #   print("++", my_obj_type)
                    # print(my_cosmetic, att, my_obj_type)
                    if my_obj_type == 'dict':
                        if len(new_obj) > 0:
                            # print(my_space,"-- dict")
                            print(my_cosmetic, att, my_obj_type, " Class - dict in class")
                            # print(new_obj.keys())
                            my_cosmetic += "['" + att + "']" # Dictionary in class att
                            for k in new_obj.keys():
                                val_obj = new_obj[k]
                                my_val_type = type(val_obj).__name__
                                # print(my_space, k, val_obj, my_val_type)
                                if my_val_type == 'dict':
                                    # print(my_space, "-- dict in dict")
                                    # print(my_space, k, val_obj, my_val_type)
                                    if len(val_obj) > 0:
                                        print(my_cosmetic, k, my_val_type, "sending to print_structure, Class, ", my_obj_type, " in key value of att")
                                        my_cosmetic += "['"+ k + "']"  # Dictionary in k value of att
                                        print_structure_det(val_obj, True, my_cosmetic, k)
                                elif my_val_type == 'list':
                                    # print(my_space, "-- list in dict")
                                    # print(my_space, k, val_obj, my_val_type)
                                    if len(val_obj) > 0:
                                        print(my_cosmetic, " sending ", k, my_val_type,
                                              " to print_structure, Class ", my_obj_type, "L in key value of att")
                                        my_cosmetic += "L->"  # List in k value of att
                                        print_structure_det(val_obj, True, my_cosmetic)
                                elif my_val_type == 'str':
                                    print(my_cosmetic, k, val_obj, my_val_type)
                                elif my_val_type == 'int':
                                    print(my_cosmetic, k, val_obj, my_val_type)
                                elif my_val_type == 'float':
                                    print(my_cosmetic, k, val_obj, my_val_type)
                                elif my_val_type == 'bool':
                                    print(my_cosmetic, k, val_obj, my_val_type)
                                elif my_val_type == 'NoneType':
                                    print(my_cosmetic, k, val_obj, my_val_type)
                                elif my_val_type == 'method':
                                    print(my_cosmetic, k, my_val_type)
                                else:
                                    print(my_cosmetic, '=> ', k, val_obj, my_val_type)


                    elif my_obj_type == 'list':
                        print(my_cosmetic, att, "is List in Class att")
                        my_cosmetic += " "
                        for i in new_obj:
                            list_obj = i
                            list_obj_type = type(list_obj).__name__
                            # print(my_cosmetic, list_obj, list_obj_type, "Class, list in class att")
                            if list_obj_type == 'dict':
                                # print(my_space, "-- dict in list")
                                # print(my_space, att, i, list_obj_type)
                                # print(new_obj.keys())
                                print(my_cosmetic, att, "sending dict",
                                      " to print_structure, Class, dict in list att")
                                my_cosmetic += "D->"
                                print_structure_det(list_obj, True, my_cosmetic)
                            elif list_obj_type == 'list':
                                if len(list_obj) > 0:
                                    print(my_cosmetic, "-- list in list - sending list to print_structure, Class, list in list att")
                                    my_cosmetic += "L->"
                                    print_structure_det(list_obj, True, my_cosmetic)
                            elif list_obj_type == 'str':
                                #print(my_cosmetic, list_obj,  getattr(my_obj, list_obj), list_obj_type)
                                print(my_cosmetic, list_obj, list_obj_type)
                            elif list_obj_type == 'int':
                                print(my_cosmetic, list_obj, getattr(my_obj, list_obj),list_obj_type)
                            elif list_obj_type == 'float':
                                print(my_cosmetic, list_obj, list_obj_type)
                            elif list_obj_type == 'bool':
                                print(my_cosmetic, list_obj, list_obj_type)
                            elif list_obj_type == 'NoneType':
                                print(my_cosmetic, list_obj, list_obj_type)
                            else:
                                print(my_cosmetic, '=> ', k, val_obj, my_val_type, "Class list member")

                    elif my_obj_type == 'str':
                        print(my_cosmetic, att, new_obj, my_obj_type)
                    elif my_obj_type == 'NoneType':
                        print(my_cosmetic, att, new_obj, my_obj_type)
                    elif my_obj_type == 'int':
                        print(my_cosmetic, att, new_obj, my_obj_type)
                    elif my_obj_type == 'float':
                        print(my_cosmetic, att, new_obj, my_obj_type)
                    elif my_obj_type == 'bool':
                        print(my_cosmetic, att, new_obj, my_obj_type)
                    elif my_obj_type == 'method':
                        print(my_cosmetic, att, my_obj_type)
                    elif my_obj_type == 'builtin_function_or_method':
                        print(my_cosmetic,att, my_obj_type)
                        #continue  # ignore builtin
                    else:
                        print(my_cosmetic, ' -> ', att, new_obj, my_obj_type)

            else:
                print(att, type(getattr(my_obj, att)).__name__)
