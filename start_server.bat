@echo off

echo ==================================================
echo 电影推荐系统 - 启动服务器
echo ==================================================

rem 切换到项目目录
cd movie_recommendation

rem 检查是否安装了必要的包
python -c "import django"
if errorlevel 1 (
    echo 检测到缺少依赖包，正在安装...
    pip install -r ..\requirements.txt
)

echo.
echo 执行数据库迁移...
python manage.py makemigrations
python manage.py migrate

echo.
echo 创建超级用户（可选）
echo 如果不需要创建超级用户，请按Ctrl+C跳过
python manage.py createsuperuser

if errorlevel 1 (
    echo 跳过超级用户创建
)

echo.
echo 启动开发服务器...
echo 访问地址: http://127.0.0.1:8000/
echo 按 Ctrl+C 停止服务器
echo.
echo ==================================================

python manage.py runserver

pause