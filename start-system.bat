@echo off
echo ============================================================
echo Buddy Dashboard 系统启动
echo ============================================================
echo.
echo [1/3] 检查依赖...
if not exist "node_modules" (
    echo 安装前端依赖...
    cd frontend
    npm install
    cd ..
)
echo.
echo [2/3] 启动后端 API...
start "Buddy API" cmd /k "python buddy/scripts/start_api.py"
timeout /t 3 >nul
echo.
echo [3/3] 启动前端界面...
start "Buddy Frontend" cmd /k "cd frontend && npm run dev"
echo.
echo ============================================================
echo 启动完成！
echo ============================================================
echo.
echo 访问地址:
echo   - 前端界面: http://localhost:3000
echo   - API 文档: http://localhost:8000/docs
echo   - API ReDoc: http://localhost:8000/redoc
echo.
echo 按任意键打开浏览器访问前端界面...
pause >nul
start http://localhost:3000
