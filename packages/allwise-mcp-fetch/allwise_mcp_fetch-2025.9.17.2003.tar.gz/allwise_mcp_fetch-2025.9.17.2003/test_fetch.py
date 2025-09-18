#!/usr/bin/env python3
"""
测试fetch功能 - 抓取Yahoo Finance ENPH股票信息
"""

import asyncio
import sys
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_server_fetch.server import fetch_url


async def test_fetch():
    """测试抓取ENPH股票信息"""
    url = "https://finance.yahoo.com/quote/ENPH"
    print(f"正在抓取: {url}")

    try:
        content, prefix = await fetch_url(url, "Mozilla/5.0", False, None)
        print("抓取成功！")
        print(f"内容长度: {len(content)} 字符")
        print("\n股票信息:")
        print(content[:1000])
        print("...")
    except Exception as e:
        print(f"抓取失败: {e}")


if __name__ == "__main__":
    asyncio.run(test_fetch())
