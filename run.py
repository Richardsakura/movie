#!/usr/bin/env python
"""
启动脚本 - 一键启动电影推荐系统
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """检查依赖包是否已安装"""
    print("检查依赖包...")
    required_packages = ['Django', 'mysqlclient', 'numpy', 'scikit-learn', 'jieba', 'Pillow']
    
    for package in required_packages:
        try:
            __import__(package.lower() if package == 'Django' else package)
            print(f"✓ {package}")
        except ImportError:
            print(f"✗ {package} 未安装")
            return False
    
    return True

def install_dependencies():
    """安装依赖包"""
    print("安装依赖包...")
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", str(requirements_file)])
        print("✓ 依赖包安装成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ 依赖包安装失败: {e}")
        return False

def check_database():
    """检查数据库配置"""
    print("检查数据库配置...")
    
    # 添加项目路径
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    sys.path.insert(0, str(project_root / "movie_recommendation"))
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommendation.settings')
        import django
        django.setup()
        
        from django.db import connection
        from django.core.management import execute_from_command_line
        
        # 测试数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        if result and result[0] == 1:
            print("✓ 数据库连接正常")
            return True
        else:
            print("✗ 数据库连接异常")
            return False
            
    except Exception as e:
        print(f"✗ 数据库连接失败: {e}")
        return False

def migrate_database():
    """执行数据库迁移"""
    print("执行数据库迁移...")
    
    try:
        manage_py = Path(__file__).parent / "movie_recommendation" / "manage.py"
        
        # 生成迁移文件
        subprocess.check_call([sys.executable, str(manage_py), "makemigrations"], 
                              cwd=manage_py.parent)
        
        # 执行迁移
        subprocess.check_call([sys.executable, str(manage_py), "migrate"], 
                              cwd=manage_py.parent)
        
        print("✓ 数据库迁移完成")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"✗ 数据库迁移失败: {e}")
        return False
    except Exception as e:
        print(f"✗ 数据库迁移错误: {e}")
        return False

def create_superuser():
    """创建超级用户"""
    print("\n是否创建超级用户？(y/n): ")
    choice = input().lower().strip()
    
    if choice == 'y':
        try:
            manage_py = Path(__file__).parent / "movie_recommendation" / "manage.py"
            subprocess.check_call([sys.executable, str(manage_py), "createsuperuser"], 
                                  cwd=manage_py.parent)
            print("✓ 超级用户创建完成")
        except subprocess.CalledProcessError as e:
            print(f"✗ 超级用户创建失败: {e}")
    else:
        print("跳过超级用户创建")

def import_sample_data():
    """导入示例数据"""
    print("\n是否导入示例数据？(y/n): ")
    choice = input().lower().strip()
    
    if choice == 'y':
        try:
            sample_data_script = Path(__file__).parent / "import_sample_data.py"
            if sample_data_script.exists():
                subprocess.check_call([sys.executable, str(sample_data_script)])
                print("✓ 示例数据导入完成")
            else:
                print("✗ 示例数据脚本不存在")
        except subprocess.CalledProcessError as e:
            print(f"✗ 示例数据导入失败: {e}")
    else:
        print("跳过示例数据导入")

def start_server():
    """启动开发服务器"""
    print("\n启动开发服务器...")
    print("服务器将在 http://127.0.0.1:8000 运行")
    print("按 Ctrl+C 停止服务器")
    print("=" * 50)
    
    try:
        manage_py = Path(__file__).parent / "movie_recommendation" / "manage.py"
        subprocess.check_call([sys.executable, str(manage_py), "runserver"], 
                              cwd=manage_py.parent)
    except KeyboardInterrupt:
        print("\n服务器已停止")
    except subprocess.CalledProcessError as e:
        print(f"✗ 服务器启动失败: {e}")

def main():
    """主函数"""
    print("=" * 50)
    print("电影推荐系统 - 启动向导")
    print("=" * 50)
    
    # 检查依赖
    if not check_dependencies():
        print("\n依赖包不完整，正在安装...")
        if not install_dependencies():
            print("请手动安装依赖包: pip install -r requirements.txt")
            return
    
    # 检查数据库
    if not check_database():
        print("请检查数据库配置和连接")
        print("1. 确保MySQL服务已启动")
        print("2. 检查 movie_recommendation/settings.py 中的数据库配置")
        return
    
    # 迁移数据库
    if not migrate_database():
        print("数据库迁移失败，请检查错误信息")
        return
    
    # 可选：创建超级用户
    create_superuser()
    
    # 可选：导入示例数据
    import_sample_data()
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()