# Authors: Sergio Valqui
# Created : 2016/09
# Modified : 2016/11
# Master REST api class to contain all common properties and functions for REST api


class RestApi(object):
    def __init__(self):
        self.header_json = {"content-type": "application/json"}
        self.header_xml = {"content-type": "text/xml"}
        self.header_html = {"content-type": "text/html"}

    def navigate_json(self, json_loads, indent=""):
            if isinstance(json_loads, dict):
                print(indent, "- D_Content : dict here")
                for index in json_loads.keys():
                    if isinstance(json_loads[index], dict):
                        print(indent, "D_Content- Index: ", index, "- dict found on dict resending")
                        indent += "  "
                        self.navigate_json(json_loads[index], indent)
                    elif isinstance(json_loads[index], list):
                        print(indent, "D_Content- Index: ", index, "- list found on dict resending, len :",
                              len(json_loads[index]))
                        indent += "  "
                        self.navigate_json(json_loads[index], indent)
                    elif isinstance(json_loads[index], str):
                        print(indent, "D_Content- Index: ", index, "- str Value :", json_loads[index])
                    elif isinstance(json_loads[index], int):
                        print(indent, "D_Content- Index: ", index, "- int Value :", json_loads[index])
                    elif isinstance(json_loads[index], float):
                        print(indent, "D_Content- Index: ", index, "- float Value :", json_loads[index])
                    elif isinstance(json_loads[index], True):
                        print(indent, "D_Content- Index: ", index, "- True Value :", json_loads[index])
                    elif isinstance(json_loads[index], False):
                        print(indent, "D_Content- Index: ", index, "- False Value :", json_loads[index])
                    elif isinstance(json_loads[index], None):
                        print(indent, "D_Content- Index: ", index, "- None Value :", json_loads[index])
                    else:
                        print(indent, "D_Content- Index: ", index, "- Obj not pre defined")

            elif isinstance(json_loads, list):
                print(indent, "- L-Content : list here")
                for element in json_loads:
                    if isinstance(element, dict):
                        print(indent, "L-Content : dict found on list resending")
                        self.navigate_json(element, indent)
                    elif isinstance(element, list):
                        print(indent, "L-Content : list found on list resending, len :", len(element))
                        self.navigate_json(element, indent)
                    elif isinstance(element, str):
                        print(indent, "L-Content : str Value :", element)
                    elif isinstance(element, int):
                        print(indent, "L-Content : int Value :", element)
                    elif isinstance(element, float):
                        print(indent, "L-Content : float Value :", element)
                    elif isinstance(element, True):
                        print(indent, "L-Content : True Value :", element)
                    elif isinstance(element, False):
                        print(indent, "L-Content : False Value :", element)
                    elif isinstance(element, None):
                        print(indent, "L-Content : None Value :", element)
                    else:
                        print(indent, "- L-Content : Obj not pre defined")

            elif isinstance(json_loads, str):
                print(indent, "Content : str Value :", json_loads)
            elif isinstance(json_loads, int):
                print(indent, "Content : int Value :", json_loads)
            elif isinstance(json_loads, float):
                print(indent, "Content : float Value :", json_loads)
            elif isinstance(json_loads, True):
                print(indent, "Content : True Value :", json_loads)
            elif isinstance(json_loads, False):
                print(indent, "Content : False Value :", json_loads)
            elif isinstance(json_loads, None):
                print(indent, "Content : None Value :", json_loads)
            else:
                print(indent, "Obj not pre defined")

            return
