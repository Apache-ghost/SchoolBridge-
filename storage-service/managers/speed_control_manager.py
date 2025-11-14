"""
SpeedControlManager - OOP Class for Speed Control Operations
Handles bandwidth management, speed testing, and performance analytics
"""

import time
import random
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class SpeedPreset:
    """Represents a speed preset configuration"""
    name: str
    speed_mbps: int
    description: str
    color: str


@dataclass
class SpeedTestResult:
    """Represents results from a speed test"""
    timestamp: float
    source_node: str
    target_node: str
    advertised_speed: int
    actual_speed: float
    latency_ms: float
    packet_loss: float
    test_duration: float


class SpeedControlManager:
    """
    Manages network speed control, testing, and performance analytics
    Provides clean interface for bandwidth management operations
    """
    
    def __init__(self, network, silent_mode: bool = False):
        """Initialize speed control manager with network context"""
        self.network = network
        self.silent_mode = silent_mode
        self.speed_test_history: List[SpeedTestResult] = []
        self.current_speed = 1000  # Default 1 Gbps
        
        # Define speed presets
        self.speed_presets = {
            "dialup": SpeedPreset("Dial-up", 4, "56k modem equivalent", "🐌"),
            "dsl": SpeedPreset("DSL", 8, "Basic DSL connection", "🏠"),
            "cable": SpeedPreset("Cable", 16, "Cable internet", "📡"),
            "fiber_basic": SpeedPreset("Fiber Basic", 32, "Basic fiber optic", "💫"),
            "fiber_fast": SpeedPreset("Fiber Fast", 64, "Fast fiber connection", "⚡"),
            "gigabit": SpeedPreset("Gigabit", 100, "Gigabit ethernet", "🚀"),
            "enterprise": SpeedPreset("Enterprise", 200, "Enterprise grade", "🏢"),
            "datacenter": SpeedPreset("Data Center", 400, "Data center speeds", "🏭"),
            "superfast": SpeedPreset("Super Fast", 800, "Ultra-high speed", "⚡⚡"),
            "ludicrous": SpeedPreset("Ludicrous", 1600, "Ludicrous speed", "🌟")
        }
    
    def change_speed_interactive(self):
        """Interactive speed change interface"""
        print("\n⚡ Change Network Speed:")
        
        # Show current speed
        print(f"Current Speed: {self.current_speed} Mbps")
        
        # Show presets
        print("\n📋 Speed Presets:")
        preset_list = list(self.speed_presets.items())
        for i, (key, preset) in enumerate(preset_list, 1):
            print(f"   {i:2d}. {preset.color} {preset.name}: {preset.speed_mbps} Mbps - {preset.description}")
        
        print(f"   {len(preset_list)+1:2d}. 🎛️ Custom Speed")
        
        try:
            choice = int(input("\n👉 Select speed option: "))
            
            if 1 <= choice <= len(preset_list):
                # Use preset
                key, preset = preset_list[choice - 1]
                new_speed = preset.speed_mbps
                print(f"\n{preset.color} Setting speed to {preset.name}: {new_speed} Mbps")
                
            elif choice == len(preset_list) + 1:
                # Custom speed
                new_speed = int(input("Enter custom speed (Mbps): "))
                print(f"\n🎛️ Setting custom speed: {new_speed} Mbps")
                
            else:
                print("❌ Invalid selection")
                return
                
        except ValueError:
            print("❌ Please enter a valid number")
            return
        
        # Apply speed change with visual feedback
        success = self._apply_speed_change(new_speed)
        
        if success:
            print(f"✅ Network speed changed to {new_speed} Mbps")
            self.current_speed = new_speed
            
            # Show immediate impact
            self._show_speed_impact(new_speed)
        else:
            print("❌ Failed to change network speed")
    
    def run_speed_test_interactive(self):
        """Run interactive speed test between nodes"""
        print("\n🚀 Network Speed Test:")
        
        nodes = list(self.network.nodes.values())
        if len(nodes) < 2:
            print("❌ Need at least 2 nodes for speed test")
            return
        
        # Select source node
        print("\nSelect source node:")
        for i, node in enumerate(nodes, 1):
            print(f"   {i}. {node.node_id} ({node.ip_config.ip_address})")
        
        try:
            source_idx = int(input("Source node: ")) - 1
            source_node = nodes[source_idx]
        except (ValueError, IndexError):
            print("❌ Invalid source node selection")
            return
        
        # Select target node
        available_targets = [node for node in nodes if node != source_node]
        print("\nSelect target node:")
        for i, node in enumerate(available_targets, 1):
            print(f"   {i}. {node.node_id} ({node.ip_config.ip_address})")
        
        try:
            target_idx = int(input("Target node: ")) - 1
            target_node = available_targets[target_idx]
        except (ValueError, IndexError):
            print("❌ Invalid target node selection")
            return
        
        # Run speed test
        result = self._perform_speed_test(source_node, target_node)
        
        if result:
            self._display_speed_test_result(result)
            self.speed_test_history.append(result)
        else:
            print("❌ Speed test failed")
    
    def show_speed_presets(self):
        """Display all available speed presets"""
        print("\n📋 Available Speed Presets:")
        print("=" * 60)
        
        for key, preset in self.speed_presets.items():
            print(f"{preset.color} {preset.name:<15} {preset.speed_mbps:>4} Mbps - {preset.description}")
        
        print("=" * 60)
        print(f"Current Speed: {self.current_speed} Mbps")
    
    def custom_speed_config(self):
        """Custom speed configuration interface"""
        print("\n🎛️ Custom Speed Configuration:")
        
        try:
            # Get custom parameters
            speed = int(input("Enter speed (Mbps): "))
            latency = float(input("Enter latency (ms, default 5.0): ") or "5.0")
            jitter = float(input("Enter jitter (ms, default 1.0): ") or "1.0")
            packet_loss = float(input("Enter packet loss (%, default 0.1): ") or "0.1")
            
            print(f"\n⚙️ Configuring custom network profile:")
            print(f"   Speed: {speed} Mbps")
            print(f"   Latency: {latency} ms")
            print(f"   Jitter: {jitter} ms")
            print(f"   Packet Loss: {packet_loss}%")
            
            # Apply configuration
            success = self._apply_custom_config(speed, latency, jitter, packet_loss)
            
            if success:
                print("✅ Custom configuration applied successfully")
                self.current_speed = speed
            else:
                print("❌ Failed to apply custom configuration")
                
        except ValueError:
            print("❌ Invalid input. Please enter valid numbers.")
    
    def bandwidth_analytics(self):
        """Show bandwidth usage analytics"""
        print("\n📊 Bandwidth Analytics:")
        
        if not self.speed_test_history:
            print("❌ No speed test data available")
            return
        
        # Calculate statistics
        recent_tests = self.speed_test_history[-10:]  # Last 10 tests
        avg_speed = sum(test.actual_speed for test in recent_tests) / len(recent_tests)
        max_speed = max(test.actual_speed for test in recent_tests)
        min_speed = min(test.actual_speed for test in recent_tests)
        avg_latency = sum(test.latency_ms for test in recent_tests) / len(recent_tests)
        
        print(f"   Recent Tests: {len(recent_tests)}")
        print(f"   Average Speed: {avg_speed:.2f} Mbps")
        print(f"   Maximum Speed: {max_speed:.2f} Mbps")
        print(f"   Minimum Speed: {min_speed:.2f} Mbps")
        print(f"   Average Latency: {avg_latency:.2f} ms")
        print(f"   Speed Efficiency: {(avg_speed/self.current_speed)*100:.1f}%")
        
        # Show recent test history
        print("\n🕒 Recent Speed Tests:")
        for i, test in enumerate(recent_tests[-5:], 1):
            timestamp = time.strftime('%H:%M:%S', time.localtime(test.timestamp))
            print(f"   {i}. {timestamp} | {test.source_node} → {test.target_node} | "
                  f"{test.actual_speed:.1f} Mbps ({test.latency_ms:.1f}ms)")
    
    def performance_report(self):
        """Generate comprehensive performance report"""
        print("\n📋 Network Performance Report:")
        print("=" * 60)
        
        # Current configuration
        print(f"Current Configuration:")
        print(f"   Network Speed: {self.current_speed} Mbps")
        print(f"   Active Nodes: {len(self.network.nodes)}")
        print(f"   Network Links: {len(self.network.links)}")
        
        # Performance metrics
        if self.speed_test_history:
            all_tests = self.speed_test_history
            total_tests = len(all_tests)
            
            print(f"\nPerformance Metrics:")
            print(f"   Total Speed Tests: {total_tests}")
            
            if total_tests > 0:
                overall_avg = sum(test.actual_speed for test in all_tests) / total_tests
                overall_latency = sum(test.latency_ms for test in all_tests) / total_tests
                
                print(f"   Overall Average Speed: {overall_avg:.2f} Mbps")
                print(f"   Overall Average Latency: {overall_latency:.2f} ms")
                print(f"   Network Efficiency: {(overall_avg/self.current_speed)*100:.1f}%")
        
        # Network topology impact
        print(f"\nNetwork Topology: {self.network.topology.value}")
        print(f"Topology Impact: {'High efficiency' if len(self.network.nodes) <= 5 else 'May impact performance'}")
        
        print("=" * 60)
        print("✅ Performance report generated")
    
    def network_traffic_analysis(self):
        """Analyze network traffic patterns"""
        print("\n🚦 Network Traffic Analysis:")
        
        # Simulate traffic analysis
        nodes = list(self.network.nodes.values())
        
        print(f"   Active Connections: {sum(len(node.tcp_connections) for node in nodes)}")
        print(f"   Peak Traffic Time: {random.choice(['Morning', 'Afternoon', 'Evening'])}")
        print(f"   Traffic Distribution: {'Balanced' if len(nodes) > 2 else 'Concentrated'}")
        
        # Show per-node traffic
        print("\n📊 Per-Node Traffic:")
        for node in nodes:
            connections = len(node.tcp_connections)
            files = len(node.files)
            traffic_level = "High" if connections > 3 else "Medium" if connections > 1 else "Low"
            
            print(f"   {node.node_id}: {traffic_level} ({connections} connections, {files} files)")
    
    def _apply_speed_change(self, new_speed: int) -> bool:
        """Apply speed change to network with visual feedback"""
        print(f"\n🔄 Applying speed change to {new_speed} Mbps...")
        
        # Simulate speed change process
        steps = ["Configuring network interfaces", "Updating routing tables", 
                "Adjusting bandwidth limits", "Synchronizing nodes", "Verifying changes"]
        
        for i, step in enumerate(steps, 1):
            print(f"   [{i}/{len(steps)}] {step}...")
            time.sleep(0.3)  # Brief pause for realism
        
        # Update network speed (simplified)
        for link_id, link_info in self.network.links.items():
            link_info['bandwidth'] = new_speed
        
        return True
    
    def _show_speed_impact(self, speed_mbps: int):
        """Show immediate impact of speed change"""
        print(f"\n📊 Speed Change Impact:")
        
        # Calculate transfer times for different file sizes
        file_sizes = [1, 10, 100, 1000]  # MB
        
        print("   File Transfer Time Estimates:")
        for size in file_sizes:
            transfer_time = (size * 8) / speed_mbps  # Convert MB to Mb, divide by Mbps
            
            if transfer_time < 1:
                time_str = f"{transfer_time * 1000:.0f}ms"
            elif transfer_time < 60:
                time_str = f"{transfer_time:.1f}s"
            else:
                minutes = transfer_time / 60
                time_str = f"{minutes:.1f}min"
            
            print(f"      {size:>4} MB file: {time_str}")
    
    def _perform_speed_test(self, source_node, target_node) -> Optional[SpeedTestResult]:
        """Perform actual speed test between nodes"""
        print(f"\n🚀 Running speed test: {source_node.node_id} → {target_node.node_id}")
        
        # Simulate speed test process
        test_steps = [
            "Establishing connection",
            "Measuring latency", 
            "Testing upload speed",
            "Testing download speed",
            "Analyzing results"
        ]
        
        for step in test_steps:
            print(f"   {step}...", end="", flush=True)
            time.sleep(0.5)
            print(" ✓")
        
        # Generate realistic test results
        advertised_speed = self.current_speed
        
        # Simulate network conditions affecting actual speed
        efficiency = random.uniform(0.7, 0.95)  # 70-95% efficiency
        actual_speed = advertised_speed * efficiency
        
        # Simulate latency (lower for higher speeds, with some randomness)
        base_latency = max(1, 20 - (advertised_speed / 100))  # Better hardware = lower latency
        latency_ms = base_latency + random.uniform(-2, 5)
        
        # Simulate packet loss (very low for good connections)
        packet_loss = random.uniform(0, 0.5)  # 0-0.5% loss
        
        return SpeedTestResult(
            timestamp=time.time(),
            source_node=source_node.node_id,
            target_node=target_node.node_id,
            advertised_speed=advertised_speed,
            actual_speed=actual_speed,
            latency_ms=latency_ms,
            packet_loss=packet_loss,
            test_duration=2.5
        )
    
    def _display_speed_test_result(self, result: SpeedTestResult):
        """Display speed test results in a formatted way"""
        print(f"\n📊 Speed Test Results:")
        print("=" * 50)
        print(f"   Route: {result.source_node} → {result.target_node}")
        print(f"   Advertised Speed: {result.advertised_speed} Mbps")
        print(f"   Actual Speed: {result.actual_speed:.2f} Mbps")
        print(f"   Speed Efficiency: {(result.actual_speed/result.advertised_speed)*100:.1f}%")
        print(f"   Latency: {result.latency_ms:.2f} ms")
        print(f"   Packet Loss: {result.packet_loss:.3f}%")
        print(f"   Test Duration: {result.test_duration:.1f} seconds")
        
        # Performance rating
        efficiency = (result.actual_speed / result.advertised_speed) * 100
        if efficiency >= 90:
            rating = "🌟 Excellent"
        elif efficiency >= 80:
            rating = "✅ Good"
        elif efficiency >= 70:
            rating = "⚠️ Fair"
        else:
            rating = "❌ Poor"
        
        print(f"   Performance Rating: {rating}")
        print("=" * 50)
    
    def _apply_custom_config(self, speed: int, latency: float, jitter: float, packet_loss: float) -> bool:
        """Apply custom network configuration"""
        try:
            # Update network parameters
            for link_id, link_info in self.network.links.items():
                link_info['bandwidth'] = speed
                link_info['latency'] = latency
                link_info['jitter'] = jitter
                link_info['packet_loss'] = packet_loss
            
            print("\n⚙️ Applying configuration...")
            time.sleep(1)  # Simulate configuration time
            
            return True
            
        except Exception as e:
            print(f"❌ Configuration failed: {str(e)}")
            return False