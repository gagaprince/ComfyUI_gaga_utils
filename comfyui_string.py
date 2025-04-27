NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}


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
            "value": ("STRING", {"default": "", "multiline": True}),
        }
    }
    RETURN_TYPES = ("INT",)
    FUNCTION = "execute"

    def execute(self, value: str):
        val = value.splitlines()
        return (val,)