#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
V2EX Monitor - V2EX 精选内容监控脚本
获取 V2EX 最新主题并格式化输出
"""

import sys
import json
import time
from datetime import datetime
from typing import List, Dict, Optional

try:
    import requests
except ImportError:
    print("Error: requests module not found. Install with: pip install requests")
    sys.exit(1)


V2EX_API_URL = "https://www.v2ex.com/api/topics/latest.json"


def fetch_topics(limit: int = 20) -> List[Dict]:
    """
    获取 V2EX 最新主题

    Args:
        limit: 获取数量

    Returns:
        主题列表
    """
    try:
        response = requests.get(V2EX_API_URL, timeout=10)
        response.raise_for_status()
        topics = response.json()
        return topics[:limit] if len(topics) > limit else topics
    except requests.RequestException as e:
        print(f"Error fetching V2EX topics: {e}")
        return []


def filter_topics(topics: List[Dict], min_replies: int = 3) -> List[Dict]:
    """
    过滤主题

    Args:
        topics: 主题列表
        min_replies: 最小回复数

    Returns:
        过滤后的主题列表
    """
    return [t for t in topics if t.get("replies", 0) >= min_replies]


def format_topic(topic: Dict) -> str:
    """
    格式化单个主题

    Args:
        topic: 主题数据

    Returns:
        格式化后的字符串
    """
    title = topic.get("title", "无标题")
    url = topic.get("url", "")
    node = topic.get("node", {}).get("title", "")
    replies = topic.get("replies", 0)
    member = topic.get("member", {}).get("username", "")
    created = topic.get("created", 0)
    created_str = datetime.fromtimestamp(created).strftime("%H:%M")

    return f"""
**{title}**

📍 {node} | 👤 {member} | 💬 {replies} | ⏰ {created_str}

🔗 {url}
---
"""


def format_topics(topics: List[Dict], count: int = 5) -> str:
    """
    格式化多个主题

    Args:
        topics: 主题列表
        count: 显示数量

    Returns:
        格式化后的字符串
    """
    if not topics:
        return "📭 暂无符合条件的主题"

    display_count = min(count, len(topics))
    header = f"🔥 V2EX 今日精选 ({datetime.now().strftime('%Y-%m-%d')})\n\n"
    content = "".join([format_topic(t) for t in topics[:display_count]])
    return header + content


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="V2EX Monitor - 获取 V2EX 精选内容")
    parser.add_argument("--count", type=int, default=5, help="精选数量（默认: 5）")
    parser.add_argument("--min-replies", type=int, default=3, help="最小回复数（默认: 3）")
    parser.add_argument("--json", action="store_true", help="输出 JSON 格式")

    args = parser.parse_args()

    # 获取主题
    topics = fetch_topics(limit=20)

    if not topics:
        print("无法获取 V2EX 主题")
        return 1

    # 过滤主题
    filtered = filter_topics(topics, min_replies=args.min_replies)

    # 输出
    if args.json:
        print(json.dumps(filtered[:args.count], indent=2, ensure_ascii=False))
    else:
        print(format_topics(filtered, count=args.count))

    return 0


if __name__ == "__main__":
    sys.exit(main())
