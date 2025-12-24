#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
大模型 API 性能测试脚本
测试并发性能、延迟和吞吐量
"""

import asyncio
import aiohttp
import time
import statistics
from typing import List, Dict
import json


API_URL = "http://localhost:8000/v1/chat/completions"
MODEL_NAME = "qwen2.5-coder-32b-instruct"


test_prompts = [
    "解释一下Python的装饰器是什么",
    "写一个二分查找算法",
    "什么是RESTful API？",
    "解释TCP三次握手过程",
    "用JavaScript实现防抖函数",
    "什么是Docker容器？",
    "解释HTTP和HTTPS的区别",
    "写一个单例模式的Python实现",
    "什么是Git的分支策略？",
    "解释数据库索引的作用",
]


async def send_request(session: aiohttp.ClientSession, prompt: str) -> Dict:
    """发送单个请求"""
    start_time = time.time()

    payload = {
        "model": MODEL_NAME,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 500
    }

    try:
        async with session.post(API_URL, json=payload) as response:
            result = await response.json()
            end_time = time.time()

            return {
                "success": response.status == 200,
                "latency": end_time - start_time,
                "tokens": result.get("usage", {}).get("completion_tokens", 0),
                "error": None if response.status == 200 else str(result)
            }
    except Exception as e:
        end_time = time.time()
        return {
            "success": False,
            "latency": end_time - start_time,
            "tokens": 0,
            "error": str(e)
        }


async def run_concurrent_test(num_requests: int, concurrency: int):
    """运行并发测试"""
    print(f"\n{'='*60}")
    print(f"并发测试: {num_requests} 个请求, 并发数: {concurrency}")
    print(f"{'='*60}\n")

    async with aiohttp.ClientSession() as session:
        semaphore = asyncio.Semaphore(concurrency)

        async def bounded_request(prompt):
            async with semaphore:
                return await send_request(session, prompt)

        # 循环使用测试提示词
        prompts = [test_prompts[i % len(test_prompts)] for i in range(num_requests)]

        start_time = time.time()
        results = await asyncio.gather(*[bounded_request(p) for p in prompts])
        total_time = time.time() - start_time

    # 统计结果
    successful = [r for r in results if r["success"]]
    failed = [r for r in results if not r["success"]]

    if successful:
        latencies = [r["latency"] for r in successful]
        tokens = [r["tokens"] for r in successful]

        print(f"总请求数: {num_requests}")
        print(f"成功: {len(successful)}, 失败: {len(failed)}")
        print(f"总耗时: {total_time:.2f}秒")
        print(f"吞吐量: {len(successful) / total_time:.2f} 请求/秒")
        print(f"\n延迟统计:")
        print(f"  平均: {statistics.mean(latencies):.2f}秒")
        print(f"  中位数: {statistics.median(latencies):.2f}秒")
        print(f"  最小: {min(latencies):.2f}秒")
        print(f"  最大: {max(latencies):.2f}秒")
        if len(latencies) > 1:
            print(f"  标准差: {statistics.stdev(latencies):.2f}秒")

        print(f"\nToken统计:")
        print(f"  平均token数: {statistics.mean(tokens):.0f}")
        print(f"  总token数: {sum(tokens)}")
        print(f"  Token/秒: {sum(tokens) / total_time:.2f}")

    if failed:
        print(f"\n失败请求数: {len(failed)}")
        for i, f in enumerate(failed[:3], 1):
            print(f"  错误 {i}: {f['error']}")


async def main():
    """主函数"""
    print("="*60)
    print("大模型 API 性能测试")
    print(f"API: {API_URL}")
    print(f"模型: {MODEL_NAME}")
    print("="*60)

    # 测试场景
    test_scenarios = [
        (5, 1),    # 5个请求，1个并发（顺序测试）
        (10, 2),   # 10个请求，2个并发
        (10, 5),   # 10个请求，5个并发
        (20, 10),  # 20个请求，10个并发
    ]

    for num_requests, concurrency in test_scenarios:
        await run_concurrent_test(num_requests, concurrency)
        await asyncio.sleep(2)  # 测试之间等待2秒

    print(f"\n{'='*60}")
    print("测试完成！")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    asyncio.run(main())
