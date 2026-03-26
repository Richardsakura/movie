#!/usr/bin/env python
"""
检查Python路径和模块导入
"""

import os
import sys
from pathlib import Path

print("当前工作目录:", os.getcwd())
print()
print("Python路径:")
for i, path in enumerate(sys.path):
    print(f"  {i:2d}. {path}")

print()
print("检查模块导入:")

# 尝试导入Django
print("1. 导入Django:", end=" ")
try:
    import django
    print("成功")
except ImportError as e:
    print(f"失败: {e}")

# 尝试导入项目设置
print("2. 导入项目设置:", end=" ")
try:
    # 添加项目根目录
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommendation.settings')
    import django
    django.setup()
    
    from django.conf import settings
    print(f"成功 - DEBUG={settings.DEBUG}, DATABASE={settings.DATABASES['default']['ENGINE']}")
except Exception as e:
    print(f"失败: {e}")