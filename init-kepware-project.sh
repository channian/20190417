#!/bin/bash
# Kepware 專案快速初始化腳本
# 使用方式：在新專案目錄執行 bash /path/to/this/script.sh

set -e

echo "🚀 Kepware 專案初始化開始..."
echo ""

# 檢查是否在 Git repository 中
if [ ! -d .git ]; then
    echo "⚠️  目前目錄還沒有 Git repository"
    read -p "是否要執行 git init? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git init
        echo "✅ Git repository 已初始化"
    fi
fi

# 複製 .claude 設定目錄
SOURCE_CLAUDE="/home/user/20190417/.claude"
if [ -d "$SOURCE_CLAUDE" ]; then
    echo "📦 正在複製 Claude Code 設定和 Skills..."
    cp -r "$SOURCE_CLAUDE" .
    echo "✅ .claude 目錄已複製"
else
    echo "❌ 找不到來源專案：$SOURCE_CLAUDE"
    exit 1
fi

echo ""
echo "✅ 初始化完成！"
echo ""
echo "📋 已複製的內容："
echo "  - .claude/settings.json（權限與 hooks）"
echo "  - .claude/skills/add-personal-context/"
echo "  - .claude/skills/setup-project/"
echo ""
echo "🎯 下一步："
echo "  1. 在 Claude Code 中開啟這個專案"
echo "  2. 執行 /setup-project 完成完整設定"
echo "  3. 開始開發！"
echo ""
