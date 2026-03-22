@echo off
REM Buddy 看板系统快速启动脚本 (Windows)

echo ============================================================
echo Buddy 看板系统 - 快速启动
echo ============================================================
echo.

REM 检查 Python 版本
python --version
if %errorlevel% neq 0 (
    echo ✗ Python 未安装，请先安装 Python 3.8+
    pause
    exit /b 1
)

REM 安装依赖
echo.
echo 正在安装 Python 依赖...
pip install -q fastapi uvicorn sqlalchemy psycopg2-binary pydantic pydantic-settings python-dotenv

if %errorlevel% equ 0 (
    echo ✓ Python 依赖安装完成
) else (
    echo ✗ Python 依赖安装失败
    pause
    exit /b 1
)

REM 初始化数据库
echo.
echo 正在初始化数据库...
echo y | python -m buddy.scripts.init_mock_data

if %errorlevel% equ 0 (
    echo ✓ 数据库初始化完成
) else (
    echo ✗ 数据库初始化失败
    pause
    exit /b 1
)

REM 启动服务
echo.
echo ============================================================
echo 启动 API 服务...
echo ============================================================
echo.
echo 📍 API 文档: http://localhost:8000/docs
echo 📍 登录页面: 请在浏览器打开 frontend\index.html
echo.
echo 按 Ctrl+C 停止服务
echo.

python -m buddy.main

pause
