import io
import sys

from .utils import AlwaysEqualProxy
NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

any_type = AlwaysEqualProxy("*")


def register_node(identifier: str, display_name: str):
    def decorator(cls):
        NODE_CLASS_MAPPINGS[identifier] = cls
        NODE_DISPLAY_NAME_MAPPINGS[identifier] = display_name

        return cls

    return decorator

@register_node("GagaPythonScript", "python script")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda: {
        "required": {
            "value": (any_type,),
            "code": ("STRING", {
                "multiline": True,
                "default": "# Write Python code here\n# 'value' is ANY_TYPE, assign 'result' (must match upstream/downstream type)\nprint(\"value=\", value)\nresult = value"
            })
        }
    }
    RETURN_TYPES = (any_type,any_type,any_type,any_type,any_type, "STRING",)  # Outputs: result and debug_output
    RETURN_NAMES = ("result","ret1","ret2","ret3","ret4", "debug_output",)  # Renamed to debug_output
    FUNCTION = "execute"

    def execute(self, value, code):

        local_vars = {"value": value}
        # Redirect stdout to capture print() output
        output_capture = io.StringIO()
        sys.stdout = output_capture

        try:
            # Execute the code
            exec(code, {}, local_vars)
            # Restore stdout
            sys.stdout = sys.__stdout__
            # Get result, raise error if not assigned
            if "result" not in local_vars:
                raise ValueError("Result must be assigned in the code")
            result = local_vars["result"]

            captured_output = output_capture.getvalue()

            # Return result and captured output (or "No output" if empty)
            ret1 = ret2 = ret3 = ret4 = ""
            if isinstance(result, dict) and result:
                if "ret1" in result:
                    ret1 = result["ret1"]
                if "ret2" in result:
                    ret2 = result["ret2"]
                if "ret3" in result:
                    ret3 = result["ret3"]
                if "ret4" in result:
                    ret4 = result["ret4"]
            return (result, ret1, ret2, ret3, ret4, captured_output if captured_output else "No output")
        except Exception as e:
            # Restore stdout on error
            print(e)
            sys.stdout = sys.__stdout__
            error_msg = f"Error: {str(e)}"
            # Return None and error message on exception
            return (None, error_msg)
