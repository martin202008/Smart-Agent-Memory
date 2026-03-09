@echo off
REM Smart-Agent-Memory 发布脚本
REM 使用前请确保已安装 GitHub CLI: https://cli.github.com/

echo ========================================
echo Smart-Agent-Memory GitHub 发布
echo ========================================

REM 检查 gh 是否安装
where gh >nul 2>&1
if %errorlevel% neq 0 (
    echo [错误] 未找到 GitHub CLI (gh)
    echo 请先安装: https://cli.github.com/
    echo 安装后运行: gh auth login
    pause
    exit /b 1
)

REM 检查登录状态
gh auth status >nul 2>&1
if %errorlevel% neq 0 (
    echo 请先登录 GitHub:
    gh auth login
)

echo.
echo [1/3] 创建远程仓库...
gh repo create Smart-Agent-Memory --public --source=. --description "让AI Agent拥有类似人类的记忆系统——5层记忆架构+自我进化+情感感知" --confirm

echo.
echo [2/3] 添加文件并提交...
git add .
git commit -m "feat: Smart-Agent-Memory 智能记忆系统 - 5层记忆+自我进化+情感感知"

echo.
echo [3/3] 推送到 GitHub...
git push -u origin main

echo.
echo ========================================
echo 发布完成！
echo 仓库地址: https://github.com/martin202008/Smart-Agent-Memory
echo ========================================
pause
