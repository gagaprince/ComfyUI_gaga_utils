import os
from typing import List, Union

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}


def register_node(identifier: str, display_name: str):
    def decorator(cls):
        NODE_CLASS_MAPPINGS[identifier] = cls
        NODE_DISPLAY_NAME_MAPPINGS[identifier] = display_name

        return cls

    return decorator


@register_node("GagaGetFileList", "getFileList")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda: {
        "required": {
            "dir_path": ("STRING", {"default": ""}),
            "is_recursion": ("BOOLEAN", {"default": False}),
            "ext": ("STRING", {"default": ""})
        }
    }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"

    def execute(self, dir_path, is_recursion, ext):
        if ext:
            ext = ext.split(",")
        file_list = self.get_files(dir_path, is_recursion, ext)
        return ("\n".join(file_list), )

    def get_files(self,
            directory: str,
            recursive: bool = False,
            extensions: Union[List[str], None] = None
    ) -> List[str]:
        """
        获取指定目录下的文件列表

        参数：
        directory  : 目标目录路径
        recursive  : 是否递归子目录 (默认False)
        extensions : 过滤的文件扩展名列表，如 ['.txt', '.jpg'] (默认不过滤)

        返回：
        匹配条件的文件绝对路径列表
        """

        # 检查目录有效性
        if not os.path.isdir(directory):
            return []

        # 处理扩展名参数
        ext_set = None
        if extensions:
            ext_set = {
                ext.lower().strip() if ext.startswith('.') else f'.{ext.lower().strip()}'
                for ext in extensions
            }

        file_list = []

        # 遍历目录结构
        for root, dirs, files in os.walk(directory):
            # 处理当前目录文件
            for filename in files:
                # 提取扩展名并校验
                file_ext = os.path.splitext(filename)[1].lower()
                if not ext_set or file_ext in ext_set:
                    full_path = os.path.abspath(os.path.join(root, filename))
                    file_list.append(full_path)

            # 控制递归深度
            if not recursive:
                dirs[:] = []  # 清空子目录列表以停止递归

        return file_list


@register_node("GagaGetDirList", "getDirList")
class _:
    CATEGORY = "gaga"
    INPUT_TYPES = lambda: {
        "required": {
            "dir_path": ("STRING", {"default": ""})
        }
    }
    RETURN_TYPES = ("STRING",)
    FUNCTION = "execute"

    def execute(self, dir_path):
        dir_list = self.get_dirs(dir_path)
        return ("\n".join(dir_list), )

    def get_dirs(self,
            directory: str,
    ) -> List[str]:
        # 检查目录有效性
        if not os.path.isdir(directory):
            return []
        with os.scandir(directory) as entries:
            return [entry.path for entry in entries if entry.is_dir()]
