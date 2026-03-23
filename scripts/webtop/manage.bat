@echo off
chcp 65001 >nul
echo ========================================
echo   WebTop Local - 持久化浏览器管理
echo ========================================
echo.

:menu
echo 请选择操作:
echo   1. 启动浏览器
echo   2. 停止浏览器
echo   3. 查看状态
echo   4. 启动 Watchdog 监控
echo   5. 输出连接配置
echo   0. 退出
echo.
set /p choice="请输入选项 (0-5): "

if "%choice%"=="1" goto start
if "%choice%"=="2" goto stop
if "%choice%"=="3" goto status
if "%choice%"=="4" goto watchdog
if "%choice%"=="5" goto config
if "%choice%"=="0" goto end

echo 无效选项，请重试
echo.
goto menu

:start
echo.
echo [启动] 正在启动持久化浏览器...
python "%~dp0webtop_local.py" --start
pause
goto menu

:stop
echo.
echo [停止] 正在停止浏览器...
python "%~dp0webtop_local.py" --stop
pause
goto menu

:status
echo.
echo [状态] 当前浏览器状态:
python "%~dp0webtop_local.py" --status
pause
goto menu

:watchdog
echo.
echo [Watchdog] 启动监控（按 Ctrl+C 停止）
python "%~dp0webtop_local.py" --watchdog
goto menu

:config
echo.
echo [配置] 浏览器连接配置:
python "%~dp0webtop_local.py" --config
pause
goto menu

:end
echo.
echo 再见！
pause
