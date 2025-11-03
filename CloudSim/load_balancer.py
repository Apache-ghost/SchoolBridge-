"""
SchoolBridge Load Balancer and Multi-Region System
Implements load balancing and regional failover mechanisms for high availability
"""
import time
import random
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Tuple
from enum import Enum, auto
from collections import defaultdict, deque
import statistics

class LoadBalancingAlgorithm(Enum):
    ROUND_ROBIN = auto()
    WEIGHTED_ROUND_ROBIN = auto()
    LEAST_CONNECTIONS = auto()
    LEAST_RESPONSE_TIME = auto()
    HEALTH_BASED = auto()

class RegionStatus(Enum):
    ACTIVE = auto()
    DEGRADED = auto()
    FAILED = auto()
    RECOVERING = auto()

class NodeHealth(Enum):
    HEALTHY = auto()
    WARNING = auto()
    CRITICAL = auto()
    FAILED = auto()

@dataclass
class HealthMetrics:
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    storage_usage: float = 0.0
    network_latency_ms: float = 0.0
    active_connections: int = 0
    requests_per_second: float = 0.0
    error_rate: float = 0.0
    last_updated: float = field(default_factory=time.time)

@dataclass
class NodeInfo:
    node_id: str
    region: str
    weight: int = 1
    max_connections: int = 1000
    current_connections: int = 0
    health_status: NodeHealth = NodeHealth.HEALTHY
    health_metrics: HealthMetrics = field(default_factory=HealthMetrics)
    last_request_time: float = field(default_factory=time.time)
    response_times: deque = field(default_factory=lambda: deque(maxlen=100))
    total_requests: int = 0
    failed_requests: int = 0
    is_available: bool = True

@dataclass
class Region:
    region_id: str
    name: str
    location: str
    status: RegionStatus = RegionStatus.ACTIVE
    nodes: Dict[str, NodeInfo] = field(default_factory=dict)
    max_capacity: int = 10000
    current_load: int = 0
    priority: int = 1  # Higher number = higher priority
    latency_to_regions: Dict[str, float] = field(default_factory=dict)

class LoadBalancer:
    """
    Load Balancer for distributing requests across multiple nodes
    """
    
    def __init__(self, balancer_id: str, algorithm: LoadBalancingAlgorithm = LoadBalancingAlgorithm.LEAST_CONNECTIONS):
        self.balancer_id = balancer_id
        self.algorithm = algorithm
        
        # Node management
        self.nodes: Dict[str, NodeInfo] = {}
        self.healthy_nodes: List[str] = []
        self.failed_nodes: Set[str] = set()
        
        # Algorithm-specific state
        self.round_robin_index = 0
        self.weighted_round_robin_state: Dict[str, int] = {}
        
        # Performance tracking
        self.total_requests = 0
        self.successful_requests = 0
        self.failed_requests = 0
        self.average_response_time = 0.0
        
        # Health checking
        self.health_check_interval = 30  # seconds
        self.last_health_check = time.time()
    
    def add_node(self, node: NodeInfo) -> bool:
        """Add a node to the load balancer"""
        try:
            self.nodes[node.node_id] = node
            if node.is_available and node.health_status != NodeHealth.FAILED:
                self.healthy_nodes.append(node.node_id)
            
            # Initialize weighted round robin state
            self.weighted_round_robin_state[node.node_id] = node.weight
            
            print(f"Added node {node.node_id} to load balancer {self.balancer_id}")
            return True
            
        except Exception as e:
            print(f"Error adding node {node.node_id}: {e}")
            return False
    
    def remove_node(self, node_id: str) -> bool:
        """Remove a node from the load balancer"""
        try:
            if node_id in self.nodes:
                del self.nodes[node_id]
                
                if node_id in self.healthy_nodes:
                    self.healthy_nodes.remove(node_id)
                
                self.failed_nodes.discard(node_id)
                
                if node_id in self.weighted_round_robin_state:
                    del self.weighted_round_robin_state[node_id]
                
                print(f"Removed node {node_id} from load balancer {self.balancer_id}")
                return True
            
        except Exception as e:
            print(f"Error removing node {node_id}: {e}")
            return False
    
    def get_next_node(self, request_metadata: Dict = None) -> Optional[str]:
        """Get the next node to handle a request based on load balancing algorithm"""
        if not self.healthy_nodes:
            return None
        
        if self.algorithm == LoadBalancingAlgorithm.ROUND_ROBIN:
            return self._round_robin()
        elif self.algorithm == LoadBalancingAlgorithm.WEIGHTED_ROUND_ROBIN:
            return self._weighted_round_robin()
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._least_connections()
        elif self.algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            return self._least_response_time()
        elif self.algorithm == LoadBalancingAlgorithm.HEALTH_BASED:
            return self._health_based()
        
        return self._round_robin()  # Default fallback
    
    def record_request_start(self, node_id: str) -> bool:
        """Record the start of a request to a node"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.current_connections += 1
            node.total_requests += 1
            node.last_request_time = time.time()
            self.total_requests += 1
            return True
        return False
    
    def record_request_completion(self, node_id: str, response_time_ms: float, success: bool = True) -> bool:
        """Record the completion of a request"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.current_connections = max(0, node.current_connections - 1)
            node.response_times.append(response_time_ms)
            
            if success:
                self.successful_requests += 1
            else:
                node.failed_requests += 1
                self.failed_requests += 1
            
            # Update average response time
            all_response_times = []
            for n in self.nodes.values():
                all_response_times.extend(list(n.response_times))
            
            if all_response_times:
                self.average_response_time = statistics.mean(all_response_times)
            
            return True
        return False
    
    def update_node_health(self, node_id: str, health_metrics: HealthMetrics) -> bool:
        """Update health metrics for a node"""
        if node_id in self.nodes:
            node = self.nodes[node_id]
            node.health_metrics = health_metrics
            
            # Determine health status based on metrics
            old_status = node.health_status
            new_status = self._calculate_health_status(health_metrics)
            node.health_status = new_status
            
            # Update availability based on health
            if new_status == NodeHealth.FAILED:
                node.is_available = False
                if node_id in self.healthy_nodes:
                    self.healthy_nodes.remove(node_id)
                self.failed_nodes.add(node_id)
            elif new_status in [NodeHealth.HEALTHY, NodeHealth.WARNING] and not node.is_available:
                node.is_available = True
                if node_id not in self.healthy_nodes:
                    self.healthy_nodes.append(node_id)
                self.failed_nodes.discard(node_id)
            
            if old_status != new_status:
                print(f"Node {node_id} health status changed: {old_status.name} -> {new_status.name}")
            
            return True
        return False
    
    def perform_health_checks(self) -> Dict[str, Any]:
        """Perform health checks on all nodes"""
        current_time = time.time()
        if current_time - self.last_health_check < self.health_check_interval:
            return {}
        
        health_results = {
            "healthy": 0,
            "warning": 0,
            "critical": 0,
            "failed": 0,
            "checked_nodes": []
        }
        
        for node_id, node in self.nodes.items():
            # Simulate health check
            simulated_metrics = self._simulate_health_check(node_id)
            self.update_node_health(node_id, simulated_metrics)
            
            health_results[node.health_status.name.lower()] += 1
            health_results["checked_nodes"].append({
                "node_id": node_id,
                "status": node.health_status.name,
                "metrics": {
                    "cpu_usage": simulated_metrics.cpu_usage,
                    "memory_usage": simulated_metrics.memory_usage,
                    "active_connections": node.current_connections,
                    "error_rate": node.failed_requests / max(node.total_requests, 1)
                }
            })
        
        self.last_health_check = current_time
        return health_results
    
    def _round_robin(self) -> Optional[str]:
        """Round robin load balancing"""
        if not self.healthy_nodes:
            return None
        
        node_id = self.healthy_nodes[self.round_robin_index]
        self.round_robin_index = (self.round_robin_index + 1) % len(self.healthy_nodes)
        return node_id
    
    def _weighted_round_robin(self) -> Optional[str]:
        """Weighted round robin load balancing"""
        if not self.healthy_nodes:
            return None
        
        # Find node with highest remaining weight
        best_node = None
        highest_weight = -1
        
        for node_id in self.healthy_nodes:
            current_weight = self.weighted_round_robin_state.get(node_id, 0)
            if current_weight > highest_weight:
                highest_weight = current_weight
                best_node = node_id
        
        if best_node:
            # Decrease weight for selected node
            self.weighted_round_robin_state[best_node] -= 1
            
            # Reset weights if all are zero
            if all(w <= 0 for w in self.weighted_round_robin_state.values()):
                for node_id in self.healthy_nodes:
                    if node_id in self.nodes:
                        self.weighted_round_robin_state[node_id] = self.nodes[node_id].weight
        
        return best_node
    
    def _least_connections(self) -> Optional[str]:
        """Least connections load balancing"""
        if not self.healthy_nodes:
            return None
        
        min_connections = float('inf')
        best_node = None
        
        for node_id in self.healthy_nodes:
            node = self.nodes[node_id]
            if node.current_connections < min_connections:
                min_connections = node.current_connections
                best_node = node_id
        
        return best_node
    
    def _least_response_time(self) -> Optional[str]:
        """Least response time load balancing"""
        if not self.healthy_nodes:
            return None
        
        min_response_time = float('inf')
        best_node = None
        
        for node_id in self.healthy_nodes:
            node = self.nodes[node_id]
            if node.response_times:
                avg_response_time = statistics.mean(node.response_times)
                if avg_response_time < min_response_time:
                    min_response_time = avg_response_time
                    best_node = node_id
            else:
                # Prefer nodes with no recorded response times (new nodes)
                best_node = node_id
                break
        
        return best_node
    
    def _health_based(self) -> Optional[str]:
        """Health-based load balancing"""
        if not self.healthy_nodes:
            return None
        
        # Score nodes based on health metrics
        best_score = -1
        best_node = None
        
        for node_id in self.healthy_nodes:
            node = self.nodes[node_id]
            score = self._calculate_health_score(node)
            
            if score > best_score:
                best_score = score
                best_node = node_id
        
        return best_node
    
    def _calculate_health_status(self, metrics: HealthMetrics) -> NodeHealth:
        """Calculate health status based on metrics"""
        critical_conditions = 0
        warning_conditions = 0
        
        # Check CPU usage
        if metrics.cpu_usage > 90:
            critical_conditions += 1
        elif metrics.cpu_usage > 80:
            warning_conditions += 1
        
        # Check memory usage
        if metrics.memory_usage > 90:
            critical_conditions += 1
        elif metrics.memory_usage > 80:
            warning_conditions += 1
        
        # Check error rate
        if metrics.error_rate > 0.1:  # 10% error rate
            critical_conditions += 1
        elif metrics.error_rate > 0.05:  # 5% error rate
            warning_conditions += 1
        
        # Check network latency
        if metrics.network_latency_ms > 1000:  # 1 second
            critical_conditions += 1
        elif metrics.network_latency_ms > 500:  # 500ms
            warning_conditions += 1
        
        # Determine overall status
        if critical_conditions >= 2:
            return NodeHealth.FAILED
        elif critical_conditions >= 1:
            return NodeHealth.CRITICAL
        elif warning_conditions >= 2:
            return NodeHealth.WARNING
        else:
            return NodeHealth.HEALTHY
    
    def _calculate_health_score(self, node: NodeInfo) -> float:
        """Calculate a health score for load balancing (higher = better)"""
        metrics = node.health_metrics
        
        # Base score starts at 100
        score = 100.0
        
        # Subtract points for high resource usage
        score -= metrics.cpu_usage * 0.5
        score -= metrics.memory_usage * 0.3
        score -= metrics.storage_usage * 0.2
        
        # Subtract points for high latency
        score -= min(metrics.network_latency_ms / 10, 50)
        
        # Subtract points for high error rate
        score -= metrics.error_rate * 100
        
        # Subtract points for high connection count
        connection_ratio = node.current_connections / node.max_connections
        score -= connection_ratio * 30
        
        return max(score, 0)  # Ensure non-negative score
    
    def _simulate_health_check(self, node_id: str) -> HealthMetrics:
        """Simulate health check for a node"""
        # Generate realistic but random health metrics
        return HealthMetrics(
            cpu_usage=random.uniform(10, 95),
            memory_usage=random.uniform(20, 90),
            storage_usage=random.uniform(30, 85),
            network_latency_ms=random.uniform(5, 200),
            active_connections=self.nodes[node_id].current_connections,
            requests_per_second=random.uniform(1, 100),
            error_rate=random.uniform(0, 0.15),
            last_updated=time.time()
        )
    
    def get_balancer_statistics(self) -> Dict[str, Any]:
        """Get comprehensive load balancer statistics"""
        success_rate = (self.successful_requests / max(self.total_requests, 1)) * 100
        
        node_stats = {}
        for node_id, node in self.nodes.items():
            node_stats[node_id] = {
                "status": node.health_status.name,
                "current_connections": node.current_connections,
                "total_requests": node.total_requests,
                "failed_requests": node.failed_requests,
                "average_response_time": statistics.mean(node.response_times) if node.response_times else 0,
                "is_available": node.is_available
            }
        
        return {
            "balancer_id": self.balancer_id,
            "algorithm": self.algorithm.name,
            "total_nodes": len(self.nodes),
            "healthy_nodes": len(self.healthy_nodes),
            "failed_nodes": len(self.failed_nodes),
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate_percent": round(success_rate, 2),
            "average_response_time_ms": round(self.average_response_time, 2),
            "node_statistics": node_stats
        }

class MultiRegionManager:
    """
    Multi-Region Manager for SchoolBridge
    Handles regional failover and global load distribution
    """
    
    def __init__(self, system_id: str):
        self.system_id = system_id
        
        # Region management
        self.regions: Dict[str, Region] = {}
        self.active_regions: List[str] = []
        self.failed_regions: Set[str] = set()
        
        # Load balancers per region
        self.regional_load_balancers: Dict[str, LoadBalancer] = {}
        
        # Global routing
        self.global_routing_algorithm = LoadBalancingAlgorithm.LEAST_RESPONSE_TIME
        self.region_preferences: Dict[str, List[str]] = {}  # client_region -> preferred_regions
        
        # Failover configuration
        self.failover_enabled = True
        self.automatic_recovery = True
        self.failover_threshold_seconds = 30
        
        # Performance tracking
        self.cross_region_requests = 0
        self.failover_events = 0
        
    def add_region(self, region: Region) -> bool:
        """Add a new region to the multi-region system"""
        try:
            self.regions[region.region_id] = region
            
            if region.status == RegionStatus.ACTIVE:
                self.active_regions.append(region.region_id)
            
            # Create regional load balancer
            regional_lb = LoadBalancer(
                f"lb-{region.region_id}",
                LoadBalancingAlgorithm.LEAST_CONNECTIONS
            )
            self.regional_load_balancers[region.region_id] = regional_lb
            
            print(f"Added region {region.region_id} ({region.name}) to multi-region system")
            return True
            
        except Exception as e:
            print(f"Error adding region {region.region_id}: {e}")
            return False
    
    def add_node_to_region(self, region_id: str, node: NodeInfo) -> bool:
        """Add a node to a specific region"""
        if region_id not in self.regions:
            return False
        
        try:
            # Add to region
            self.regions[region_id].nodes[node.node_id] = node
            
            # Add to regional load balancer
            if region_id in self.regional_load_balancers:
                self.regional_load_balancers[region_id].add_node(node)
            
            print(f"Added node {node.node_id} to region {region_id}")
            return True
            
        except Exception as e:
            print(f"Error adding node {node.node_id} to region {region_id}: {e}")
            return False
    
    def route_request(self, client_region: str, request_metadata: Dict = None) -> Tuple[Optional[str], Optional[str]]:
        """Route a request to the best region and node"""
        # Determine target region
        target_region = self._select_target_region(client_region, request_metadata)
        if not target_region:
            return None, None
        
        # Get node from regional load balancer
        if target_region in self.regional_load_balancers:
            lb = self.regional_load_balancers[target_region]
            node_id = lb.get_next_node(request_metadata)
            
            if node_id:
                # Record request routing
                if target_region != client_region:
                    self.cross_region_requests += 1
                
                return target_region, node_id
        
        # Fallback to any available region
        for region_id in self.active_regions:
            if region_id in self.regional_load_balancers:
                lb = self.regional_load_balancers[region_id]
                node_id = lb.get_next_node(request_metadata)
                if node_id:
                    self.cross_region_requests += 1
                    return region_id, node_id
        
        return None, None
    
    def handle_region_failure(self, region_id: str) -> bool:
        """Handle failure of a region"""
        if region_id not in self.regions:
            return False
        
        try:
            # Mark region as failed
            self.regions[region_id].status = RegionStatus.FAILED
            
            if region_id in self.active_regions:
                self.active_regions.remove(region_id)
            
            self.failed_regions.add(region_id)
            self.failover_events += 1
            
            print(f"Region {region_id} marked as failed. Failover initiated.")
            
            # Redistribute traffic to healthy regions
            if self.failover_enabled:
                self._redistribute_traffic_from_failed_region(region_id)
            
            return True
            
        except Exception as e:
            print(f"Error handling region failure for {region_id}: {e}")
            return False
    
    def recover_region(self, region_id: str) -> bool:
        """Recover a failed region"""
        if region_id not in self.regions:
            return False
        
        try:
            region = self.regions[region_id]
            
            # Check if region can be recovered
            if not self._can_recover_region(region):
                return False
            
            # Mark as recovering
            region.status = RegionStatus.RECOVERING
            
            # Perform health checks on regional nodes
            if region_id in self.regional_load_balancers:
                lb = self.regional_load_balancers[region_id]
                health_results = lb.perform_health_checks()
                
                # Check if enough nodes are healthy
                healthy_nodes = health_results.get("healthy", 0) + health_results.get("warning", 0)
                if healthy_nodes >= len(region.nodes) * 0.5:  # At least 50% healthy
                    region.status = RegionStatus.ACTIVE
                    self.active_regions.append(region_id)
                    self.failed_regions.discard(region_id)
                    
                    print(f"Region {region_id} successfully recovered")
                    return True
            
            return False
            
        except Exception as e:
            print(f"Error recovering region {region_id}: {e}")
            return False
    
    def monitor_regions(self) -> Dict[str, Any]:
        """Monitor all regions and perform automatic recovery if enabled"""
        monitoring_results = {
            "total_regions": len(self.regions),
            "active_regions": len(self.active_regions),
            "failed_regions": len(self.failed_regions),
            "region_status": {},
            "health_checks": {},
            "recovery_attempts": 0
        }
        
        for region_id, region in self.regions.items():
            # Perform health checks
            if region_id in self.regional_load_balancers:
                lb = self.regional_load_balancers[region_id]
                health_results = lb.perform_health_checks()
                monitoring_results["health_checks"][region_id] = health_results
                
                # Check for automatic recovery
                if (self.automatic_recovery and 
                    region.status == RegionStatus.FAILED and
                    health_results.get("healthy", 0) > 0):
                    
                    recovery_success = self.recover_region(region_id)
                    if recovery_success:
                        monitoring_results["recovery_attempts"] += 1
            
            monitoring_results["region_status"][region_id] = {
                "status": region.status.name,
                "current_load": region.current_load,
                "node_count": len(region.nodes),
                "priority": region.priority
            }
        
        return monitoring_results
    
    def _select_target_region(self, client_region: str, request_metadata: Dict = None) -> Optional[str]:
        """Select the best region to handle a request"""
        # Check if client's preferred region is available
        if client_region in self.active_regions:
            region = self.regions[client_region]
            if region.status == RegionStatus.ACTIVE and region.current_load < region.max_capacity:
                return client_region
        
        # Check region preferences
        preferred_regions = self.region_preferences.get(client_region, [])
        for preferred_region in preferred_regions:
            if preferred_region in self.active_regions:
                region = self.regions[preferred_region]
                if region.status == RegionStatus.ACTIVE and region.current_load < region.max_capacity:
                    return preferred_region
        
        # Select based on global routing algorithm
        if self.global_routing_algorithm == LoadBalancingAlgorithm.LEAST_RESPONSE_TIME:
            return self._select_lowest_latency_region(client_region)
        elif self.global_routing_algorithm == LoadBalancingAlgorithm.LEAST_CONNECTIONS:
            return self._select_least_loaded_region()
        else:
            # Default to first available region
            return self.active_regions[0] if self.active_regions else None
    
    def _select_lowest_latency_region(self, client_region: str) -> Optional[str]:
        """Select region with lowest latency to client region"""
        if not self.active_regions:
            return None
        
        best_region = None
        lowest_latency = float('inf')
        
        for region_id in self.active_regions:
            region = self.regions[region_id]
            latency = region.latency_to_regions.get(client_region, 100.0)  # Default 100ms
            
            if latency < lowest_latency:
                lowest_latency = latency
                best_region = region_id
        
        return best_region
    
    def _select_least_loaded_region(self) -> Optional[str]:
        """Select region with lowest current load"""
        if not self.active_regions:
            return None
        
        best_region = None
        lowest_load = float('inf')
        
        for region_id in self.active_regions:
            region = self.regions[region_id]
            load_ratio = region.current_load / region.max_capacity
            
            if load_ratio < lowest_load:
                lowest_load = load_ratio
                best_region = region_id
        
        return best_region
    
    def _redistribute_traffic_from_failed_region(self, failed_region_id: str):
        """Redistribute traffic from a failed region to healthy regions"""
        # In a real system, this would involve:
        # 1. Updating DNS records
        # 2. Redirecting active connections
        # 3. Migrating data if needed
        
        print(f"Redistributing traffic from failed region {failed_region_id} to healthy regions")
        
        # For simulation, we just log the action
        healthy_regions = [r for r in self.active_regions if r != failed_region_id]
        if healthy_regions:
            print(f"Traffic redirected to regions: {', '.join(healthy_regions)}")
    
    def _can_recover_region(self, region: Region) -> bool:
        """Check if a region can be recovered"""
        # Basic checks for region recovery
        return (region.status in [RegionStatus.FAILED, RegionStatus.DEGRADED] and
                len(region.nodes) > 0)
    
    def set_region_preferences(self, client_region: str, preferred_regions: List[str]):
        """Set region preferences for a client region"""
        self.region_preferences[client_region] = preferred_regions
    
    def get_system_statistics(self) -> Dict[str, Any]:
        """Get comprehensive multi-region system statistics"""
        total_nodes = sum(len(region.nodes) for region in self.regions.values())
        total_capacity = sum(region.max_capacity for region in self.regions.values())
        total_load = sum(region.current_load for region in self.regions.values())
        
        return {
            "system_id": self.system_id,
            "regions": {
                "total_regions": len(self.regions),
                "active_regions": len(self.active_regions),
                "failed_regions": len(self.failed_regions)
            },
            "capacity": {
                "total_nodes": total_nodes,
                "total_capacity": total_capacity,
                "current_load": total_load,
                "utilization_percent": (total_load / total_capacity * 100) if total_capacity > 0 else 0
            },
            "performance": {
                "cross_region_requests": self.cross_region_requests,
                "failover_events": self.failover_events
            },
            "configuration": {
                "global_routing_algorithm": self.global_routing_algorithm.name,
                "failover_enabled": self.failover_enabled,
                "automatic_recovery": self.automatic_recovery
            }
        }