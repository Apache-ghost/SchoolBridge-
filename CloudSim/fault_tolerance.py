"""
SchoolBridge Fault Tolerance System
Automatic failover, data consistency checks, and system recovery mechanisms
"""
import time
import threading
import uuid
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Any, Callable
from enum import Enum, auto
import json
import hashlib
from collections import defaultdict
import random

class FailureType(Enum):
    NODE_FAILURE = auto()
    NETWORK_PARTITION = auto()
    DATA_CORRUPTION = auto()
    SERVICE_UNAVAILABLE = auto()
    PERFORMANCE_DEGRADATION = auto()
    SECURITY_BREACH = auto()

class RecoveryAction(Enum):
    RESTART_SERVICE = auto()
    FAILOVER_TO_BACKUP = auto()
    REDISTRIBUTE_LOAD = auto()
    REPAIR_DATA = auto()
    ISOLATE_NODE = auto()
    MANUAL_INTERVENTION = auto()

class AlertLevel(Enum):
    INFO = auto()
    WARNING = auto()
    CRITICAL = auto()
    EMERGENCY = auto()

@dataclass
class FailureEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    failure_type: FailureType = FailureType.NODE_FAILURE
    affected_component: str = ""
    description: str = ""
    timestamp: float = field(default_factory=time.time)
    severity: AlertLevel = AlertLevel.WARNING
    resolved: bool = False
    resolution_time: Optional[float] = None
    recovery_actions: List[RecoveryAction] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class HealthCheck:
    check_id: str
    component_id: str
    check_function: Callable[[], bool]
    interval_seconds: int = 30
    timeout_seconds: int = 10
    failure_threshold: int = 3
    current_failures: int = 0
    last_check: float = 0
    last_success: float = field(default_factory=time.time)

@dataclass
class CircuitBreaker:
    service_id: str
    failure_threshold: int = 5
    reset_timeout_seconds: int = 60
    current_failures: int = 0
    state: str = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    last_failure_time: float = 0
    successful_calls: int = 0
    failed_calls: int = 0

class FaultToleranceSystem:
    """
    Comprehensive Fault Tolerance System for SchoolBridge
    Handles failure detection, recovery, and system resilience
    """
    
    def __init__(self, system_id: str):
        self.system_id = system_id
        self.is_running = False
        
        # Failure tracking and monitoring
        self.failure_events: Dict[str, FailureEvent] = {}
        self.health_checks: Dict[str, HealthCheck] = {}
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        
        # System components registry
        self.registered_components: Dict[str, Dict[str, Any]] = {}
        self.component_dependencies: Dict[str, List[str]] = {}
        
        # Recovery and backup systems
        self.backup_components: Dict[str, List[str]] = {}  # component_id -> backup_ids
        self.recovery_strategies: Dict[str, List[RecoveryAction]] = {}
        
        # Monitoring and alerting
        self.alert_handlers: List[Callable[[FailureEvent], None]] = []
        self.monitoring_thread: Optional[threading.Thread] = None
        self.monitoring_interval = 5  # seconds
        
        # System metrics
        self.total_failures_detected = 0
        self.successful_recoveries = 0
        self.failed_recoveries = 0
        self.system_downtime_seconds = 0.0
        self.last_failure_time = 0.0
        
        # Configuration
        self.auto_recovery_enabled = True
        self.max_concurrent_recoveries = 3
        self.active_recoveries = 0
        
    def register_component(self, component_id: str, component_type: str, 
                          health_check_func: Callable[[], bool] = None,
                          dependencies: List[str] = None,
                          backup_components: List[str] = None) -> bool:
        """Register a component for fault tolerance monitoring"""
        try:
            self.registered_components[component_id] = {
                "type": component_type,
                "registered_at": time.time(),
                "status": "active",
                "last_seen": time.time()
            }
            
            # Set up dependencies
            if dependencies:
                self.component_dependencies[component_id] = dependencies
            
            # Set up backup components
            if backup_components:
                self.backup_components[component_id] = backup_components
            
            # Set up health check
            if health_check_func:
                health_check = HealthCheck(
                    check_id=f"health-{component_id}",
                    component_id=component_id,
                    check_function=health_check_func
                )
                self.health_checks[component_id] = health_check
            
            # Set up circuit breaker
            circuit_breaker = CircuitBreaker(service_id=component_id)
            self.circuit_breakers[component_id] = circuit_breaker
            
            print(f"Registered component {component_id} for fault tolerance monitoring")
            return True
            
        except Exception as e:
            print(f"Error registering component {component_id}: {e}")
            return False
    
    def start_monitoring(self) -> bool:
        """Start the fault tolerance monitoring system"""
        try:
            if self.is_running:
                return True
            
            self.is_running = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitoring_thread.start()
            
            print(f"Fault tolerance monitoring started for system {self.system_id}")
            return True
            
        except Exception as e:
            print(f"Error starting fault tolerance monitoring: {e}")
            return False
    
    def stop_monitoring(self):
        """Stop the fault tolerance monitoring system"""
        self.is_running = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        print("Fault tolerance monitoring stopped")
    
    def report_failure(self, component_id: str, failure_type: FailureType, 
                      description: str, severity: AlertLevel = AlertLevel.WARNING,
                      metadata: Dict[str, Any] = None) -> str:
        """Report a failure event"""
        failure_event = FailureEvent(
            failure_type=failure_type,
            affected_component=component_id,
            description=description,
            severity=severity,
            metadata=metadata or {}
        )
        
        self.failure_events[failure_event.event_id] = failure_event
        self.total_failures_detected += 1
        self.last_failure_time = time.time()
        
        # Update component status
        if component_id in self.registered_components:
            self.registered_components[component_id]["status"] = "failed"
        
        # Trigger alerts
        self._trigger_alerts(failure_event)
        
        # Initiate automatic recovery if enabled
        if self.auto_recovery_enabled:
            self._initiate_recovery(failure_event)
        
        print(f"Failure reported: {failure_type.name} in {component_id} - {description}")
        return failure_event.event_id
    
    def call_service_with_circuit_breaker(self, service_id: str, 
                                        service_call: Callable[[], Any]) -> Any:
        """Call a service through a circuit breaker pattern"""
        if service_id not in self.circuit_breakers:
            # Create circuit breaker if it doesn't exist
            self.circuit_breakers[service_id] = CircuitBreaker(service_id=service_id)
        
        circuit_breaker = self.circuit_breakers[service_id]
        current_time = time.time()
        
        # Check circuit breaker state
        if circuit_breaker.state == "OPEN":
            # Check if we should try to reset
            if current_time - circuit_breaker.last_failure_time > circuit_breaker.reset_timeout_seconds:
                circuit_breaker.state = "HALF_OPEN"
                print(f"Circuit breaker for {service_id} moved to HALF_OPEN")
            else:
                raise Exception(f"Circuit breaker for {service_id} is OPEN")
        
        try:
            # Call the service
            result = service_call()
            
            # Success - update circuit breaker
            circuit_breaker.successful_calls += 1
            circuit_breaker.current_failures = 0
            
            if circuit_breaker.state == "HALF_OPEN":
                circuit_breaker.state = "CLOSED"
                print(f"Circuit breaker for {service_id} reset to CLOSED")
            
            return result
            
        except Exception as e:
            # Failure - update circuit breaker
            circuit_breaker.failed_calls += 1
            circuit_breaker.current_failures += 1
            circuit_breaker.last_failure_time = current_time
            
            # Check if we should open the circuit
            if circuit_breaker.current_failures >= circuit_breaker.failure_threshold:
                circuit_breaker.state = "OPEN"
                print(f"Circuit breaker for {service_id} opened due to failures")
            
            raise e
    
    def perform_data_consistency_check(self, component_id: str, 
                                     data_validation_func: Callable[[], bool]) -> bool:
        """Perform data consistency check for a component"""
        try:
            is_consistent = data_validation_func()
            
            if not is_consistent:
                # Report data corruption
                self.report_failure(
                    component_id=component_id,
                    failure_type=FailureType.DATA_CORRUPTION,
                    description="Data consistency check failed",
                    severity=AlertLevel.CRITICAL
                )
                return False
            
            return True
            
        except Exception as e:
            print(f"Error performing data consistency check for {component_id}: {e}")
            return False
    
    def initiate_manual_recovery(self, event_id: str, recovery_actions: List[RecoveryAction]) -> bool:
        """Initiate manual recovery for a failure event"""
        if event_id not in self.failure_events:
            return False
        
        failure_event = self.failure_events[event_id]
        failure_event.recovery_actions = recovery_actions
        
        return self._execute_recovery_actions(failure_event)
    
    def add_alert_handler(self, handler: Callable[[FailureEvent], None]):
        """Add an alert handler function"""
        self.alert_handlers.append(handler)
    
    def get_system_health_status(self) -> Dict[str, Any]:
        """Get comprehensive system health status"""
        current_time = time.time()
        
        # Component status
        component_status = {}
        healthy_components = 0
        failed_components = 0
        
        for comp_id, comp_info in self.registered_components.items():
            status = comp_info["status"]
            component_status[comp_id] = {
                "status": status,
                "type": comp_info["type"],
                "last_seen": comp_info["last_seen"],
                "uptime_hours": (current_time - comp_info["registered_at"]) / 3600
            }
            
            if status == "active":
                healthy_components += 1
            else:
                failed_components += 1
        
        # Recent failures
        recent_failures = [
            event for event in self.failure_events.values()
            if current_time - event.timestamp < 3600  # Last hour
        ]
        
        # Circuit breaker status
        circuit_breaker_status = {}
        for service_id, cb in self.circuit_breakers.items():
            circuit_breaker_status[service_id] = {
                "state": cb.state,
                "current_failures": cb.current_failures,
                "successful_calls": cb.successful_calls,
                "failed_calls": cb.failed_calls
            }
        
        # Calculate system availability
        total_components = len(self.registered_components)
        availability_percentage = (healthy_components / total_components * 100) if total_components > 0 else 100
        
        return {
            "system_id": self.system_id,
            "monitoring_active": self.is_running,
            "overall_health": {
                "availability_percentage": round(availability_percentage, 2),
                "total_components": total_components,
                "healthy_components": healthy_components,
                "failed_components": failed_components
            },
            "component_status": component_status,
            "recent_failures": len(recent_failures),
            "circuit_breakers": circuit_breaker_status,
            "recovery_stats": {
                "total_failures": self.total_failures_detected,
                "successful_recoveries": self.successful_recoveries,
                "failed_recoveries": self.failed_recoveries,
                "active_recoveries": self.active_recoveries
            },
            "configuration": {
                "auto_recovery_enabled": self.auto_recovery_enabled,
                "monitoring_interval": self.monitoring_interval,
                "max_concurrent_recoveries": self.max_concurrent_recoveries
            }
        }
    
    def simulate_failure(self, component_id: str, failure_type: FailureType) -> str:
        """Simulate a failure for testing purposes"""
        failure_descriptions = {
            FailureType.NODE_FAILURE: f"Node {component_id} has become unresponsive",
            FailureType.NETWORK_PARTITION: f"Network partition detected affecting {component_id}",
            FailureType.DATA_CORRUPTION: f"Data corruption detected in {component_id}",
            FailureType.SERVICE_UNAVAILABLE: f"Service {component_id} is unavailable",
            FailureType.PERFORMANCE_DEGRADATION: f"Performance degradation detected in {component_id}",
            FailureType.SECURITY_BREACH: f"Security breach detected in {component_id}"
        }
        
        description = failure_descriptions.get(failure_type, f"Unknown failure in {component_id}")
        severity = AlertLevel.CRITICAL if failure_type in [
            FailureType.NODE_FAILURE, 
            FailureType.DATA_CORRUPTION, 
            FailureType.SECURITY_BREACH
        ] else AlertLevel.WARNING
        
        return self.report_failure(component_id, failure_type, description, severity)
    
    def _monitoring_loop(self):
        """Main monitoring loop running in a separate thread"""
        while self.is_running:
            try:
                # Perform health checks
                self._perform_health_checks()
                
                # Check circuit breakers
                self._check_circuit_breakers()
                
                # Check for stuck recovery processes
                self._check_recovery_processes()
                
                # Sleep until next monitoring cycle
                time.sleep(self.monitoring_interval)
                
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(self.monitoring_interval)
    
    def _perform_health_checks(self):
        """Perform health checks on all registered components"""
        current_time = time.time()
        
        for component_id, health_check in self.health_checks.items():
            # Check if it's time for health check
            if current_time - health_check.last_check < health_check.interval_seconds:
                continue
            
            health_check.last_check = current_time
            
            try:
                # Perform health check with timeout
                is_healthy = health_check.check_function()
                
                if is_healthy:
                    health_check.current_failures = 0
                    health_check.last_success = current_time
                    
                    # Update component status
                    if component_id in self.registered_components:
                        self.registered_components[component_id]["status"] = "active"
                        self.registered_components[component_id]["last_seen"] = current_time
                
                else:
                    health_check.current_failures += 1
                    
                    # Check if failure threshold reached
                    if health_check.current_failures >= health_check.failure_threshold:
                        self.report_failure(
                            component_id=component_id,
                            failure_type=FailureType.SERVICE_UNAVAILABLE,
                            description=f"Health check failed {health_check.current_failures} times",
                            severity=AlertLevel.CRITICAL
                        )
                        
            except Exception as e:
                health_check.current_failures += 1
                print(f"Health check exception for {component_id}: {e}")
    
    def _check_circuit_breakers(self):
        """Check and update circuit breaker states"""
        current_time = time.time()
        
        for service_id, circuit_breaker in self.circuit_breakers.items():
            if circuit_breaker.state == "OPEN":
                # Check if we should attempt to reset
                if current_time - circuit_breaker.last_failure_time > circuit_breaker.reset_timeout_seconds:
                    circuit_breaker.state = "HALF_OPEN"
                    print(f"Circuit breaker for {service_id} moved to HALF_OPEN for testing")
    
    def _check_recovery_processes(self):
        """Check for stuck or failed recovery processes"""
        # In a real system, this would monitor active recovery operations
        # and handle cases where recovery processes get stuck
        pass
    
    def _trigger_alerts(self, failure_event: FailureEvent):
        """Trigger alerts for a failure event"""
        for handler in self.alert_handlers:
            try:
                handler(failure_event)
            except Exception as e:
                print(f"Error in alert handler: {e}")
    
    def _initiate_recovery(self, failure_event: FailureEvent) -> bool:
        """Initiate automatic recovery for a failure event"""
        if self.active_recoveries >= self.max_concurrent_recoveries:
            print(f"Maximum concurrent recoveries reached, queuing recovery for {failure_event.event_id}")
            return False
        
        component_id = failure_event.affected_component
        
        # Determine recovery strategy
        recovery_actions = self._determine_recovery_strategy(failure_event)
        failure_event.recovery_actions = recovery_actions
        
        # Execute recovery
        return self._execute_recovery_actions(failure_event)
    
    def _determine_recovery_strategy(self, failure_event: FailureEvent) -> List[RecoveryAction]:
        """Determine the appropriate recovery strategy for a failure"""
        component_id = failure_event.affected_component
        failure_type = failure_event.failure_type
        
        # Check if we have predefined recovery strategies
        if component_id in self.recovery_strategies:
            return self.recovery_strategies[component_id]
        
        # Default recovery strategies based on failure type
        if failure_type == FailureType.NODE_FAILURE:
            if component_id in self.backup_components:
                return [RecoveryAction.FAILOVER_TO_BACKUP, RecoveryAction.REDISTRIBUTE_LOAD]
            else:
                return [RecoveryAction.RESTART_SERVICE]
        
        elif failure_type == FailureType.SERVICE_UNAVAILABLE:
            return [RecoveryAction.RESTART_SERVICE, RecoveryAction.REDISTRIBUTE_LOAD]
        
        elif failure_type == FailureType.DATA_CORRUPTION:
            return [RecoveryAction.REPAIR_DATA, RecoveryAction.ISOLATE_NODE]
        
        elif failure_type == FailureType.NETWORK_PARTITION:
            return [RecoveryAction.REDISTRIBUTE_LOAD]
        
        elif failure_type == FailureType.SECURITY_BREACH:
            return [RecoveryAction.ISOLATE_NODE, RecoveryAction.MANUAL_INTERVENTION]
        
        else:
            return [RecoveryAction.RESTART_SERVICE]
    
    def _execute_recovery_actions(self, failure_event: FailureEvent) -> bool:
        """Execute recovery actions for a failure event"""
        self.active_recoveries += 1
        recovery_start_time = time.time()
        
        try:
            component_id = failure_event.affected_component
            success = False
            
            for action in failure_event.recovery_actions:
                print(f"Executing recovery action {action.name} for {component_id}")
                
                if action == RecoveryAction.RESTART_SERVICE:
                    success = self._restart_service(component_id)
                
                elif action == RecoveryAction.FAILOVER_TO_BACKUP:
                    success = self._failover_to_backup(component_id)
                
                elif action == RecoveryAction.REDISTRIBUTE_LOAD:
                    success = self._redistribute_load(component_id)
                
                elif action == RecoveryAction.REPAIR_DATA:
                    success = self._repair_data(component_id)
                
                elif action == RecoveryAction.ISOLATE_NODE:
                    success = self._isolate_node(component_id)
                
                elif action == RecoveryAction.MANUAL_INTERVENTION:
                    print(f"Manual intervention required for {component_id}")
                    success = False  # Requires human intervention
                
                if success:
                    break
            
            # Update failure event
            failure_event.resolved = success
            if success:
                failure_event.resolution_time = time.time()
                self.successful_recoveries += 1
                
                # Update component status
                if component_id in self.registered_components:
                    self.registered_components[component_id]["status"] = "active"
                
                print(f"Recovery successful for {component_id}")
            else:
                self.failed_recoveries += 1
                print(f"Recovery failed for {component_id}")
            
            return success
            
        except Exception as e:
            print(f"Error executing recovery actions: {e}")
            self.failed_recoveries += 1
            return False
        
        finally:
            self.active_recoveries -= 1
    
    def _restart_service(self, component_id: str) -> bool:
        """Simulate service restart"""
        print(f"Restarting service {component_id}")
        time.sleep(1)  # Simulate restart time
        return random.random() > 0.2  # 80% success rate
    
    def _failover_to_backup(self, component_id: str) -> bool:
        """Simulate failover to backup component"""
        backups = self.backup_components.get(component_id, [])
        if not backups:
            return False
        
        backup_id = backups[0]  # Use first backup
        print(f"Failing over from {component_id} to backup {backup_id}")
        time.sleep(2)  # Simulate failover time
        return random.random() > 0.1  # 90% success rate
    
    def _redistribute_load(self, component_id: str) -> bool:
        """Simulate load redistribution"""
        print(f"Redistributing load from {component_id}")
        time.sleep(0.5)  # Simulate redistribution time
        return random.random() > 0.05  # 95% success rate
    
    def _repair_data(self, component_id: str) -> bool:
        """Simulate data repair"""
        print(f"Repairing data for {component_id}")
        time.sleep(3)  # Simulate repair time
        return random.random() > 0.3  # 70% success rate
    
    def _isolate_node(self, component_id: str) -> bool:
        """Simulate node isolation"""
        print(f"Isolating node {component_id}")
        if component_id in self.registered_components:
            self.registered_components[component_id]["status"] = "isolated"
        return True  # Always successful