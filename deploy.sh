#!/bin/bash
#
# 📦 内存价格监控系统 - 一键部署到 GitHub
# 运行前请确保已安装 GitHub CLI (gh) 并登录
#

set -e

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║   📦 内存价格监控系统 - 一键部署脚本                    ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置信息
REPO_NAME="memory-price-monitor"
SMTP_EMAIL="289997689@qq.com"
SMTP_PASSWORD="ghwsjgueaqurbjgh"
RECIPIENT_EMAIL="289997689@qq.com"

# 检查 gh 是否安装
echo -e "${BLUE}[1/6]${NC} 检查 GitHub CLI..."
if ! command -v gh &> /dev/null; then
    echo -e "${YELLOW}⚠️  未安装 GitHub CLI，正在安装...${NC}"
    if command -v brew &> /dev/null; then
        brew install gh
    else
        echo -e "${RED}❌ 请先安装 Homebrew 或手动安装 GitHub CLI${NC}"
        echo "   安装命令: brew install gh"
        echo "   或访问: https://cli.github.com/"
        exit 1
    fi
fi
echo -e "${GREEN}✅ GitHub CLI 已安装${NC}"

# 检查 gh 登录状态
echo ""
echo -e "${BLUE}[2/6]${NC} 检查 GitHub 登录状态..."
if ! gh auth status &> /dev/null; then
    echo -e "${YELLOW}⚠️  未登录 GitHub，请先登录...${NC}"
    gh auth login
fi
echo -e "${GREEN}✅ 已登录 GitHub${NC}"

# 初始化 Git 仓库
echo ""
echo -e "${BLUE}[3/6]${NC} 初始化 Git 仓库..."
cd "$(dirname "$0")"

if [ -d ".git" ]; then
    echo -e "${YELLOW}   Git 仓库已存在，跳过初始化${NC}"
else
    git init
    echo -e "${GREEN}✅ Git 仓库已初始化${NC}"
fi

# 添加文件并提交
git add -A
git commit -m "🚀 Initial commit: 内存价格监控系统" 2>/dev/null || echo -e "${YELLOW}   没有新的更改需要提交${NC}"

# 创建 GitHub 仓库
echo ""
echo -e "${BLUE}[4/6]${NC} 创建 GitHub 仓库..."
if gh repo view "$REPO_NAME" &> /dev/null; then
    echo -e "${YELLOW}   仓库 $REPO_NAME 已存在${NC}"
else
    gh repo create "$REPO_NAME" --public --source=. --remote=origin --push \
        --description "📊 内存价格监控系统 - 每日自动发送价格报告到邮箱"
    echo -e "${GREEN}✅ GitHub 仓库已创建${NC}"
fi

# 推送代码
echo ""
echo -e "${BLUE}[5/6]${NC} 推送代码到 GitHub..."
git branch -M main 2>/dev/null || true
git remote add origin "https://github.com/$(gh api user -q .login)/$REPO_NAME.git" 2>/dev/null || true
git push -u origin main --force
echo -e "${GREEN}✅ 代码已推送${NC}"

# 配置 Secrets
echo ""
echo -e "${BLUE}[6/6]${NC} 配置 GitHub Secrets..."
gh secret set SMTP_EMAIL --body "$SMTP_EMAIL"
gh secret set SMTP_PASSWORD --body "$SMTP_PASSWORD"
gh secret set RECIPIENT_EMAIL --body "$RECIPIENT_EMAIL"
echo -e "${GREEN}✅ Secrets 已配置${NC}"

# 启用 Actions
echo ""
echo -e "${BLUE}[额外]${NC} 启用 GitHub Actions..."
gh workflow enable monitor.yml 2>/dev/null || echo -e "${YELLOW}   Actions 将在首次推送后自动启用${NC}"

# 获取仓库 URL
REPO_URL="https://github.com/$(gh api user -q .login)/$REPO_NAME"

echo ""
echo "╔════════════════════════════════════════════════════════╗"
echo "║                    🎉 部署完成！                        ║"
echo "╚════════════════════════════════════════════════════════╝"
echo ""
echo -e "${GREEN}✅ 仓库地址: ${BLUE}$REPO_URL${NC}"
echo -e "${GREEN}✅ Actions:  ${BLUE}$REPO_URL/actions${NC}"
echo ""
echo "📅 定时任务: 每天早上 8:00 (北京时间) 自动运行"
echo "📧 收件邮箱: $RECIPIENT_EMAIL"
echo ""
echo "💡 提示:"
echo "   - 查看运行状态: $REPO_URL/actions"
echo "   - 手动触发运行: 在 Actions 页面点击 'Run workflow'"
echo "   - 修改监控产品: 编辑 data/products.json"
echo ""
