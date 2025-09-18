#!/usr/bin/env python3
"""
测试fetch功能 - 包括正常抓取和超时测试
"""

import asyncio
import sys
import time
from pathlib import Path

# 添加src目录到Python路径
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp_server_fetch.server import fetch_url


async def test_normal_fetch():
    """测试正常抓取"""
    print("=== 测试1: 正常抓取 ===")
    url = "https://httpbin.org/html"  # 使用一个快速响应的测试网站
    print(f"正在抓取: {url}")

    start_time = time.time()
    try:
        content, prefix = await fetch_url(url, "Mozilla/5.0", False, None)
        end_time = time.time()
        print(f"✅ 抓取成功！耗时: {end_time - start_time:.2f}秒")
        print(f"内容长度: {len(content)} 字符")
        print(f"内容预览: {content[:200]}...")
    except Exception as e:
        end_time = time.time()
        print(f"❌ 抓取失败: {e}")
        print(f"耗时: {end_time - start_time:.2f}秒")


async def test_timeout():
    """测试超时功能"""
    print("\n=== 测试2: 超时测试 ===")
    # 使用一个会故意延迟的URL来测试超时
    url = "https://httpbin.org/delay/5"  # 延迟5秒，应该会超时（3秒超时）
    print(f"正在抓取延迟URL: {url}")
    print("预期: 3秒后应该超时")

    start_time = time.time()
    try:
        content, prefix = await fetch_url(url, "Mozilla/5.0", False, None)
        end_time = time.time()
        print(f"❌ 意外成功！耗时: {end_time - start_time:.2f}秒")
    except Exception as e:
        end_time = time.time()
        print(f"✅ 超时测试通过！耗时: {end_time - start_time:.2f}秒")
        print(f"错误信息: {e}")


async def test_slow_website():
    """测试慢速网站"""
    print("\n=== 测试3: 慢速网站测试 ===")
    url = "https://www.google.com"  # 使用Google测试
    print(f"正在抓取: {url}")

    start_time = time.time()
    try:
        content, prefix = await fetch_url(url, "Mozilla/5.0", False, None)
        end_time = time.time()
        print(f"✅ 抓取成功！耗时: {end_time - start_time:.2f}秒")
        print(f"内容长度: {len(content)} 字符")
        print(f"内容预览: {content[:200]}...")
    except Exception as e:
        end_time = time.time()
        print(f"❌ 抓取失败: {e}")
        print(f"耗时: {end_time - start_time:.2f}秒")


async def main():
    """运行所有测试"""
    print("开始测试 fetch 功能...")

    await test_normal_fetch()
    await test_timeout()
    await test_slow_website()

    print("\n=== 测试完成 ===")


if __name__ == "__main__":
    asyncio.run(main())
