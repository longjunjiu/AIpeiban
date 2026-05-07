#!/bin/bash
# AIpeiban 项目推送脚本

echo "正在推送AI陪伴项目到GitHub..."
cd "$(dirname "$0")"

# 添加远程仓库（如果需要）
git remote set-url origin https://github.com/longjunjiu/AIpeiban.git

# 推送代码
# 如果你配置了GitHub Personal Access Token，可以使用以下格式：
# git remote set-url origin https://YOUR_TOKEN@github.com/longjunjiu/AIpeiban.git

git push origin main

echo "推送完成！"
echo ""
echo "如果推送失败，请确保已配置GitHub访问令牌："
echo "1. 前往 https://github.com/settings/tokens"
echo "2. 创建新的Personal Access Token"
echo "3. 运行: git remote set-url origin https://YOUR_TOKEN@github.com/longjunjiu/AIpeiban.git"
echo "4. 再次运行: git push origin main"
