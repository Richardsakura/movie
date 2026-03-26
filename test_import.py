#!/usr/bin/env python
"""
测试模块导入
"""

import os
import sys

# 添加当前目录到Python路径
current_dir = os.path.dirname(os.path.abspath(__file__))
movie_dir = os.path.join(current_dir, "movie_recommendation")

print("当前目录:", current_dir)
print("movie_recommendation目录:", movie_dir)

# 检查目录是否存在
if os.path.exists(movie_dir):
    print(" movie_recommendation目录存在")
    
    # 检查__init__.py文件
    init_file = os.path.join(movie_dir, "__init__.py")
    if os.path.exists(init_file):
        print(" __init__.py文件存在")
        print("文件内容:")
        with open(init_file, 'r') as f:
            content = f.read()
            print(repr(content))
    else:
        print(" __init__.py文件不存在")
        
    # 检查settings.py文件
    settings_file = os.path.join(movie_dir, "settings.py")
    if os.path.exists(settings_file):
        print(" settings.py文件存在")
    else:
        print(" settings.py文件不存在")
        
else:
    print(" movie_recommendation目录不存在")
    sys.exit(1)

print()
print("尝试导入...")

# 添加movie_recommendation目录到Python路径
sys.path.insert(0, movie_dir)

# 尝试导入
print("1. 导入settings模块:", end=" ")
try:
    from movie_recommendation import settings
    print("成功")
    print("   DEBUG =", getattr(settings, 'DEBUG', '未找到'))
except Exception as e:
    print(f"失败: {e}")

print("2. 直接导入settings:", end=" ")
try:
    import movie_recommendation.settings as s
    print("成功")
    print("   DEBUG =", getattr(s, 'DEBUG', '未找到'))
except Exception as e:
    print(f"失败: {e}")

print("3. 使用importlib:", end=" ")
try:
    import importlib
    module = importlib.import_module('movie_recommendation.settings')
    print("成功")
    print("   DEBUG =", getattr(module, 'DEBUG', '未找到'))
except Exception as e:
    print(f"失败: {e}")