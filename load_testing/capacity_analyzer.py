"""
Capacity Analyzer for AI ChatBot
Analyzes system resources and estimates capacity limits
"""

import psutil
import requests
import time
import json
from typing import Dict, List
import subprocess
import docker
import sys

class ChatBotCapacityAnalyzer:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.system_info = {}
        self.performance_metrics = {}
        
    def analyze_system_resources(self):
        """Analyze current system resources"""
        print("🔍 Analyzing System Resources...")
        
        # CPU Information
        cpu_count = psutil.cpu_count()
        cpu_usage = psutil.cpu_percent(interval=1)
        cpu_freq = psutil.cpu_freq()
        
        # Memory Information
        memory = psutil.virtual_memory()
        swap = psutil.swap_memory()
        
        # Disk Information
        disk = psutil.disk_usage('/')
        
        # Network Information
        network = psutil.net_io_counters()
        
        self.system_info = {
            "cpu": {
                "cores": cpu_count,
                "usage_percent": cpu_usage,
                "frequency_mhz": cpu_freq.current if cpu_freq else "Unknown",
                "max_frequency_mhz": cpu_freq.max if cpu_freq else "Unknown"
            },
            "memory": {
                "total_gb": round(memory.total / (1024**3), 2),
                "available_gb": round(memory.available / (1024**3), 2),
                "used_percent": memory.percent,
                "swap_total_gb": round(swap.total / (1024**3), 2),
                "swap_used_percent": swap.percent
            },
            "disk": {
                "total_gb": round(disk.total / (1024**3), 2),
                "free_gb": round(disk.free / (1024**3), 2),
                "used_percent": round(disk.used / disk.total * 100, 2)
            },
            "network": {
                "bytes_sent": network.bytes_sent,
                "bytes_recv": network.bytes_recv,
                "packets_sent": network.packets_sent,
                "packets_recv": network.packets_recv
            }
        }
        
        # Display system info
        print(f"💻 System Resources:")
        print(f"   CPU: {cpu_count} cores @ {cpu_usage}% usage")
        print(f"   Memory: {memory.available / (1024**3):.1f}GB available / {memory.total / (1024**3):.1f}GB total ({memory.percent}% used)")
        print(f"   Disk: {disk.free / (1024**3):.1f}GB free / {disk.total / (1024**3):.1f}GB total")
        
        return self.system_info
    
    def analyze_docker_containers(self):
        """Analyze Docker container resource usage"""
        print("\n🐳 Analyzing Docker Containers...")
        
        try:
            client = docker.from_env()
            containers = client.containers.list()
            
            container_stats = []
            for container in containers:
                if "chatbot" in container.name.lower():
                    stats = container.stats(stream=False)
                    
                    # Calculate CPU usage
                    cpu_delta = stats['cpu_stats']['cpu_usage']['total_usage'] - stats['precpu_stats']['cpu_usage']['total_usage']
                    system_delta = stats['cpu_stats']['system_cpu_usage'] - stats['precpu_stats']['system_cpu_usage']
                    cpu_usage = (cpu_delta / system_delta) * len(stats['cpu_stats']['cpu_usage']['percpu_usage']) * 100.0
                    
                    # Calculate memory usage
                    memory_usage = stats['memory_stats']['usage']
                    memory_limit = stats['memory_stats']['limit']
                    memory_percent = (memory_usage / memory_limit) * 100.0
                    
                    container_info = {
                        "name": container.name,
                        "status": container.status,
                        "cpu_percent": round(cpu_usage, 2),
                        "memory_usage_mb": round(memory_usage / (1024**2), 2),
                        "memory_limit_mb": round(memory_limit / (1024**2), 2),
                        "memory_percent": round(memory_percent, 2)
                    }
                    container_stats.append(container_info)
                    
                    print(f"   📦 {container.name}:")
                    print(f"      CPU: {cpu_usage:.1f}%")
                    print(f"      Memory: {memory_usage / (1024**2):.1f}MB / {memory_limit / (1024**2):.1f}MB ({memory_percent:.1f}%)")
            
            return container_stats
            
        except Exception as e:
            print(f"   ⚠️  Could not analyze Docker containers: {e}")
            return []
    
    def test_api_responsiveness(self):
        """Test basic API responsiveness"""
        print("\n🌐 Testing API Responsiveness...")
        
        endpoints = [
            ("/", "Root endpoint"),
            ("/status", "Status check"),
            ("/docs", "API documentation")
        ]
        
        api_results = []
        for endpoint, description in endpoints:
            try:
                start_time = time.time()
                response = requests.get(f"{self.base_url}{endpoint}", timeout=10)
                response_time = time.time() - start_time
                
                result = {
                    "endpoint": endpoint,
                    "description": description,
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "success": response.status_code == 200
                }
                api_results.append(result)
                
                status = "✅" if response.status_code == 200 else "❌"
                print(f"   {status} {endpoint}: {response.status_code} ({response_time:.3f}s)")
                
            except Exception as e:
                result = {
                    "endpoint": endpoint,
                    "description": description,
                    "error": str(e),
                    "success": False
                }
                api_results.append(result)
                print(f"   ❌ {endpoint}: Error - {e}")
        
        return api_results
    
    def estimate_capacity(self):
        """Estimate system capacity based on current resources"""
        print("\n📊 Estimating Capacity...")
        
        if not self.system_info:
            self.analyze_system_resources()
        
        # Base estimates (conservative)
        cpu_cores = self.system_info["cpu"]["cores"]
        available_memory_gb = self.system_info["memory"]["available_gb"]
        
        # Estimate concurrent users based on resources
        # Each concurrent user roughly needs:
        # - 0.1 CPU core for processing
        # - 50MB RAM for conversation memory
        # - Additional overhead for AI processing
        
        cpu_based_limit = cpu_cores * 8  # Conservative: 8 users per core
        memory_based_limit = int(available_memory_gb * 1024 / 100)  # 100MB per user (including overhead)
        
        # Take the more conservative estimate
        estimated_concurrent_users = min(cpu_based_limit, memory_based_limit)
        
        # Daily capacity estimation
        # Assume average user session: 10 messages over 5 minutes
        # Average response time: 3 seconds
        # User session duration: ~2 minutes active chatting
        sessions_per_hour = 60 / 2  # 30 sessions per hour per concurrent slot
        daily_sessions = sessions_per_hour * 24 * estimated_concurrent_users
        daily_messages = daily_sessions * 10  # 10 messages per session
        
        capacity_estimate = {
            "concurrent_users": estimated_concurrent_users,
            "daily_sessions": int(daily_sessions),
            "daily_messages": int(daily_messages),
            "cpu_limit": cpu_based_limit,
            "memory_limit": memory_based_limit,
            "bottleneck": "CPU" if cpu_based_limit < memory_based_limit else "Memory"
        }
        
        print(f"🎯 Capacity Estimates:")
        print(f"   Concurrent Users: {estimated_concurrent_users}")
        print(f"   Daily Sessions: {daily_sessions:,.0f}")
        print(f"   Daily Messages: {daily_messages:,.0f}")
        print(f"   Primary Bottleneck: {capacity_estimate['bottleneck']}")
        
        # Scaling recommendations
        print(f"\n📈 Scaling Recommendations:")
        if estimated_concurrent_users < 10:
            print("   📱 Current: Suitable for small applications")
            print("   💡 Upgrade: Add more RAM or CPU cores")
        elif estimated_concurrent_users < 50:
            print("   🏢 Current: Suitable for medium applications")
            print("   💡 Upgrade: Consider load balancing")
        else:
            print("   🏭 Current: Suitable for large applications")
            print("   💡 Upgrade: Implement horizontal scaling")
        
        return capacity_estimate
    
    def analyze_bottlenecks(self):
        """Identify potential bottlenecks"""
        print("\n🔍 Analyzing Potential Bottlenecks...")
        
        bottlenecks = []
        
        # Check CPU usage
        if self.system_info["cpu"]["usage_percent"] > 80:
            bottlenecks.append({
                "type": "CPU",
                "severity": "High",
                "description": f"CPU usage is {self.system_info['cpu']['usage_percent']}%"
            })
        elif self.system_info["cpu"]["usage_percent"] > 60:
            bottlenecks.append({
                "type": "CPU", 
                "severity": "Medium",
                "description": f"CPU usage is {self.system_info['cpu']['usage_percent']}%"
            })
        
        # Check memory usage
        if self.system_info["memory"]["used_percent"] > 85:
            bottlenecks.append({
                "type": "Memory",
                "severity": "High", 
                "description": f"Memory usage is {self.system_info['memory']['used_percent']}%"
            })
        elif self.system_info["memory"]["used_percent"] > 70:
            bottlenecks.append({
                "type": "Memory",
                "severity": "Medium",
                "description": f"Memory usage is {self.system_info['memory']['used_percent']}%"
            })
        
        # Check disk space
        if self.system_info["disk"]["used_percent"] > 90:
            bottlenecks.append({
                "type": "Disk",
                "severity": "High",
                "description": f"Disk usage is {self.system_info['disk']['used_percent']}%"
            })
        elif self.system_info["disk"]["used_percent"] > 80:
            bottlenecks.append({
                "type": "Disk",
                "severity": "Medium", 
                "description": f"Disk usage is {self.system_info['disk']['used_percent']}%"
            })
        
        # Check available memory
        if self.system_info["memory"]["available_gb"] < 1:
            bottlenecks.append({
                "type": "Memory",
                "severity": "Critical",
                "description": f"Only {self.system_info['memory']['available_gb']:.1f}GB RAM available"
            })
        
        if bottlenecks:
            print("   ⚠️  Potential Bottlenecks Found:")
            for bottleneck in bottlenecks:
                severity_icon = "🔴" if bottleneck["severity"] == "Critical" else "🟠" if bottleneck["severity"] == "High" else "🟡"
                print(f"   {severity_icon} {bottleneck['type']}: {bottleneck['description']}")
        else:
            print("   ✅ No significant bottlenecks detected")
        
        return bottlenecks
    
    def run_complete_analysis(self):
        """Run complete capacity analysis"""
        print("🚀 Starting Complete Capacity Analysis")
        print("=" * 50)
        
        # Analyze system resources
        system_info = self.analyze_system_resources()
        
        # Analyze Docker containers
        container_stats = self.analyze_docker_containers()
        
        # Test API responsiveness
        api_results = self.test_api_responsiveness()
        
        # Estimate capacity
        capacity = self.estimate_capacity()
        
        # Analyze bottlenecks
        bottlenecks = self.analyze_bottlenecks()
        
        # Generate summary report
        print(f"\n📋 CAPACITY ANALYSIS SUMMARY")
        print("=" * 50)
        
        print(f"🎯 Current Capacity:")
        print(f"   Estimated Concurrent Users: {capacity['concurrent_users']}")
        print(f"   Estimated Daily Messages: {capacity['daily_messages']:,}")
        print(f"   Primary Bottleneck: {capacity['bottleneck']}")
        
        print(f"\n💻 System Health:")
        api_healthy = all(result.get("success", False) for result in api_results)
        system_healthy = len(bottlenecks) == 0
        
        if api_healthy and system_healthy:
            print("   ✅ System is healthy and ready for load testing")
        elif api_healthy:
            print("   ⚠️  API is healthy but system has performance concerns")
        else:
            print("   ❌ System needs attention before load testing")
        
        print(f"\n🚀 Next Steps:")
        print("   1. Run load tests to validate capacity estimates")
        print("   2. Monitor system during peak usage")
        print("   3. Plan scaling based on actual usage patterns")
        
        if capacity['concurrent_users'] < 20:
            print("   4. Consider upgrading hardware for better performance")
        
        return {
            "system_info": system_info,
            "container_stats": container_stats,
            "api_results": api_results,
            "capacity": capacity,
            "bottlenecks": bottlenecks
        }

def main():
    """Run capacity analysis"""
    analyzer = ChatBotCapacityAnalyzer()
    
    print("🔍 AI ChatBot Capacity Analyzer")
    print("Choose analysis type:")
    print("1. Quick Analysis (System + API)")
    print("2. Complete Analysis (Full Report)")
    print("3. Just System Resources")
    print("4. Just Capacity Estimate")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        analyzer.analyze_system_resources()
        analyzer.test_api_responsiveness()
        analyzer.estimate_capacity()
    elif choice == "2":
        analyzer.run_complete_analysis()
    elif choice == "3":
        analyzer.analyze_system_resources()
        analyzer.analyze_bottlenecks()
    elif choice == "4":
        analyzer.analyze_system_resources()
        analyzer.estimate_capacity()
    else:
        print("Invalid choice. Running complete analysis...")
        analyzer.run_complete_analysis()

if __name__ == "__main__":
    main() 