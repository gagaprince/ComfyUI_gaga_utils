import subprocess
from PIL import Image, ImageOps
from PIL.PngImagePlugin import PngInfo
import numpy as np
import folder_paths
import torch
import hashlib
import os
import urllib.request
import urllib.error
from .utils import get_save_image_path

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


@register_node("GagaGetImageInfoByUpload", "getImageInfoByUpload")
class _:
    CATEGORY = "gaga"
    @classmethod
    def INPUT_TYPES(s):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        return {"required":
                    {"image": (sorted(files), {"image_upload": True})},
                }
    RETURN_TYPES = ("STRING","STRING","IMAGE", "MASK",)
    RETURN_NAMES = ("info","prompt","image","mask",)
    OUTPUT_NODE = True
    FUNCTION = "execute"

    def execute(self, image):
        image_path = folder_paths.get_annotated_filepath(image)
        imgF = Image.open(image_path)
        metaData = imgF.info
        prompt = self.parsePrompt(metaData)

        img = ImageOps.exif_transpose(imgF)
        image = img.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        if 'A' in img.getbands():
            mask = np.array(img.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

        return (metaData,prompt,image, mask.unsqueeze(0),)

    def parsePrompt(self, meta):
        try:
            info = meta["parameters"]
            prompt = info.split("\nNegative")[0]
            return prompt
        except Exception as e:
            print(f"发生错误：{str(e)}")
            return ""


@register_node("GagaGetImageInfoWithUrl", "getImageInfoWithUrl")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda: {
        "required": {
            "url": ("STRING", {"default": "", "multiline": True}),
            "save_path":("STRING", {"default": ""}),
        }
    }
    RETURN_TYPES = ("STRING","STRING","IMAGE", "MASK","STRING",)
    RETURN_NAMES = ("info","prompt","image","mask","savepath")
    OUTPUT_NODE = True
    FUNCTION = "execute"

    def execute(self, url, save_path):
        # 先下载图片到 目标位置
        tmp_path = folder_paths.get_temp_directory()
        if save_path is not None and save_path != "":
            tmp_path = save_path

        image_path = self.download_img(url, tmp_path)
        # image_path = folder_paths.get_annotated_filepath(image)
        imgF = Image.open(image_path)
        metaData = imgF.info
        prompt = self.parsePrompt(metaData)

        img = ImageOps.exif_transpose(imgF)
        image = img.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        if 'A' in img.getbands():
            mask = np.array(img.getchannel('A')).astype(np.float32) / 255.0
            mask = 1. - torch.from_numpy(mask)
        else:
            mask = torch.zeros((64, 64), dtype=torch.float32, device="cpu")

        return (metaData,prompt,image, mask.unsqueeze(0),image_path,)

    def download_img(self, url, tmp_path):
        """
        使用纯标准库实现的下载器
        功能：下载文件并以URL哈希值命名

        参数:
            url (str): 要下载的文件URL
            save_dir (str): 文件保存目录
            hash_algorithm (str): 哈希算法，默认md5，可选 sha1/sha256等
        """
        try:
            # 生成文件名哈希值
            hash_obj = hashlib.new("md5")
            hash_obj.update(url.encode('utf-8'))
            filename = hash_obj.hexdigest()

            # 发起请求
            with urllib.request.urlopen(url) as resp:
                extension = '.png'

                # 创建保存目录
                os.makedirs(tmp_path, exist_ok=True)

                # 构建保存路径
                save_path = os.path.join(tmp_path, f"{filename}{extension}")

                # 写入文件
                with open(save_path, 'wb') as f:
                    f.write(resp.read())

                print(f"文件下载成功: {save_path}")
                return save_path

        except urllib.error.URLError as e:
            print(f"网络错误: {e.reason}")
        except ValueError as e:
            print(f"URL格式错误: {str(e)}")
        except IOError as e:
            print(f"文件操作失败: {str(e)}")
        except Exception as e:
            print(f"未知错误: {str(e)}")

    def parsePrompt(self, meta):
        try:
            info = meta["parameters"]
            prompt = info.split("\nNegative")[0]
            return prompt
        except Exception as e:
            print(f"发生错误：{str(e)}")
            return ""


@register_node("GagaSaveImageToPath", "saveImageToPath")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda: {
        "required": {
            "images": ("IMAGE",),
            "filename_prefix": ("STRING", {"default": "ComfyUI"}),
            "save_path": ("STRING", {"default": "", "multiline": True}),
        }
    }
    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("filepath",)
    OUTPUT_NODE = True
    FUNCTION = "execute"

    def execute(self, images, filename_prefix, save_path):

        output_dir = folder_paths.get_output_directory()
        if save_path is not None and save_path != "":
            output_dir = save_path
        output_path = os.path.join(output_dir, filename_prefix)

        if not os.path.exists(os.path.dirname(output_path)):
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

        file_path = ""

        (
            full_output_folder,
            filename,
            counter,
            subfolder,
            filename_prefix,
        ) = get_save_image_path(
            filename_prefix, output_dir, images[0].shape[1], images[0].shape[0]
        )

        for index, image in enumerate(images):
            i = 255.0 * image.cpu().numpy()
            img = Image.fromarray(np.clip(i, 0, 255).astype(np.uint8))

            base_filename = filename
            base_filename += f"_{counter:05}_"
            file = base_filename + ".png"
            file_path = os.path.join(full_output_folder, file)
            print("file_path:", file_path)

            img.save(
                file_path,
                compress_level=4,
            )
            counter += 1
        return (file_path,)


@register_node("GagaGetImageWithPath", "getImageWithPath")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda: {
        "required": {
            "file_path": ("STRING",),
        }
    }
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("image",)
    FUNCTION = "execute"

    def execute(self, file_path):
        imgF = Image.open(file_path)
        img = ImageOps.exif_transpose(imgF)
        image = img.convert("RGB")
        image = np.array(image).astype(np.float32) / 255.0
        image = torch.from_numpy(image)[None,]
        return (image,)

