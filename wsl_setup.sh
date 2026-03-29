#!/bin/bash
# WSL2 配置脚本 - 禁用代理并安装必要工具

# 禁用代理
export http_proxy=""
export https_proxy=""
unset http_proxy
unset https_proxy

# 更新 apt 源（使用阿里云镜像加速）
sudo sed -i 's/archive.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list
sudo sed -i 's/security.ubuntu.com/mirrors.aliyun.com/g' /etc/apt/sources.list

# 更新并安装必要工具
sudo apt update
sudo apt install -y tmux git python3 python3-pip curl

# 安装 ClawTeam（WSL 内）
pip3 install clawteam

# 验证安装
echo "=== 安装完成 ==="
tmux -V
git --version
python3 --version
clawteam --version
