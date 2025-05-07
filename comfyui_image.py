import subprocess
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

# """
# Invoke-WebRequest -Uri https://win.rustup.rs/x86_64 -OutFile rustup-init.exe

# $env:RUSTUP_DIST_SERVER = "https://mirrors.tuna.tsinghua.edu.cn/rustup"
# $env:RUSTUP_UPDATE_ROOT = "https://mirrors.tuna.tsinghua.edu.cn/rustup/rustup"

# rustc --version   # 输出类似 rustc 1.78.0 (abcabcabc 2025-XX-XX)
# cargo --version   # 输出类似 cargo 1.78.0 (defdefdef 2025-XX-XX)

# cargo install gifski
# """

@register_node("GagaSaveImagesToGif", "saveImagesToGif")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda: {
        "required": {
            "images": ("IMAGE",),
            "filename_prefix": ("STRING", {"default": "ComfyUI"}),
            "fps": ("INT", {"default": "1"}),
            "width": ("INT", {"default": "720"})
        }
    }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)
    OUTPUT_NODE = True
    FUNCTION = "execute"

    def execute(self, images, filename_prefix, fps, width):
        print("------saveImagesToGif--------")
        temp_dir = "tmp_frames"
        output_dir = folder_paths.get_output_directory()
        temp_path = os.path.join(output_dir, temp_dir)
        os.makedirs(temp_path, exist_ok=True)
        for i, img_tensor in enumerate(images):
            img = Image.fromarray((img_tensor.numpy().squeeze() * 255).astype("uint8"))
            img.save(os.path.join(temp_path, f"{filename_prefix}_{i:04d}.png"))
        
        output_path = os.path.join(output_dir, filename_prefix)
        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

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
        file = base_filename + ".gif"
        file_path = os.path.join(full_output_folder, file)

        cmd = [
            "gifski",
            "--fps", str(fps),
            "-W", str(width),
            "-o", file_path,
            os.path.join(temp_path, f"{filename_prefix}_*.png")
        ]
        subprocess.run(cmd, check=True)
        for file in os.listdir(temp_path):
            os.remove(os.path.join(temp_path, file))
        os.rmdir(temp_path)

        print("save gif:", file_path)

        return (file_path,)
        



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

        (
            full_output_folder,
            filename,
            counter,
            subfolder,
            filename_prefix,
        ) = folder_paths.get_save_image_path(
            filename_prefix, output_dir, images[0].shape[1], images[0].shape[0]
        )

        for index, image in enumerate(images):
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))
            
            base_filename = filename
            base_filename += f"_{counter:05}_"
            file = base_filename + ".png"
            file_path = os.path.join(full_output_folder, file)
            print("file_path:",file_path)            

            img.save(
                file_path,
                pnginfo=metadata,
                compress_level=4,
            )
            counter += 1
        return (info, file_path, )


