NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

class AlwaysEqualProxy(str):
    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False

any_type = AlwaysEqualProxy("*")


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