import os
from PIL import Image
from PIL.PngImagePlugin import PngInfo
import numpy as np
import folder_paths

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}

def register_node(identifier: str, display_name: str):
    def decorator(cls):
        NODE_CLASS_MAPPINGS[identifier] = cls
        NODE_DISPLAY_NAME_MAPPINGS[identifier] = display_name

        return cls

    return decorator

@register_node("GagaSaveImageWithInfo", "saveImageWithInfo")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda: {
        "required": {
            "images": ("IMAGE",),
            "filename_prefix": ("STRING", {"default": "ComfyUI"}),
            "prompt": ("STRING", {"default": "", "multiline": True}),
            "template": ("STRING", {"default": "", "multiline": True, "label": "输入{prompt}xxx 会最终写入保存的图片中"})
        }
    }
    RETURN_TYPES = ("STRING", "STRING")
    RETURN_NAMES = ("info", "filepath")
    OUTPUT_NODE = True
    FUNCTION = "execute"

    def execute(self, images, filename_prefix, prompt, template):
        print("-------")
        if template == "":
            template = "{prompt}\nNegative prompt: ng_deepnegative_v1_75t,(badhandv4:1.2),EasyNegative,(worst quality:2),\nSteps: 25,Size: 720x1024,Seed: -1,Model: F.1 模型下载版-黑暗森林工作室,Sampler: Euler,useLcm: false,CFG scale: 3.5,Clip skip: undefined,  "



        info = template.replace("{prompt}", prompt)

        print("--------:", info)

        metadata = PngInfo()
        metadata.add_text("parameters", info)

        output_dir = folder_paths.get_output_directory()
        output_path = os.path.join(output_dir, filename_prefix)

        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        file_path=""

        for index, image in enumerate(images):
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            (
                full_output_folder,
                filename,
                counter,
                subfolder,
                filename_prefix,
            ) = folder_paths.get_save_image_path(
                filename_prefix, output_dir, images[0].shape[1], images[0].shape[0]
            )
            base_filename = filename
            base_filename += f"_{counter:05}_"
            file = base_filename + ".png"
            file_path = os.path.join(full_output_folder, file)

            img.save(
                file_path,
                pnginfo=metadata,
                compress_level=4,
            )
        return (info, file_path, )


