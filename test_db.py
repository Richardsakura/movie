#!/usr/bin/env python
"""
测试数据库连接脚本
"""

import os
import sys
from pathlib import Path

# 添加项目路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "movie_recommendation"))

def test_database_connection():
    """测试数据库连接"""
    print("测试数据库连接...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'movie_recommendation.settings')
        import django
        django.setup()
        
        from django.db import connection
        
        # 测试数据库连接
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            result = cursor.fetchone()
            
        if result and result[0] == 1:
            print("数据库连接成功!")
            return True
        else:
            print("数据库连接异常")
            return False
            
    except Exception as e:
        print(f"数据库连接失败: {e}")
        
        # 提供常见问题的解决方案
        print("")
        print("常见问题解决方案:")
        print("1. 确保MySQL服务已启动")
        print("2. 检查 movie_recommendation/settings.py 中的数据库配置")
        print("3. 确认数据库 'movie_recommendation' 已创建")
        print("4. 检查用户名和密码是否正确")
        
        return False

def main():
    """主函数"""
    print("=" * 50)
    print("电影推荐系统 - 数据库连接测试")
    print("=" * 50)
    
    success = test_database_connection()
    
    if success:
        print("")
        print("数据库配置正确，可以继续下一步")
    else:
        print("")
        print("数据库配置有问题，请先解决上述问题")
    
    return success

if __name__ == "__main__":
    main()