# Authors: Sergio Valqui
# Created : 2016/09
# Modified : 2018/05
# Master REST api class to contain all common properties and functions for REST api


class RestApi(object):
    def __init__(self):
        self.header_json = {"content-type": "application/json"}
        self.header_xml = {"content-type": "text/xml"}
        self.header_html = {"content-type": "text/html"}

    def navigate_json(self, json_loads, indent=""):  # json_loads, file-like object
            if isinstance(json_loads, dict):
                print(indent, "D_ Dict Here")
                for index in json_loads.keys():
                    if isinstance(json_loads[index], dict):
                        print(indent, "D_Content: ", index, "- Dict found on Dict resending")
                        indent += "  "
                        self.navigate_json(json_loads[index], indent)
                    elif isinstance(json_loads[index], list):
                        print(indent, "D_Content: ", index, "- List found on Dict resending, len :",
                              len(json_loads[index]))
                        indent += "  "
                        self.navigate_json(json_loads[index], indent)
                    elif isinstance(json_loads[index], str):
                        print(indent, "D_Content- Idx: ", index, "- str Value :", json_loads[index])
                    elif isinstance(json_loads[index], int):
                        print(indent, "D_Content- Idx: ", index, "- int Value :", json_loads[index])
                    elif isinstance(json_loads[index], float):
                        print(indent, "D_Content- Idx: ", index, "- float Value :", json_loads[index])
                    elif isinstance(json_loads[index], bool):
                        print(indent, "D_Content- Idx: ", index, "- bool Value :", json_loads[index])
                    elif isinstance(json_loads[index], type(None)):
                        print(indent, "D_Content- Idx: ", index, "- None Value :", json_loads[index])
                    else:
                        print(indent, "D_Content- Idx: ", index, "- Obj not pre defined")

            elif isinstance(json_loads, list):
                print(indent, "- L- list here, len :", len(json_loads))
                for element in json_loads:
                    if isinstance(element, dict):
                        print(indent, "L-Content : Dict found on List resending")
                        self.navigate_json(element, indent)
                    elif isinstance(element, list):
                        print(indent, "L-Content : List found on List resending, len :", len(element))
                        self.navigate_json(element, indent)
                    elif isinstance(element, str):
                        print(indent, "L-Content : str Value :", element)
                    elif isinstance(element, int):
                        print(indent, "L-Content : int Value :", element)
                    elif isinstance(element, float):
                        print(indent, "L-Content : float Value :", element)
                    elif isinstance(element, bool):
                        print(indent, "L-Content : bool Value :", element)
                    elif isinstance(element, type(None)):
                        print(indent, "L-Content : None Value :", element)
                    else:
                        print(indent, "L-Content : Obj not pre defined")

            elif isinstance(json_loads, str):
                print(indent, "Content : str Value :", json_loads)
            elif isinstance(json_loads, int):
                print(indent, "Content : int Value :", json_loads)
            elif isinstance(json_loads, float):
                print(indent, "Content : float Value :", json_loads)
            elif isinstance(json_loads, bool):
                print(indent, "Content : bool Value :", json_loads)
            elif isinstance(json_loads, type(None)):
                print(indent, "Content : None Value :", json_loads)
            else:
                print(indent, "Obj not pre defined")

            return
