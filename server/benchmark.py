#!/usr/bin/env python3
"""
Helios Server Performance Benchmark Tool
Tests completion performance under various conditions
"""

import asyncio
import time
import statistics
import json
import argparse
from typing import List, Dict, Any
import aiohttp
import matplotlib.pyplot as plt
import seaborn as sns

class HeliosBenchmark:
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.results: List[Dict[str, Any]] = []
    
    async def single_completion_test(self, session: aiohttp.ClientSession, 
                                   request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Test a single completion request"""
        start_time = time.time()
        
        try:
            async with session.post(f"{self.server_url}/complete", 
                                  json=request_data) as response:
                if response.status == 200:
                    result = await response.json()
                    end_time = time.time()
                    
                    return {
                        "success": True,
                        "response_time": end_time - start_time,
                        "suggestion_length": len(result.get("suggestion", "")),
                        "confidence": result.get("confidence", 0),
                        "server_processing_time": result.get("processing_time", 0)
                    }
                else:
                    return {
                        "success": False,
                        "response_time": time.time() - start_time,
                        "error": f"HTTP {response.status}"
                    }
        except Exception as e:
            return {
                "success": False,
                "response_time": time.time() - start_time,
                "error": str(e)
            }
    
    async def concurrent_test(self, num_requests: int = 10, 
                            request_data: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Test multiple concurrent requests"""
        if not request_data:
            request_data = {
                "code": "def fibonacci(n):\n    if n <= 1:\n        return n\n    ",
                "language": "python",
                "position": {"line": 3, "character": 4},
                "filename": "test.py"
            }
        
        async with aiohttp.ClientSession() as session:
            tasks = [
                self.single_completion_test(session, request_data)
                for _ in range(num_requests)
            ]
            
            results = await asyncio.gather(*tasks)
            return results
    
    async def load_test(self, duration_seconds: int = 60, 
                       requests_per_second: int = 5) -> Dict[str, Any]:
        """Run a load test for specified duration"""
        print(f"Running load test: {requests_per_second} req/sec for {duration_seconds}s")
        
        start_time = time.time()
        end_time = start_time + duration_seconds
        interval = 1.0 / requests_per_second
        
        request_data = {
            "code": "function calculateSum(arr) {\n    let total = 0;\n    ",
            "language": "javascript",
            "position": {"line": 1, "character": 18},
            "filename": "utils.js"
        }
        
        all_results = []
        
        async with aiohttp.ClientSession() as session:
            while time.time() < end_time:
                batch_start = time.time()
                
                # Send requests for this second
                tasks = [
                    self.single_completion_test(session, request_data)
                    for _ in range(requests_per_second)
                ]
                
                batch_results = await asyncio.gather(*tasks)
                all_results.extend(batch_results)
                
                # Wait for the rest of the second
                elapsed = time.time() - batch_start
                if elapsed < 1.0:
                    await asyncio.sleep(1.0 - elapsed)
        
        # Analyze results
        successful_requests = [r for r in all_results if r.get("success", False)]
        failed_requests = [r for r in all_results if not r.get("success", False)]
        
        if successful_requests:
            response_times = [r["response_time"] for r in successful_requests]
            avg_response_time = statistics.mean(response_times)
            p95_response_time = statistics.quantiles(response_times, n=20)[18] if len(response_times) > 20 else max(response_times)
        else:
            avg_response_time = 0
            p95_response_time = 0
        
        return {
            "total_requests": len(all_results),
            "successful_requests": len(successful_requests),
            "failed_requests": len(failed_requests),
            "success_rate": len(successful_requests) / len(all_results) * 100,
            "avg_response_time": avg_response_time,
            "p95_response_time": p95_response_time,
            "requests_per_second": len(all_results) / duration_seconds,
            "duration": duration_seconds
        }
    
    def generate_test_cases(self) -> List[Dict[str, Any]]:
        """Generate various test cases for different scenarios"""
        test_cases = [
            {
                "name": "Python function",
                "data": {
                    "code": "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    ",
                    "language": "python",
                    "position": {"line": 4, "character": 4},
                    "filename": "sorting.py"
                }
            },
            {
                "name": "JavaScript class",
                "data": {
                    "code": "class Calculator {\n    constructor() {\n        this.history = [];\n    }\n    \n    add(a, b) {\n        ",
                    "language": "javascript",
                    "position": {"line": 6, "character": 8},
                    "filename": "calculator.js"
                }
            },
            {
                "name": "TypeScript interface",
                "data": {
                    "code": "interface User {\n    id: number;\n    name: string;\n    email: string;\n}\n\nfunction createUser(userData: Partial<User>): User {\n    ",
                    "language": "typescript",
                    "position": {"line": 7, "character": 4},
                    "filename": "user.ts"
                }
            },
            {
                "name": "Complex algorithm",
                "data": {
                    "code": "def dijkstra(graph, start):\n    distances = {node: float('infinity') for node in graph}\n    distances[start] = 0\n    unvisited = set(graph.keys())\n    \n    while unvisited:\n        ",
                    "language": "python",
                    "position": {"line": 6, "character": 8},
                    "filename": "graph.py"
                }
            }
        ]
        
        return test_cases
    
    async def run_comprehensive_benchmark(self) -> Dict[str, Any]:
        """Run a comprehensive benchmark suite"""
        print("🚀 Starting Helios Performance Benchmark")
        print("=" * 50)
        
        # Test server health
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{self.server_url}/health") as response:
                    if response.status != 200:
                        raise Exception(f"Server health check failed: {response.status}")
        except Exception as e:
            print(f"❌ Server not available: {e}")
            return {}
        
        print("✅ Server is healthy")
        
        results = {
            "test_timestamp": time.time(),
            "server_url": self.server_url,
            "tests": {}
        }
        
        # Test 1: Single request latency
        print("\n📊 Test 1: Single Request Latency")
        test_cases = self.generate_test_cases()
        
        for test_case in test_cases:
            print(f"   Testing: {test_case['name']}")
            result = await self.concurrent_test(1, test_case['data'])
            if result and result[0].get("success"):
                print(f"   Response time: {result[0]['response_time']:.3f}s")
                results["tests"][f"single_{test_case['name'].replace(' ', '_')}"] = result[0]
        
        # Test 2: Concurrent requests
        print("\n📊 Test 2: Concurrent Requests (10 simultaneous)")
        concurrent_results = await self.concurrent_test(10)
        successful = [r for r in concurrent_results if r.get("success", False)]
        
        if successful:
            response_times = [r["response_time"] for r in successful]
            results["tests"]["concurrent_10"] = {
                "success_rate": len(successful) / len(concurrent_results) * 100,
                "avg_response_time": statistics.mean(response_times),
                "max_response_time": max(response_times),
                "min_response_time": min(response_times)
            }
            print(f"   Success rate: {results['tests']['concurrent_10']['success_rate']:.1f}%")
            print(f"   Avg response time: {results['tests']['concurrent_10']['avg_response_time']:.3f}s")
        
        # Test 3: Load test
        print("\n📊 Test 3: Load Test (30 seconds)")
        load_results = await self.load_test(duration_seconds=30, requests_per_second=3)
        results["tests"]["load_test"] = load_results
        
        print(f"   Total requests: {load_results['total_requests']}")
        print(f"   Success rate: {load_results['success_rate']:.1f}%")
        print(f"   Avg response time: {load_results['avg_response_time']:.3f}s")
        print(f"   P95 response time: {load_results['p95_response_time']:.3f}s")
        
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str = "benchmark_results.json"):
        """Save benchmark results to file"""
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\n💾 Results saved to {filename}")
    
    def generate_report(self, results: Dict[str, Any]):
        """Generate a performance report"""
        if not results:
            return
        
        print("\n📈 Performance Report")
        print("=" * 50)
        
        # Summary statistics
        if "load_test" in results["tests"]:
            load_test = results["tests"]["load_test"]
            print(f"Overall Performance:")
            print(f"  Success Rate: {load_test['success_rate']:.1f}%")
            print(f"  Throughput: {load_test['requests_per_second']:.1f} req/sec")
            print(f"  Avg Latency: {load_test['avg_response_time']:.3f}s")
            print(f"  P95 Latency: {load_test['p95_response_time']:.3f}s")
        
        # Recommendations
        print(f"\n💡 Recommendations:")
        
        if "load_test" in results["tests"]:
            success_rate = results["tests"]["load_test"]["success_rate"]
            avg_time = results["tests"]["load_test"]["avg_response_time"]
            
            if success_rate < 95:
                print("  ⚠️  Low success rate - consider reducing request frequency")
            
            if avg_time > 2.0:
                print("  ⚠️  High latency - consider using a smaller model or better hardware")
            elif avg_time < 0.5:
                print("  ✅ Excellent latency performance")
            
            if success_rate >= 95 and avg_time < 1.0:
                print("  🎉 Outstanding performance! Consider increasing request frequency.")

async def main():
    parser = argparse.ArgumentParser(description="Helios Performance Benchmark")
    parser.add_argument("--url", default="http://localhost:8000", 
                       help="Server URL (default: http://localhost:8000)")
    parser.add_argument("--output", default="benchmark_results.json",
                       help="Output file for results")
    parser.add_argument("--duration", type=int, default=30,
                       help="Load test duration in seconds")
    
    args = parser.parse_args()
    
    benchmark = HeliosBenchmark(args.url)
    results = await benchmark.run_comprehensive_benchmark()
    
    if results:
        benchmark.save_results(results, args.output)
        benchmark.generate_report(results)
    else:
        print("❌ Benchmark failed - check server availability")

if __name__ == "__main__":
    asyncio.run(main())