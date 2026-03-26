"""
项目初始化脚本
用于设置环境并启动项目
"""

import os
import sys
import subprocess
from pathlib import Path

def init_project():
    """初始化项目"""
    print("正在初始化电影推荐系统...")
    
    # 设置Python路径
    current_dir = Path(__file__).parent.absolute()
    sys.path.insert(0, str(current_dir))
    
    # 检查虚拟环境
    venv_path = current_dir / "venv"
    if not venv_path.exists():
        print("创建虚拟环境...")
        subprocess.run([sys.executable, "-m", "venv", "venv"], cwd=current_dir)
    
    # 激活虚拟环境并安装依赖
    print("安装依赖包...")
    requirements_path = current_dir / "requirements.txt"
    if requirements_path.exists():
        pip_path = venv_path / "Scripts" / "pip.exe"
        if pip_path.exists():
            subprocess.run([str(pip_path), "install", "-r", str(requirements_path)])
        else:
            print("警告：虚拟环境pip未找到，尝试使用系统pip")
            subprocess.run([sys.executable, "-m", "pip", "install", "-r", str(requirements_path)])
    
    # 检查数据库配置
    print("检查数据库配置...")
    try:
        from movie_recommendation import settings
        print("✓ 配置加载成功")
    except Exception as e:
        print(f"✗ 配置加载失败: {e}")
        return False
    
    # 初始化数据库
    print("初始化数据库...")
    manage_py = current_dir / "manage.py"
    if manage_py.exists():
        try:
            # 生成迁移文件
            subprocess.run([sys.executable, str(manage_py), "makemigrations"], cwd=current_dir)
            # 执行迁移
            subprocess.run([sys.executable, str(manage_py), "migrate"], cwd=current_dir)
            print("✓ 数据库初始化成功")
        except Exception as e:
            print(f"✗ 数据库初始化失败: {e}")
            return False
    
    print("项目初始化完成！")
    print("\n下一步操作：")
    print("1. 创建超级用户: python manage.py createsuperuser")
    print("2. 启动服务器: python manage.py runserver")
    print("3. 访问: http://127.0.0.1:8000/")
    
    return True

if __name__ == "__main__":
    init_project()
"""