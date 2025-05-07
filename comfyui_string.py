from .utils import StringArrayProxy, AlwaysEqualProxy
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

any_type = AlwaysEqualProxy("*")
string_arr = StringArrayProxy("*")


def register_node(identifier: str, display_name: str):
    def decorator(cls):
        NODE_CLASS_MAPPINGS[identifier] = cls
        NODE_DISPLAY_NAME_MAPPINGS[identifier] = display_name

        return cls

    return decorator

@register_node("GagaGetStringListSize", "Get String List Size")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda: {
        "required": {
            "string": ("STRING", {"default": "", "multiline": True}),
        }
    }
    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"

    def execute(self, string: str):
        val = len(string.splitlines())
        return (val,)

@register_node("GagaSplitStringToList", "split string to list")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda: {
        "required": {
            "string": ("STRING", {"default": "", "multiline": True}),
            "split_by": ("STRING", {"default": ",", "multiline": False})
        }
    }
    RETURN_TYPES = ("STRING_LIST",)
    FUNCTION = "execute"

    def execute(self, string: str, split_by: str):
        print(string)
        print(split_by)
        if split_by is None or split_by == "":
            val = string.splitlines()
        else:
            val = string.split(split_by)
        return (val,)

@register_node("GagaTest", "gaga test")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda: {
        "required": {
            "string_list": ("STRING_LIST", {"default": ""}),
            "index": ("INT", {"default": "0"})
        }
    }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"

    def execute(self, string_list, index):
        return (string_list[index],)

@register_node("GagaBatchStringReplace", "batchStringReplace")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda: {
        "required": {
            "string": ("STRING", {"default": ""}),
            "replace": ("STRING", {"default": ""}),
            "target": ("STRING", {"default": ""})
        }
    }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"

    def execute(self, string: str, replace, target):
        str_list = string.splitlines()
        ret = list(map(lambda line: line.replace(replace, target), str_list))
        return ("\n".join(ret),)

@register_node("GagaStringListToArray", "stringListToArray")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda : {
        "required": {
        },
        "optional": {
            "string_1": ("STRING", {"default": ""}),
            "string_2": ("STRING", {"default": ""}),
            "string_3": ("STRING", {"default": ""}),
            "string_4": ("STRING", {"default": ""}),
        }
    }
    RETURN_TYPES = (string_arr,)
    RETURN_NAMES = ("string_arr",)
    FUNCTION = "execute"

    def execute(self,
                string_1=None,
                string_2=None,
                string_3=None,
                string_4=None):
        list_str = []

        if string_1 is not None and string_1 != "":
            list_str.append(string_1)
        if string_2 is not None and string_2 != "":
            list_str.append(string_2)
        if string_3 is not None and string_3 != "":
            list_str.append(string_3)
        if string_4 is not None and string_4 != "":
            list_str.append(string_4)
        return (list_str, )

@register_node("GagaAddStringArray", "addStringArray")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda : {
        "required": {
        },
        "optional": {
            "string_arr1": (string_arr),
            "string_arr2": (string_arr),
        }
    }
    RETURN_TYPES = (string_arr,)
    RETURN_NAMES = ("string_arr",)
    FUNCTION = "execute"

    def execute(self,
                string_arr1=None,
                string_arr2=None,):
        str_arr = string_arr1 + string_arr2


        return (str_arr, )


@register_node("GagaGetStringArrayByIndex", "getStringArrayByIndex")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda : {
        "required": {
            "string_arr": (string_arr),
            "index": ("INT", {"default": "0"})
        },
    }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"

    def execute(self, string_arr, index):
        return (string_arr[index],)


@register_node("GagaGetStringArraySize", "Get String Array Size")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda: {
        "required": {
            "string_arr": (string_arr),
        }
    }
    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"

    def execute(self, string_arr):
        val = len(string_arr)
        return (val,)