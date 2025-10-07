#!/usr/bin/env python3
"""
Helios Performance Profiler

A comprehensive performance profiling tool for the Helios code assistant.
Profiles completion latency, memory usage, model inference time, and system resources.
"""

import time
import psutil
import json
import asyncio
import aiohttp
import statistics
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import argparse
import sys


@dataclass
class ProfileResult:
    """Results from a single profiling run."""
    timestamp: str
    test_name: str
    completion_time_ms: float
    inference_time_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    tokens_generated: int
    prompt_length: int
    success: bool
    error_message: Optional[str] = None


@dataclass
class ProfileSummary:
    """Summary statistics from multiple profiling runs."""
    total_tests: int
    successful_tests: int
    failed_tests: int
    avg_completion_time_ms: float
    median_completion_time_ms: float
    p95_completion_time_ms: float
    p99_completion_time_ms: float
    avg_memory_usage_mb: float
    max_memory_usage_mb: float
    avg_cpu_usage_percent: float
    max_cpu_usage_percent: float
    total_tokens_generated: int
    avg_tokens_per_second: float


class HeliosProfiler:
    """Main profiler class for Helios performance testing."""
    
    def __init__(self, server_url: str = "http://localhost:8000"):
        self.server_url = server_url
        self.results: List[ProfileResult] = []
        
    async def profile_completion(self, prompt: str, test_name: str) -> ProfileResult:
        """Profile a single completion request."""
        start_time = time.time()
        start_memory = psutil.virtual_memory().used / 1024 / 1024
        start_cpu = psutil.cpu_percent()
        
        try:
            async with aiohttp.ClientSession() as session:
                # Time the inference request
                inference_start = time.time()
                
                async with session.post(
                    f"{self.server_url}/completion",
                    json={
                        "prompt": prompt,
                        "max_tokens": 100,
                        "temperature": 0.7
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        inference_time = (time.time() - inference_start) * 1000
                        
                        # Calculate metrics
                        completion_time = (time.time() - start_time) * 1000
                        end_memory = psutil.virtual_memory().used / 1024 / 1024
                        end_cpu = psutil.cpu_percent()
                        
                        memory_usage = end_memory - start_memory
                        cpu_usage = max(end_cpu - start_cpu, 0)
                        
                        tokens_generated = len(result.get('completion', '').split())
                        
                        return ProfileResult(
                            timestamp=datetime.now().isoformat(),
                            test_name=test_name,
                            completion_time_ms=completion_time,
                            inference_time_ms=inference_time,
                            memory_usage_mb=memory_usage,
                            cpu_usage_percent=cpu_usage,
                            tokens_generated=tokens_generated,
                            prompt_length=len(prompt),
                            success=True
                        )
                    else:
                        error_msg = f"HTTP {response.status}: {await response.text()}"
                        raise Exception(error_msg)
                        
        except Exception as e:
            completion_time = (time.time() - start_time) * 1000
            return ProfileResult(
                timestamp=datetime.now().isoformat(),
                test_name=test_name,
                completion_time_ms=completion_time,
                inference_time_ms=0,
                memory_usage_mb=0,
                cpu_usage_percent=0,
                tokens_generated=0,
                prompt_length=len(prompt),
                success=False,
                error_message=str(e)
            )
    
    async def run_test_suite(self, test_cases: List[Tuple[str, str]], iterations: int = 1) -> None:
        """Run a suite of performance tests."""
        print(f"Running performance tests with {iterations} iterations each...")
        print(f"Server: {self.server_url}")
        print(f"Test cases: {len(test_cases)}")
        print("-" * 60)
        
        total_tests = len(test_cases) * iterations
        completed = 0
        
        for test_name, prompt in test_cases:
            for i in range(iterations):
                result = await self.profile_completion(prompt, f"{test_name}_{i+1}")
                self.results.append(result)
                completed += 1
                
                status = "✓" if result.success else "✗"
                print(f"{status} [{completed:3d}/{total_tests}] {test_name} - "
                      f"{result.completion_time_ms:.1f}ms "
                      f"({result.tokens_generated} tokens)")
                
                # Small delay between requests
                await asyncio.sleep(0.1)
    
    def generate_summary(self) -> ProfileSummary:
        """Generate summary statistics from all results."""
        successful_results = [r for r in self.results if r.success]
        
        if not successful_results:
            return ProfileSummary(
                total_tests=len(self.results),
                successful_tests=0,
                failed_tests=len(self.results),
                avg_completion_time_ms=0,
                median_completion_time_ms=0,
                p95_completion_time_ms=0,
                p99_completion_time_ms=0,
                avg_memory_usage_mb=0,
                max_memory_usage_mb=0,
                avg_cpu_usage_percent=0,
                max_cpu_usage_percent=0,
                total_tokens_generated=0,
                avg_tokens_per_second=0
            )
        
        completion_times = [r.completion_time_ms for r in successful_results]
        memory_usage = [r.memory_usage_mb for r in successful_results]
        cpu_usage = [r.cpu_usage_percent for r in successful_results]
        total_tokens = sum(r.tokens_generated for r in successful_results)
        total_time_seconds = sum(r.completion_time_ms for r in successful_results) / 1000
        
        return ProfileSummary(
            total_tests=len(self.results),
            successful_tests=len(successful_results),
            failed_tests=len(self.results) - len(successful_results),
            avg_completion_time_ms=statistics.mean(completion_times),
            median_completion_time_ms=statistics.median(completion_times),
            p95_completion_time_ms=statistics.quantiles(completion_times, n=20)[18] if len(completion_times) > 1 else completion_times[0],
            p99_completion_time_ms=statistics.quantiles(completion_times, n=100)[98] if len(completion_times) > 1 else completion_times[0],
            avg_memory_usage_mb=statistics.mean(memory_usage),
            max_memory_usage_mb=max(memory_usage),
            avg_cpu_usage_percent=statistics.mean(cpu_usage),
            max_cpu_usage_percent=max(cpu_usage),
            total_tokens_generated=total_tokens,
            avg_tokens_per_second=total_tokens / total_time_seconds if total_time_seconds > 0 else 0
        )
    
    def save_results(self, filename: str) -> None:
        """Save detailed results and summary to JSON file."""
        summary = self.generate_summary()
        
        output = {
            "summary": asdict(summary),
            "results": [asdict(result) for result in self.results],
            "metadata": {
                "profiler_version": "1.0.0",
                "server_url": self.server_url,
                "system_info": {
                    "cpu_count": psutil.cpu_count(),
                    "memory_gb": psutil.virtual_memory().total / 1024 / 1024 / 1024,
                    "platform": sys.platform
                }
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(output, f, indent=2)
        
        print(f"\nResults saved to {filename}")
    
    def print_summary(self) -> None:
        """Print summary statistics to console."""
        summary = self.generate_summary()
        
        print("\n" + "=" * 60)
        print("PERFORMANCE SUMMARY")
        print("=" * 60)
        print(f"Total Tests:     {summary.total_tests}")
        print(f"Successful:      {summary.successful_tests}")
        print(f"Failed:          {summary.failed_tests}")
        print(f"Success Rate:    {summary.successful_tests/summary.total_tests*100:.1f}%")
        print()
        print("COMPLETION TIMES:")
        print(f"  Average:       {summary.avg_completion_time_ms:.1f}ms")
        print(f"  Median:        {summary.median_completion_time_ms:.1f}ms")
        print(f"  95th percentile: {summary.p95_completion_time_ms:.1f}ms")
        print(f"  99th percentile: {summary.p99_completion_time_ms:.1f}ms")
        print()
        print("RESOURCE USAGE:")
        print(f"  Avg Memory:    {summary.avg_memory_usage_mb:.1f}MB")
        print(f"  Max Memory:    {summary.max_memory_usage_mb:.1f}MB")
        print(f"  Avg CPU:       {summary.avg_cpu_usage_percent:.1f}%")
        print(f"  Max CPU:       {summary.max_cpu_usage_percent:.1f}%")
        print()
        print("THROUGHPUT:")
        print(f"  Total Tokens:  {summary.total_tokens_generated}")
        print(f"  Tokens/sec:    {summary.avg_tokens_per_second:.1f}")


def get_default_test_cases() -> List[Tuple[str, str]]:
    """Get default test cases for profiling."""
    return [
        ("simple_function", "def calculate_fibonacci(n):"),
        ("class_definition", "class UserManager:"),
        ("import_statement", "import"),
        ("complex_algorithm", "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    pivot = arr[len(arr) // 2]\n    left = [x for x in arr if x < pivot]\n    middle = [x for x in arr if x == pivot]\n    right = [x for x in arr if x > pivot]\n    return"),
        ("error_handling", "try:\n    result = process_data()\nexcept"),
        ("async_function", "async def fetch_data(url):\n    async with aiohttp.ClientSession() as session:\n        async with session.get(url) as response:"),
        ("list_comprehension", "squared_numbers = [x**2 for x in range(10) if"),
        ("docstring", 'def complex_function(a, b, c):\n    """'),
        ("decorator", "@"),
        ("context_manager", "with open('file.txt', 'r') as f:")
    ]


async def main():
    """Main entry point for the profiler."""
    parser = argparse.ArgumentParser(description="Helios Performance Profiler")
    parser.add_argument("--server", default="http://localhost:8000", 
                       help="Helios server URL (default: http://localhost:8000)")
    parser.add_argument("--iterations", type=int, default=5,
                       help="Number of iterations per test case (default: 5)")
    parser.add_argument("--output", default="helios_profile.json",
                       help="Output file for results (default: helios_profile.json)")
    parser.add_argument("--test-cases", help="JSON file with custom test cases")
    
    args = parser.parse_args()
    
    # Load test cases
    if args.test_cases:
        with open(args.test_cases, 'r') as f:
            test_data = json.load(f)
            test_cases = [(case["name"], case["prompt"]) for case in test_data["test_cases"]]
    else:
        test_cases = get_default_test_cases()
    
    # Initialize profiler
    profiler = HeliosProfiler(args.server)
    
    try:
        # Run tests
        await profiler.run_test_suite(test_cases, args.iterations)
        
        # Print and save results
        profiler.print_summary()
        profiler.save_results(args.output)
        
    except KeyboardInterrupt:
        print("\nProfiling interrupted by user")
        if profiler.results:
            profiler.print_summary()
            profiler.save_results(args.output)
    except Exception as e:
        print(f"Error during profiling: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())