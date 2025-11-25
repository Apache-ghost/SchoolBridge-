#!/usr/bin/env python3
"""
Virtual Machine Manager
Simulates real computer hardware and resources
"""

import time
import threading
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import random

# Mock psutil functionality since we can't install it
class MockPsutil:
    @staticmethod
    def cpu_percent():
        return random.uniform(10, 80)
    
    @staticmethod
    def virtual_memory():
        class Memory:
            percent = random.uniform(30, 70)
            total = 8 * 1024 * 1024 * 1024  # 8GB
            available = int(total * (1 - percent/100))
        return Memory()
    
    @staticmethod
    def disk_usage(path):
        class Disk:
            total = 512 * 1024 * 1024 * 1024  # 512GB
            free = int(total * random.uniform(0.3, 0.8))
            used = total - free
        return Disk()
    
    @staticmethod
    def net_io_counters():
        class Network:
            bytes_sent = random.randint(1000000, 10000000)
            bytes_recv = random.randint(1000000, 10000000)
        return Network()
    
    @staticmethod
    def boot_time():
        return time.time() - random.randint(3600, 86400)

try:
    import psutil
except ImportError:
    psutil = MockPsutil()

class VirtualHardware:
    """Simulates computer hardware components"""
    
    def __init__(self, node_id: str, cpu_cores: int, memory_gb: int, storage_gb: int):
        self.node_id = node_id
        self.cpu_cores = cpu_cores
        self.memory_gb = memory_gb
        self.storage_gb = storage_gb
        
        # Hardware specifications
        self.cpu_model = f"Virtual CPU {cpu_cores}-Core 3.2GHz"
        self.memory_type = "DDR4"
        self.storage_type = "NVMe SSD"
        self.network_adapter = "Virtual Ethernet 1Gbps"
        
        # Current usage
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.network_rx_bytes = 0
        self.network_tx_bytes = 0
        self.disk_read_bytes = 0
        self.disk_write_bytes = 0
        
        # Performance monitoring
        self.performance_history = []
        self.monitoring_active = False
        self.monitor_thread = None
        
        # Boot information
        self.boot_time = datetime.now()
        self.is_powered_on = False
        
        print(f"🖥️ Virtual Hardware initialized for {node_id}")
        print(f"   💻 CPU: {self.cpu_model}")
        print(f"   🧠 Memory: {memory_gb}GB {self.memory_type}")
        print(f"   💾 Storage: {storage_gb}GB {self.storage_type}")
    
    def power_on(self):
        """Simulate powering on the virtual machine"""
        if self.is_powered_on:
            print("⚡ Virtual machine is already powered on")
            return
        
        print("🔄 Powering on virtual machine...")
        print("🔍 POST (Power-On Self-Test)...")
        time.sleep(1)
        
        print("💾 Memory test: OK")
        print("💻 CPU initialization: OK")
        print("🔌 Hardware detection: OK")
        
        self.is_powered_on = True
        self.boot_time = datetime.now()
        
        # Start performance monitoring
        self.start_performance_monitoring()
        
        print("✅ Virtual machine powered on successfully")
    
    def power_off(self):
        """Simulate powering off the virtual machine"""
        if not self.is_powered_on:
            print("⚡ Virtual machine is already powered off")
            return
        
        print("🔄 Shutting down virtual machine...")
        
        # Stop monitoring
        self.stop_performance_monitoring()
        
        self.is_powered_on = False
        print("✅ Virtual machine powered off")
    
    def start_performance_monitoring(self):
        """Start performance monitoring thread"""
        if self.monitoring_active:
            return
        
        self.monitoring_active = True
        self.monitor_thread = threading.Thread(target=self._monitor_performance, daemon=True)
        self.monitor_thread.start()
        print("📊 Performance monitoring started")
    
    def stop_performance_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=1)
        print("📊 Performance monitoring stopped")
    
    def _monitor_performance(self):
        """Monitor system performance"""
        while self.monitoring_active and self.is_powered_on:
            try:
                # Simulate realistic usage patterns
                self._simulate_cpu_usage()
                self._simulate_memory_usage()
                self._simulate_network_activity()
                self._simulate_disk_activity()
                
                # Record performance data
                performance_data = {
                    'timestamp': datetime.now().isoformat(),
                    'cpu_usage': self.cpu_usage,
                    'memory_usage': self.memory_usage,
                    'network_rx': self.network_rx_bytes,
                    'network_tx': self.network_tx_bytes,
                    'disk_read': self.disk_read_bytes,
                    'disk_write': self.disk_write_bytes
                }
                
                self.performance_history.append(performance_data)
                
                # Keep only last 100 records
                if len(self.performance_history) > 100:
                    self.performance_history.pop(0)
                
                time.sleep(5)  # Monitor every 5 seconds
                
            except Exception as e:
                print(f"❌ Performance monitoring error: {e}")
                break
    
    def _simulate_cpu_usage(self):
        """Simulate realistic CPU usage"""
        # Base usage + random fluctuation
        base_usage = 5 + random.uniform(0, 10)
        
        # Simulate CPU spikes during operations
        if random.random() < 0.1:  # 10% chance of spike
            base_usage += random.uniform(20, 60)
        
        self.cpu_usage = min(100.0, max(0.0, base_usage))
    
    def _simulate_memory_usage(self):
        """Simulate realistic memory usage"""
        # Memory usage typically grows over time then gets garbage collected
        current_time = time.time()
        
        # Base memory usage (OS + applications)
        base_memory = 30 + (current_time % 300) / 300 * 20  # Cycles every 5 minutes
        
        # Add random usage
        base_memory += random.uniform(0, 15)
        
        self.memory_usage = min(95.0, max(20.0, base_memory))
    
    def _simulate_network_activity(self):
        """Simulate network activity"""
        # Random network activity
        if random.random() < 0.3:  # 30% chance of network activity
            rx_bytes = random.randint(1024, 1024*1024)  # 1KB to 1MB
            tx_bytes = random.randint(512, 512*1024)    # 512B to 512KB
            
            self.network_rx_bytes += rx_bytes
            self.network_tx_bytes += tx_bytes
    
    def _simulate_disk_activity(self):
        """Simulate disk I/O activity"""
        # Random disk activity
        if random.random() < 0.4:  # 40% chance of disk activity
            read_bytes = random.randint(4096, 1024*1024)   # 4KB to 1MB
            write_bytes = random.randint(4096, 512*1024)   # 4KB to 512KB
            
            self.disk_read_bytes += read_bytes
            self.disk_write_bytes += write_bytes
    
    def get_hardware_info(self) -> Dict:
        """Get detailed hardware information"""
        uptime = datetime.now() - self.boot_time if self.is_powered_on else timedelta(0)
        
        return {
            'node_id': self.node_id,
            'power_state': 'ON' if self.is_powered_on else 'OFF',
            'boot_time': self.boot_time.isoformat(),
            'uptime_seconds': int(uptime.total_seconds()),
            'cpu': {
                'model': self.cpu_model,
                'cores': self.cpu_cores,
                'current_usage': self.cpu_usage,
                'architecture': 'x64'
            },
            'memory': {
                'total_gb': self.memory_gb,
                'type': self.memory_type,
                'current_usage': self.memory_usage,
                'speed': '3200 MHz'
            },
            'storage': {
                'total_gb': self.storage_gb,
                'type': self.storage_type,
                'interface': 'NVMe PCIe 4.0'
            },
            'network': {
                'adapter': self.network_adapter,
                'rx_bytes': self.network_rx_bytes,
                'tx_bytes': self.network_tx_bytes,
                'speed': '1000 Mbps'
            },
            'disk_io': {
                'read_bytes': self.disk_read_bytes,
                'write_bytes': self.disk_write_bytes
            }
        }
    
    def get_performance_stats(self) -> Dict:
        """Get current performance statistics"""
        if not self.is_powered_on:
            return {'status': 'powered_off'}
        
        # Calculate averages from recent history
        recent_history = self.performance_history[-20:]  # Last 20 readings
        
        if recent_history:
            avg_cpu = sum(p['cpu_usage'] for p in recent_history) / len(recent_history)
            avg_memory = sum(p['memory_usage'] for p in recent_history) / len(recent_history)
        else:
            avg_cpu = self.cpu_usage
            avg_memory = self.memory_usage
        
        return {
            'status': 'running',
            'current': {
                'cpu_usage': round(self.cpu_usage, 1),
                'memory_usage': round(self.memory_usage, 1),
                'network_rx_mb': round(self.network_rx_bytes / (1024*1024), 2),
                'network_tx_mb': round(self.network_tx_bytes / (1024*1024), 2),
                'disk_read_mb': round(self.disk_read_bytes / (1024*1024), 2),
                'disk_write_mb': round(self.disk_write_bytes / (1024*1024), 2)
            },
            'average': {
                'cpu_usage': round(avg_cpu, 1),
                'memory_usage': round(avg_memory, 1)
            },
            'history_points': len(self.performance_history)
        }
    
    def simulate_load(self, duration_seconds: int = 10, load_type: str = "cpu"):
        """Simulate high load on specific component"""
        if not self.is_powered_on:
            print("❌ Cannot simulate load: Virtual machine is powered off")
            return
        
        print(f"🔥 Simulating {load_type} load for {duration_seconds} seconds...")
        
        def load_simulation():
            start_time = time.time()
            
            while time.time() - start_time < duration_seconds:
                if load_type == "cpu":
                    self.cpu_usage = min(100.0, self.cpu_usage + random.uniform(20, 40))
                elif load_type == "memory":
                    self.memory_usage = min(95.0, self.memory_usage + random.uniform(10, 30))
                elif load_type == "network":
                    self.network_rx_bytes += random.randint(1024*1024, 10*1024*1024)
                    self.network_tx_bytes += random.randint(512*1024, 5*1024*1024)
                elif load_type == "disk":
                    self.disk_read_bytes += random.randint(1024*1024, 50*1024*1024)
                    self.disk_write_bytes += random.randint(1024*1024, 25*1024*1024)
                
                time.sleep(0.5)
            
            print(f"✅ {load_type.upper()} load simulation completed")
        
        load_thread = threading.Thread(target=load_simulation, daemon=True)
        load_thread.start()
    
    def get_system_logs(self) -> List[Dict]:
        """Get system event logs"""
        logs = []
        
        # Boot log
        logs.append({
            'timestamp': self.boot_time.isoformat(),
            'level': 'INFO',
            'source': 'SYSTEM',
            'message': f'Virtual machine {self.node_id} powered on'
        })
        
        # Performance logs
        if self.performance_history:
            latest = self.performance_history[-1]
            
            if latest['cpu_usage'] > 80:
                logs.append({
                    'timestamp': latest['timestamp'],
                    'level': 'WARNING',
                    'source': 'CPU',
                    'message': f'High CPU usage: {latest["cpu_usage"]:.1f}%'
                })
            
            if latest['memory_usage'] > 85:
                logs.append({
                    'timestamp': latest['timestamp'],
                    'level': 'WARNING',
                    'source': 'MEMORY',
                    'message': f'High memory usage: {latest["memory_usage"]:.1f}%'
                })
        
        # Network logs
        total_network_mb = (self.network_rx_bytes + self.network_tx_bytes) / (1024*1024)
        if total_network_mb > 100:  # More than 100MB transferred
            logs.append({
                'timestamp': datetime.now().isoformat(),
                'level': 'INFO',
                'source': 'NETWORK',
                'message': f'High network activity: {total_network_mb:.1f}MB transferred'
            })
        
        return sorted(logs, key=lambda x: x['timestamp'], reverse=True)[:50]  # Last 50 logs
    
    def reset_hardware(self):
        """Reset hardware statistics"""
        print("🔄 Resetting hardware statistics...")
        
        self.cpu_usage = 0.0
        self.memory_usage = 0.0
        self.network_rx_bytes = 0
        self.network_tx_bytes = 0
        self.disk_read_bytes = 0
        self.disk_write_bytes = 0
        self.performance_history = []
        
        print("✅ Hardware statistics reset")