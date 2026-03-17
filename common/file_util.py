# common/file_util.py
import yaml
import os


def read_yaml(file_path):
    """读取 YAML 文件，返回 Python 列表或字典"""
    # 动态获取当前项目的绝对根目录，防止相对路径报错
    root_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    full_path = os.path.join(root_path, file_path)

    with open(full_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)
        return data