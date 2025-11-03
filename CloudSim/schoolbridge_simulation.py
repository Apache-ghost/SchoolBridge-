"""
SchoolBridge Distributed System - Main Simulation
Comprehensive demonstration of the distributed parent-teacher communication platform
"""
import time
import random
import json
from typing import Dict, List
from datetime import datetime, timedelta

# Import all our distributed system components
from communication_service import CommunicationService, User, Student, MessageType
from school_node import SchoolNode, SchoolConfig, NodeStatus
from p2p_communication import P2PCommunicationLayer
from distributed_database import DistributedDatabase, DatabaseNode, DataType, DataRecord
from load_balancer import LoadBalancer, LoadBalancingAlgorithm, NodeInfo, Region, MultiRegionManager, NodeHealth
from fault_tolerance import FaultToleranceSystem, FailureType, AlertLevel

class SchoolBridgeSimulation:
    """
    Main simulation class for the SchoolBridge Distributed System
    Demonstrates all features including fault tolerance, load balancing, and data replication
    """
    
    def __init__(self):
        self.simulation_id = f"schoolbridge-sim-{int(time.time())}"
        
        # Initialize core components
        self.multi_region_manager = MultiRegionManager(self.simulation_id)
        self.distributed_db = DistributedDatabase(self.simulation_id)
        self.p2p_layer = P2PCommunicationLayer(f"p2p-{self.simulation_id}")
        self.fault_tolerance = FaultToleranceSystem(self.simulation_id)
        
        # System components
        self.school_nodes: Dict[str, SchoolNode] = {}
        self.database_nodes: Dict[str, DatabaseNode] = {}
        self.communication_services: Dict[str, CommunicationService] = {}
        
        # Simulation data
        self.users: Dict[str, User] = {}
        self.students: Dict[str, Student] = {}
        
        # Metrics and monitoring
        self.start_time = time.time()
        self.simulation_events = []
        
        print(f"🌟 SchoolBridge Distributed System Simulation Initialized")
        print(f"📊 Simulation ID: {self.simulation_id}")
    
    def setup_infrastructure(self):
        """Set up the distributed infrastructure with multiple regions and nodes"""
        print("\n🏗️  Setting up distributed infrastructure...")
        
        # Create regions
        regions = [
            Region(
                region_id="us-east",
                name="US East Coast",
                location="Virginia",
                max_capacity=5000,
                priority=1
            ),
            Region(
                region_id="us-west", 
                name="US West Coast",
                location="California",
                max_capacity=4000,
                priority=2
            ),
            Region(
                region_id="eu-central",
                name="Europe Central", 
                location="Germany",
                max_capacity=3000,
                priority=3
            )
        ]
        
        # Set up inter-region latencies
        regions[0].latency_to_regions = {"us-west": 70.0, "eu-central": 120.0}
        regions[1].latency_to_regions = {"us-east": 70.0, "eu-central": 150.0}
        regions[2].latency_to_regions = {"us-east": 120.0, "us-west": 150.0}
        
        # Add regions to multi-region manager
        for region in regions:
            self.multi_region_manager.add_region(region)
        
        # Create school nodes in each region
        schools = [
            {"id": "riverside-high", "name": "Riverside High School", "region": "us-east"},
            {"id": "oakwood-elementary", "name": "Oakwood Elementary", "region": "us-east"},
            {"id": "sunset-middle", "name": "Sunset Middle School", "region": "us-west"},
            {"id": "mountain-view-high", "name": "Mountain View High", "region": "us-west"},
            {"id": "europa-international", "name": "Europa International School", "region": "eu-central"}
        ]
        
        for school_info in schools:
            self._create_school_node(school_info)
        
        # Create database nodes
        for i, region_id in enumerate(["us-east", "us-west", "eu-central"]):
            for j in range(2):  # 2 DB nodes per region
                self._create_database_node(f"db-{region_id}-{j+1}", region_id)
        
        # Start fault tolerance monitoring
        self.fault_tolerance.start_monitoring()
        
        print("✅ Infrastructure setup complete!")
    
    def populate_sample_data(self):
        """Populate the system with sample schools, users, and students"""
        print("\n👥 Populating sample data...")
        
        # Sample users and students for each school
        school_configs = [
            {
                "school_id": "riverside-high",
                "teachers": 25,
                "students": 300,
                "parents_per_student": 2
            },
            {
                "school_id": "oakwood-elementary", 
                "teachers": 15,
                "students": 200,
                "parents_per_student": 2
            },
            {
                "school_id": "sunset-middle",
                "teachers": 20,
                "students": 250,
                "parents_per_student": 2
            },
            {
                "school_id": "mountain-view-high",
                "teachers": 30,
                "students": 400,
                "parents_per_student": 2
            },
            {
                "school_id": "europa-international",
                "teachers": 18,
                "students": 180,
                "parents_per_student": 2
            }
        ]
        
        for school_config in school_configs:
            self._populate_school_data(school_config)
        
        print(f"✅ Sample data populated!")
        print(f"   📚 Total Schools: {len(school_configs)}")
        print(f"   👨‍🏫 Total Users: {len(self.users)}")
        print(f"   🎓 Total Students: {len(self.students)}")
    
    def demonstrate_communication_features(self):
        """Demonstrate various communication features"""
        print("\n💬 Demonstrating communication features...")
        
        # Get some sample data
        sample_students = list(self.students.values())[:5]
        sample_teachers = [u for u in self.users.values() if u.role == "teacher"][:3]
        sample_parents = [u for u in self.users.values() if u.role == "parent"][:5]
        
        if not (sample_students and sample_teachers and sample_parents):
            print("⚠️  Not enough sample data for communication demo")
            return
        
        # Demonstrate attendance alerts
        print("📋 Sending attendance alerts...")
        for i, student in enumerate(sample_students):
            school_node = self.school_nodes.get(student.school_id)
            if school_node:
                status = "absent" if i % 2 == 0 else "late"
                school_node.communication_service.send_attendance_alert(
                    student.student_id, status, datetime.now().strftime("%Y-%m-%d")
                )
        
        # Demonstrate P2P messaging
        print("💭 Setting up P2P communication...")
        for teacher in sample_teachers:
            self.p2p_layer.register_user(teacher.user_id)
        
        for parent in sample_parents:
            self.p2p_layer.register_user(parent.user_id)
        
        # Send some P2P messages
        if sample_teachers and sample_parents:
            teacher = sample_teachers[0]
            parent = sample_parents[0]
            
            message_id = self.p2p_layer.send_message(
                teacher.user_id,
                parent.user_id,
                "Hello! I wanted to discuss your child's recent progress in math class.",
                "text"
            )
            
            if message_id:
                print(f"   ✉️  P2P message sent from teacher to parent")
        
        # Demonstrate school announcements
        print("📢 Broadcasting school events...")
        for school_id in ["riverside-high", "oakwood-elementary"]:
            school_node = self.school_nodes.get(school_id)
            if school_node:
                messages_sent = school_node.communication_service.send_event_broadcast(
                    school_id,
                    "Parent-Teacher Conference",
                    "Annual parent-teacher conferences will be held next week.",
                    (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")
                )
                print(f"   📡 Broadcast to {messages_sent} parents in {school_id}")
        
        print("✅ Communication features demonstrated!")
    
    def demonstrate_fault_tolerance(self):
        """Demonstrate fault tolerance and recovery mechanisms"""
        print("\n🛡️  Demonstrating fault tolerance...")
        
        # Get a school node to simulate failure
        school_node_id = list(self.school_nodes.keys())[0]
        school_node = self.school_nodes[school_node_id]
        
        print(f"🔴 Simulating node failure for {school_node_id}")
        
        # Report the failure
        failure_id = self.fault_tolerance.simulate_failure(
            school_node_id, 
            FailureType.NODE_FAILURE
        )
        
        # Simulate the actual failure
        school_node.simulate_node_failure()
        
        # Wait a moment for recovery
        time.sleep(2)
        
        # Attempt recovery
        print(f"🔧 Attempting recovery for {school_node_id}")
        school_node.recover_from_failure()
        
        # Network partition simulation
        print("🌐 Simulating network partition...")
        self.fault_tolerance.simulate_failure(
            "us-west",
            FailureType.NETWORK_PARTITION
        )
        
        # Data corruption simulation
        db_node_id = list(self.database_nodes.keys())[0]
        print(f"💾 Simulating data corruption in {db_node_id}")
        self.fault_tolerance.simulate_failure(
            db_node_id,
            FailureType.DATA_CORRUPTION
        )
        
        print("✅ Fault tolerance demonstrations complete!")
    
    def demonstrate_load_balancing(self):
        """Demonstrate load balancing across regions"""
        print("\n⚖️  Demonstrating load balancing...")
        
        # Simulate requests from different regions
        client_regions = ["us-east", "us-west", "eu-central"]
        
        for i in range(20):
            client_region = random.choice(client_regions)
            
            # Route request through multi-region manager
            target_region, target_node = self.multi_region_manager.route_request(
                client_region,
                {"request_type": "user_login", "user_id": f"user_{i}"}
            )
            
            if target_region and target_node:
                # Simulate request processing
                response_time = random.uniform(50, 200)  # ms
                
                # Update load balancer metrics
                if target_region in self.multi_region_manager.regional_load_balancers:
                    lb = self.multi_region_manager.regional_load_balancers[target_region]
                    lb.record_request_start(target_node)
                    lb.record_request_completion(target_node, response_time, True)
                
                if i % 5 == 0:  # Print every 5th request
                    print(f"   🔄 Request from {client_region} routed to {target_region}/{target_node}")
        
        print("✅ Load balancing demonstration complete!")
    
    def demonstrate_data_replication(self):
        """Demonstrate data replication across database nodes"""
        print("\n💾 Demonstrating data replication...")
        
        # Write some data to the distributed database
        sample_data_sets = [
            {
                "type": DataType.STUDENT_RECORD,
                "data": {
                    "student_id": "student_001",
                    "name": "John Doe",
                    "grade": "10th",
                    "school_id": "riverside-high"
                }
            },
            {
                "type": DataType.MESSAGE_LOG,
                "data": {
                    "message_id": "msg_001",
                    "sender": "teacher_001", 
                    "recipient": "parent_001",
                    "content": "Student performing well in mathematics"
                }
            },
            {
                "type": DataType.ANNOUNCEMENT,
                "data": {
                    "announcement_id": "ann_001",
                    "title": "School Closure Notice",
                    "content": "School will be closed due to weather conditions",
                    "school_id": "riverside-high"
                }
            }
        ]
        
        for data_set in sample_data_sets:
            record_id = self.distributed_db.write_data(
                data_set["type"],
                data_set["data"]
            )
            
            if record_id:
                print(f"   📝 Written {data_set['type'].name} with ID: {record_id}")
        
        # Demonstrate cross-node synchronization
        print("🔄 Performing cross-node synchronization...")
        sync_results = self.distributed_db.sync_all_nodes()
        print(f"   ✅ Synchronized {sync_results['total_synchronized']} records")
        
        # Query data from different nodes
        print("🔍 Querying data from distributed nodes...")
        student_records = self.distributed_db.query_data(DataType.STUDENT_RECORD, limit=5)
        print(f"   📊 Found {len(student_records)} student records across all nodes")
        
        print("✅ Data replication demonstration complete!")
    
    def run_performance_tests(self):
        """Run performance tests on the distributed system"""
        print("\n🚀 Running performance tests...")
        
        # Test message throughput
        print("📈 Testing message throughput...")
        start_time = time.time()
        messages_sent = 0
        
        for school_id, school_node in list(self.school_nodes.items())[:3]:
            for i in range(50):
                school_node.communication_service.send_chat_message(
                    f"teacher_{i % 10}",
                    f"parent_{i % 15}", 
                    f"Test message {i}",
                    f"Performance Test Subject {i}"
                )
                messages_sent += 1
        
        # Process messages
        for school_node in self.school_nodes.values():
            school_node.process_local_messages(20)
        
        elapsed_time = time.time() - start_time
        throughput = messages_sent / elapsed_time
        
        print(f"   📊 Sent {messages_sent} messages in {elapsed_time:.2f} seconds")
        print(f"   🔥 Throughput: {throughput:.2f} messages/second")
        
        # Test P2P performance
        print("💬 Testing P2P communication performance...")
        p2p_start = time.time()
        p2p_messages = 0
        
        users_list = list(self.users.values())
        for i in range(30):
            if len(users_list) >= 2:
                sender = random.choice(users_list)
                recipient = random.choice(users_list)
                
                if sender.user_id != recipient.user_id:
                    message_id = self.p2p_layer.send_message(
                        sender.user_id,
                        recipient.user_id,
                        f"Performance test message {i}"
                    )
                    if message_id:
                        p2p_messages += 1
        
        p2p_elapsed = time.time() - p2p_start
        p2p_throughput = p2p_messages / p2p_elapsed if p2p_elapsed > 0 else 0
        
        print(f"   📊 P2P messages: {p2p_messages} in {p2p_elapsed:.2f} seconds")
        print(f"   🔥 P2P throughput: {p2p_throughput:.2f} messages/second")
        
        print("✅ Performance tests complete!")
    
    def generate_comprehensive_report(self) -> Dict:
        """Generate a comprehensive system report"""
        print("\n📊 Generating comprehensive system report...")
        
        # Collect metrics from all components
        report = {
            "simulation_info": {
                "simulation_id": self.simulation_id,
                "start_time": self.start_time,
                "duration_seconds": time.time() - self.start_time,
                "timestamp": datetime.now().isoformat()
            },
            "infrastructure": {
                "regions": len(self.multi_region_manager.regions),
                "school_nodes": len(self.school_nodes),
                "database_nodes": len(self.database_nodes),
                "users": len(self.users),
                "students": len(self.students)
            },
            "multi_region_status": self.multi_region_manager.get_system_statistics(),
            "database_status": self.distributed_db.get_system_status(),
            "p2p_status": self.p2p_layer.get_layer_statistics(),
            "fault_tolerance_status": self.fault_tolerance.get_system_health_status(),
            "school_node_statistics": {},
            "load_balancer_statistics": {}
        }
        
        # Collect school node statistics
        for node_id, node in self.school_nodes.items():
            report["school_node_statistics"][node_id] = node.get_node_statistics()
        
        # Collect load balancer statistics
        for region_id, lb in self.multi_region_manager.regional_load_balancers.items():
            report["load_balancer_statistics"][region_id] = lb.get_balancer_statistics()
        
        return report
    
    def _create_school_node(self, school_info: Dict):
        """Create a school node with proper configuration"""
        school_config = SchoolConfig(
            school_id=school_info["id"],
            name=school_info["name"],
            address=f"123 School St, {school_info['region']}",
            region=school_info["region"],
            timezone="UTC",
            academic_year="2024-2025",
            total_students=300,
            total_teachers=25,
            total_parents=600,
            contact_info={"phone": "555-0100", "email": f"admin@{school_info['id']}.edu"}
        )
        
        node_capacity = {
            "max_users": 1000,
            "max_messages_per_hour": 5000,
            "storage_capacity_gb": 50,
            "bandwidth_mbps": 100
        }
        
        school_node = SchoolNode(school_config, node_capacity)
        self.school_nodes[school_info["id"]] = school_node
        
        # Create load balancer node info for this school
        node_info = NodeInfo(
            node_id=school_node.node_id,
            region=school_info["region"],
            weight=1,
            max_connections=500,
            health_status=NodeHealth.HEALTHY
        )
        
        # Add to region
        self.multi_region_manager.add_node_to_region(school_info["region"], node_info)
        
        # Register with fault tolerance
        self.fault_tolerance.register_component(
            school_node.node_id,
            "school_node",
            health_check_func=lambda: school_node.status == NodeStatus.ACTIVE,
            dependencies=[],
            backup_components=[]
        )
        
        print(f"   🏫 Created school node: {school_info['name']}")
    
    def _create_database_node(self, node_id: str, region: str):
        """Create a database node"""
        db_node = DatabaseNode(node_id, storage_capacity_gb=200)
        self.database_nodes[node_id] = db_node
        
        # Add to distributed database
        master_data_types = []
        if "db-us-east-1" == node_id:
            master_data_types = [DataType.STUDENT_RECORD, DataType.USER_PROFILE]
        elif "db-us-west-1" == node_id:
            master_data_types = [DataType.MESSAGE_LOG, DataType.ANNOUNCEMENT]
        
        self.distributed_db.add_node(db_node, master_data_types)
        
        # Register with fault tolerance
        self.fault_tolerance.register_component(
            node_id,
            "database_node",
            health_check_func=lambda: True,  # Simplified health check
            dependencies=[],
            backup_components=[]
        )
        
        print(f"   💾 Created database node: {node_id} in {region}")
    
    def _populate_school_data(self, school_config: Dict):
        """Populate data for a specific school"""
        school_id = school_config["school_id"]
        school_node = self.school_nodes.get(school_id)
        
        if not school_node:
            return
        
        # Create teachers
        for i in range(school_config["teachers"]):
            teacher = User(
                user_id=f"teacher_{school_id}_{i}",
                name=f"Teacher {i} ({school_id})",
                role="teacher",
                school_id=school_id,
                contact_info={"email": f"teacher{i}@{school_id}.edu", "phone": f"555-01{i:02d}"}
            )
            
            self.users[teacher.user_id] = teacher
            school_node.register_user_locally(teacher)
        
        # Create students and parents
        for i in range(school_config["students"]):
            student = Student(
                student_id=f"student_{school_id}_{i}",
                name=f"Student {i} ({school_id})",
                class_id=f"class_{i % 10}",
                parent_ids=[],
                teacher_ids=[f"teacher_{school_id}_{i % school_config['teachers']}"],
                school_id=school_id
            )
            
            # Create parents for this student
            parents_for_student = []
            for j in range(school_config["parents_per_student"]):
                parent = User(
                    user_id=f"parent_{school_id}_{i}_{j}",
                    name=f"Parent {j} of Student {i} ({school_id})",
                    role="parent",
                    school_id=school_id,
                    contact_info={"email": f"parent{i}_{j}@email.com", "phone": f"555-02{i:02d}"}
                )
                
                parents_for_student.append(parent.user_id)
                self.users[parent.user_id] = parent
                school_node.register_user_locally(parent)
            
            student.parent_ids = parents_for_student
            self.students[student.student_id] = student
            school_node.register_student_locally(student)

def main():
    """Main function to run the SchoolBridge simulation"""
    print("🚀 Starting SchoolBridge Distributed System Simulation")
    print("=" * 60)
    
    # Initialize simulation
    sim = SchoolBridgeSimulation()
    
    try:
        # Phase 1: Infrastructure Setup
        sim.setup_infrastructure()
        time.sleep(1)
        
        # Phase 2: Data Population
        sim.populate_sample_data()
        time.sleep(1)
        
        # Phase 3: Communication Features
        sim.demonstrate_communication_features()
        time.sleep(2)
        
        # Phase 4: Load Balancing
        sim.demonstrate_load_balancing()
        time.sleep(1)
        
        # Phase 5: Data Replication
        sim.demonstrate_data_replication()
        time.sleep(1)
        
        # Phase 6: Fault Tolerance
        sim.demonstrate_fault_tolerance()
        time.sleep(2)
        
        # Phase 7: Performance Testing
        sim.run_performance_tests()
        time.sleep(1)
        
        # Phase 8: Generate Report
        final_report = sim.generate_comprehensive_report()
        
        # Display summary
        print("\n" + "=" * 60)
        print("📋 SIMULATION SUMMARY")
        print("=" * 60)
        
        print(f"🆔 Simulation ID: {final_report['simulation_info']['simulation_id']}")
        print(f"⏱️  Duration: {final_report['simulation_info']['duration_seconds']:.2f} seconds")
        print(f"🏗️  Infrastructure:")
        print(f"   - Regions: {final_report['infrastructure']['regions']}")
        print(f"   - School Nodes: {final_report['infrastructure']['school_nodes']}")
        print(f"   - Database Nodes: {final_report['infrastructure']['database_nodes']}")
        print(f"   - Users: {final_report['infrastructure']['users']}")
        print(f"   - Students: {final_report['infrastructure']['students']}")
        
        print(f"\n💬 Communication Stats:")
        p2p_stats = final_report['p2p_status']
        print(f"   - P2P Connections: {p2p_stats['total_p2p_connections']}")
        print(f"   - Messages Sent: {p2p_stats['total_messages_sent']}")
        
        print(f"\n🛡️  Fault Tolerance:")
        ft_stats = final_report['fault_tolerance_status']
        print(f"   - System Availability: {ft_stats['overall_health']['availability_percentage']:.1f}%")
        print(f"   - Total Failures: {ft_stats['recovery_stats']['total_failures']}")
        print(f"   - Successful Recoveries: {ft_stats['recovery_stats']['successful_recoveries']}")
        
        print(f"\n🌐 Multi-Region Performance:")
        mr_stats = final_report['multi_region_status']
        print(f"   - Active Regions: {mr_stats['regions']['active_regions']}")
        print(f"   - Cross-Region Requests: {mr_stats['performance']['cross_region_requests']}")
        print(f"   - Failover Events: {mr_stats['performance']['failover_events']}")
        
        # Save detailed report
        report_filename = f"schoolbridge_report_{int(time.time())}.json"
        with open(report_filename, 'w') as f:
            json.dump(final_report, f, indent=2, default=str)
        print(f"\n📄 Detailed report saved to: {report_filename}")
        
        print("\n🎉 SchoolBridge Distributed System Simulation Complete!")
        print("✅ All features successfully demonstrated")
        
    except KeyboardInterrupt:
        print("\n⛔ Simulation interrupted by user")
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")
    finally:
        # Cleanup
        sim.fault_tolerance.stop_monitoring()
        print("\n🧹 Cleanup completed")

if __name__ == "__main__":
    main()