#!/usr/bin/env python3
"""
Helios Server Monitoring Tool
Real-time monitoring of server performance and health
"""

import time
import requests
import json
import argparse
from datetime import datetime
import sys

class HeliosMonitor:
    def __init__(self, server_url="http://localhost:8000"):
        self.server_url = server_url
        self.monitoring = False
        
    def check_health(self):
        """Check server health"""
        try:
            response = requests.get(f"{self.server_url}/health", timeout=5)
            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response.elapsed.total_seconds(),
                "data": response.json() if response.status_code == 200 else None
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "unreachable",
                "response_time": None,
                "error": str(e)
            }
    
    def get_detailed_status(self):
        """Get detailed server status"""
        try:
            response = requests.get(f"{self.server_url}/status", timeout=5)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.exceptions.RequestException:
            return None
    
    def test_completion(self):
        """Test completion endpoint"""
        test_request = {
            "code": "def hello():",
            "language": "python",
            "position": {"line": 0, "character": 12},
            "filename": "test.py"
        }
        
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.server_url}/complete",
                json=test_request,
                timeout=10
            )
            end_time = time.time()
            
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "response_time": end_time - start_time,
                "status_code": response.status_code,
                "data": response.json() if response.status_code == 200 else None
            }
        except requests.exceptions.RequestException as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    def monitor_continuous(self, interval=30):
        """Continuously monitor server"""
        print(f"🔍 Starting continuous monitoring (interval: {interval}s)")
        print("Press Ctrl+C to stop")
        print("-" * 60)
        
        self.monitoring = True
        
        try:
            while self.monitoring:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Health check
                health = self.check_health()
                status_icon = "🟢" if health["status"] == "healthy" else "🔴"
                
                print(f"[{timestamp}] {status_icon} Health: {health['status']}")
                
                if health["status"] == "healthy":
                    print(f"  └─ Response time: {health['response_time']:.3f}s")
                    
                    # Detailed status
                    status = self.get_detailed_status()
                    if status:
                        print(f"  └─ Model loaded: {status.get('model_loaded', 'Unknown')}")
                        print(f"  └─ Uptime: {status.get('uptime', 0):.1f}s")
                    
                    # Test completion
                    completion = self.test_completion()
                    if completion["status"] == "success":
                        print(f"  └─ Completion test: ✅ ({completion['response_time']:.3f}s)")
                    else:
                        print(f"  └─ Completion test: ❌ ({completion.get('error', 'Failed')})")
                
                else:
                    print(f"  └─ Error: {health.get('error', 'Unknown')}")
                
                print()
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")
            self.monitoring = False
    
    def run_health_check(self):
        """Run a single health check"""
        print("🏥 Helios Server Health Check")
        print("-" * 30)
        
        health = self.check_health()
        
        if health["status"] == "healthy":
            print("✅ Server is healthy")
            print(f"   Response time: {health['response_time']:.3f}s")
            
            if health["data"]:
                data = health["data"]
                print(f"   Model loaded: {data.get('model_loaded', 'Unknown')}")
                print(f"   Server version: {data.get('server_version', 'Unknown')}")
                print(f"   Uptime: {data.get('uptime', 0):.1f}s")
        
        elif health["status"] == "unhealthy":
            print("⚠️  Server is unhealthy")
            print(f"   Response time: {health['response_time']:.3f}s")
        
        else:
            print("❌ Server is unreachable")
            print(f"   Error: {health.get('error', 'Unknown')}")
        
        return health["status"] == "healthy"
    
    def run_performance_test(self):
        """Run performance tests"""
        print("🚀 Helios Performance Test")
        print("-" * 25)
        
        # Multiple completion tests
        response_times = []
        success_count = 0
        
        for i in range(5):
            print(f"Test {i+1}/5... ", end="", flush=True)
            result = self.test_completion()
            
            if result["status"] == "success":
                response_times.append(result["response_time"])
                success_count += 1
                print(f"✅ {result['response_time']:.3f}s")
            else:
                print(f"❌ {result.get('error', 'Failed')}")
        
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            min_time = min(response_times)
            max_time = max(response_times)
            
            print(f"\n📊 Results:")
            print(f"   Success rate: {success_count}/5 ({success_count/5*100:.1f}%)")
            print(f"   Average time: {avg_time:.3f}s")
            print(f"   Min time: {min_time:.3f}s")
            print(f"   Max time: {max_time:.3f}s")
        else:
            print("\n❌ All tests failed")

def main():
    parser = argparse.ArgumentParser(description="Helios Server Monitor")
    parser.add_argument("--url", default="http://localhost:8000",
                       help="Server URL (default: http://localhost:8000)")
    parser.add_argument("--interval", type=int, default=30,
                       help="Monitoring interval in seconds (default: 30)")
    
    subparsers = parser.add_subparsers(dest="command", help="Commands")
    
    # Health check command
    subparsers.add_parser("health", help="Run health check")
    
    # Monitor command
    monitor_parser = subparsers.add_parser("monitor", help="Continuous monitoring")
    monitor_parser.add_argument("--interval", type=int, default=30,
                               help="Monitoring interval in seconds")
    
    # Performance test command
    subparsers.add_parser("test", help="Run performance test")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    monitor = HeliosMonitor(args.url)
    
    if args.command == "health":
        success = monitor.run_health_check()
        sys.exit(0 if success else 1)
    
    elif args.command == "monitor":
        interval = getattr(args, 'interval', 30)
        monitor.monitor_continuous(interval)
    
    elif args.command == "test":
        monitor.run_performance_test()

if __name__ == "__main__":
    main()