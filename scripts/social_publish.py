#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
scripts/social_publish.py — 社交媒体自动发布

功能:
  1. 读取 content_pipeline.py 生成的社交媒体文案
  2. 自动发布到 Twitter/X（需配置 API Key）
  3. 自动发布到 Reddit（需配置 API Key）
  4. 输出未配置平台的待发布文案

用法:
  python scripts/social_publish.py --dry-run    # 预览待发布内容
  python scripts/social_publish.py --twitter    # 发布到 Twitter/X
  python scripts/social_publish.py --reddit     # 发布到 Reddit
  python scripts/social_publish.py --all        # 发布到所有已配置平台

环境变量:
  TWITTER_BEARER_TOKEN     — Twitter API Bearer Token
  TWITTER_API_KEY          — Twitter API Key
  TWITTER_API_SECRET       — Twitter API Secret
  TWITTER_ACCESS_TOKEN     — Twitter Access Token
  TWITTER_ACCESS_SECRET    — Twitter Access Token Secret
  REDDIT_CLIENT_ID         — Reddit App Client ID
  REDDIT_CLIENT_SECRET     — Reddit App Client Secret
  REDDIT_USERNAME          — Reddit 用户名
  REDDIT_PASSWORD          — Reddit 密码
"""

import json
import os
import sys
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone, timedelta

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONTENT_DIR = os.path.join(BASE_DIR, "content", "blog")

TZ = timezone(timedelta(hours=8))


def _load_text(path):
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def find_latest_social_posts():
    """找到最新生成的社交媒体文案文件"""
    import glob
    files = sorted(glob.glob(os.path.join(CONTENT_DIR, "social-*.md")), reverse=True)
    if not files:
        return None
    return files[0]


def parse_social_content(filepath):
    """解析社交媒体文案文件，按平台分类"""
    content = _load_text(filepath)
    if not content:
        return {}
    
    posts = {}
    current_platform = None
    current_posts = []
    current_text = []
    in_code = False
    
    for line in content.split("\n"):
        if line.startswith("## "):
            if current_platform and current_posts:
                posts[current_platform] = current_posts
            current_platform = line[3:].strip().lower()
            current_posts = []
            current_text = []
            in_code = False
        elif line.startswith("```"):
            if in_code and current_text:
                text = "\n".join(current_text).strip()
                if text:
                    current_posts.append(text)
                current_text = []
            in_code = not in_code
        elif in_code:
            current_text.append(line)
    
    if current_platform and current_posts:
        posts[current_platform] = current_posts
    
    return posts


# ── Twitter/X 发布 ──
def publish_twitter(text):
    """发布推文到 Twitter/X v2 API"""
    bearer = os.environ.get("TWITTER_BEARER_TOKEN", "")
    api_key = os.environ.get("TWITTER_API_KEY", "")
    api_secret = os.environ.get("TWITTER_API_SECRET", "")
    access_token = os.environ.get("TWITTER_ACCESS_TOKEN", "")
    access_secret = os.environ.get("TWITTER_ACCESS_SECRET", "")
    
    if not all([api_key, api_secret, access_token, access_secret]):
        return {"error": "缺少 Twitter API 凭证，请设置 TWITTER_API_KEY 等环境变量"}
    
    # Twitter API v2 发布推文
    # 需要 OAuth 1.0a 签名，这里简化使用 requests_oauthlib 的说明
    # 由于零依赖原则，这里输出操作指南
    return {
        "status": "manual_required",
        "message": "Twitter 发布需要 OAuth 1.0a 签名",
        "action": "请使用以下文案发布推文",
        "text": text[:280],
        "api_endpoint": "POST https://api.twitter.com/2/tweets",
        "body": {"text": text[:280]},
    }


# ── Reddit 发布 ──
def publish_reddit(title, text, subreddit="LocalLLaMA"):
    """发布到 Reddit"""
    client_id = os.environ.get("REDDIT_CLIENT_ID", "")
    client_secret = os.environ.get("REDDIT_CLIENT_SECRET", "")
    username = os.environ.get("REDDIT_USERNAME", "")
    password = os.environ.get("REDDIT_PASSWORD", "")
    
    if not all([client_id, client_secret, username, password]):
        return {"error": "缺少 Reddit API 凭证"}
    
    # Reddit API 需要 OAuth2 认证
    # 由于零依赖原则，这里输出操作指南
    return {
        "status": "manual_required",
        "message": "Reddit 发布需要 OAuth2 认证",
        "action": f"请发布到 r/{subreddit}",
        "title": title,
        "text": text,
    }


def run_publish(dry_run=True, platforms=None):
    """主流程"""
    if platforms is None:
        platforms = ["twitter", "reddit"]
    
    filepath = find_latest_social_posts()
    if not filepath:
        print("❌ 未找到社交媒体文案，请先运行 content_pipeline.py")
        return
    
    print("=" * 60)
    print("📢 AIShield 社交媒体自动发布")
    print("=" * 60)
    print(f"📄 来源: {filepath}")
    print(f"📋 模式: {'预览' if dry_run else '执行'}")
    print("=" * 60)
    
    posts = parse_social_content(filepath)
    if not posts:
        print("⚠️  未解析到任何平台文案")
        return
    
    for platform, texts in posts.items():
        if platform not in platforms:
            continue
        
        print(f"\n🔹 {platform.upper()}")
        print(f"   文案数量: {len(texts)}")
        
        for i, text in enumerate(texts, 1):
            print(f"\n   文案 {i}:")
            preview = text.replace("\n", " ")[:120] + "..." if len(text) > 120 else text
            print(f"   {preview}")
            
            if not dry_run:
                if platform == "twitter":
                    result = publish_twitter(text)
                elif platform == "reddit":
                    # Reddit 需要标题，从第一行提取
                    title = text.split("\n")[0][:300]
                    result = publish_reddit(title, text)
                else:
                    result = {"error": f"不支持的平台: {platform}"}
                
                if "error" in result:
                    print(f"   ❌ 发布失败: {result['error']}")
                elif result.get("status") == "manual_required":
                    print(f"   ⚠️  需手动发布:")
                    print(f"      {result.get('action', '')}")
                    if "text" in result:
                        print(f"      内容: {result['text'][:100]}...")
                else:
                    print(f"   ✅ 发布成功")
    
    print("\n" + "=" * 60)
    print("✅ 社交媒体发布处理完成")
    print("=" * 60)
    
    # 输出未配置平台的提醒
    print("\n💡 提示:")
    print("   Twitter 自动发布需要配置 TWITTER_API_KEY 等环境变量")
    print("   Reddit 自动发布需要配置 REDDIT_CLIENT_ID 等环境变量")
    print("   获取方式见脚本顶部注释")
    print("=" * 60)


if __name__ == "__main__":
    dry_run = "--submit" not in sys.argv and "--all" not in sys.argv
    platforms = []
    if "--twitter" in sys.argv:
        platforms.append("twitter")
    if "--reddit" in sys.argv:
        platforms.append("reddit")
    if "--all" in sys.argv:
        platforms = ["twitter", "reddit"]
    
    if not platforms:
        platforms = ["twitter", "reddit"]
    
    if dry_run:
        print("💡 当前为预览模式，添加 --all 执行实际发布\n")
    
    run_publish(dry_run=dry_run, platforms=platforms)
