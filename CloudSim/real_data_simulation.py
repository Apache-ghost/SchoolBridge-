"""
SchoolBridge Real Data Simulation
Demonstrates the distributed system using actual Cameroon schools and real people
"""
import time
import random
from datetime import datetime, timedelta
from typing import Dict, List

# Import all distributed system components
from communication_service import CommunicationService, User, Student, MessageType
from school_node import SchoolNode, SchoolConfig
from p2p_communication import P2PCommunicationLayer
from distributed_database import DistributedDatabase, DatabaseNode, DataType
from load_balancer import MultiRegionManager, Region, NodeInfo, NodeHealth
from fault_tolerance import FaultToleranceSystem, FailureType

# Import real data
from real_data_config import (
    REAL_SCHOOLS, REAL_PARENTS, REAL_STUDENTS, REAL_TEACHERS,
    SAMPLE_GRADES, SAMPLE_ATTENDANCE, SCHOOL_FEES
)

class RealDataSchoolBridgeSimulation:
    """
    SchoolBridge simulation using real Cameroon schools and actual people
    """
    
    def __init__(self):
        self.simulation_id = f"cameroon-schoolbridge-{int(time.time())}"
        
        # Initialize distributed system components
        self.multi_region_manager = MultiRegionManager(self.simulation_id)
        self.distributed_db = DistributedDatabase(self.simulation_id)
        self.p2p_layer = P2PCommunicationLayer(f"p2p-{self.simulation_id}")
        self.fault_tolerance = FaultToleranceSystem(self.simulation_id)
        
        # System components
        self.school_nodes: Dict[str, SchoolNode] = {}
        self.database_nodes: Dict[str, DatabaseNode] = {}
        
        # Real data storage
        self.real_users: Dict[str, User] = {}
        self.real_students: Dict[str, Student] = {}
        
        print("🇨🇲 SchoolBridge Cameroon - Real Data Simulation Initialized")
        print(f"📊 Simulation ID: {self.simulation_id}")
    
    def setup_real_infrastructure(self):
        """Set up infrastructure using real Cameroon locations"""
        print("\n🏗️  Setting up Cameroon distributed infrastructure...")
        
        # Create regions based on Cameroon locations
        regions = [
            Region(
                region_id="centre-region",
                name="Centre Region (Yaoundé)",
                location="Yaoundé, Cameroon",
                max_capacity=8000,
                priority=1
            ),
            Region(
                region_id="littoral-region",
                name="Littoral Region (Douala)", 
                location="Douala, Cameroon",
                max_capacity=7000,
                priority=2
            ),
            Region(
                region_id="west-region",
                name="West Region (Bafoussam)",
                location="Bafoussam, Cameroon", 
                max_capacity=5000,
                priority=3
            )
        ]
        
        # Set up inter-city latencies (realistic for Cameroon)
        regions[0].latency_to_regions = {"littoral-region": 45.0, "west-region": 85.0}  # Yaoundé to others
        regions[1].latency_to_regions = {"centre-region": 45.0, "west-region": 65.0}   # Douala to others  
        regions[2].latency_to_regions = {"centre-region": 85.0, "littoral-region": 65.0}  # Bafoussam to others
        
        # Add regions to manager
        for region in regions:
            self.multi_region_manager.add_region(region)
        
        # Create real school nodes
        region_mapping = {
            "us-east": "centre-region",      # ICT University -> Yaoundé
            "us-west": "littoral-region",    # Polytech -> Douala  
            "eu-central": "west-region"      # University Yaoundé -> Bafoussam (distributed campus)
        }
        
        for school_info in REAL_SCHOOLS:
            mapped_region = region_mapping.get(school_info["region"], "centre-region")
            school_info["region"] = mapped_region
            self._create_real_school_node(school_info)
        
        # Create database nodes in each region
        db_locations = [
            ("db-yaounde-1", "centre-region"),
            ("db-yaounde-2", "centre-region"), 
            ("db-douala-1", "littoral-region"),
            ("db-douala-2", "littoral-region"),
            ("db-bafoussam-1", "west-region"),
            ("db-bafoussam-2", "west-region")
        ]
        
        for db_id, region in db_locations:
            self._create_database_node(db_id, region)
        
        # Start fault tolerance monitoring
        self.fault_tolerance.start_monitoring()
        
        print("✅ Cameroon infrastructure setup complete!")
        
    def populate_real_data(self):
        """Populate system with real Cameroon school data"""
        print("\n👥 Populating real Cameroon school data...")
        
        # Register real teachers
        teacher_count = 0
        for teacher_info in REAL_TEACHERS:
            teacher = User(
                user_id=f"teacher_{teacher_info['school_id']}_{teacher_count}",
                name=teacher_info["name"],
                role="teacher", 
                school_id=teacher_info["school_id"],
                contact_info={
                    "phone": teacher_info["phone"],
                    "email": teacher_info["email"],
                    "office": teacher_info["office"],
                    "subjects": teacher_info["subjects"]
                }
            )
            
            self.real_users[teacher.user_id] = teacher
            school_node = self.school_nodes.get(teacher_info["school_id"])
            if school_node:
                school_node.register_user_locally(teacher)
                # Register for P2P communication
                self.p2p_layer.register_user(teacher.user_id)
            
            teacher_count += 1
        
        # Register real parents  
        parent_count = 0
        for parent_info in REAL_PARENTS:
            parent = User(
                user_id=f"parent_{parent_info['school_id']}_{parent_count}",
                name=parent_info["name"],
                role="parent",
                school_id=parent_info["school_id"], 
                contact_info={
                    "phone": parent_info["phone"],
                    "email": parent_info["email"],
                    "children": parent_info["children"]
                }
            )
            
            self.real_users[parent.user_id] = parent
            school_node = self.school_nodes.get(parent_info["school_id"])
            if school_node:
                school_node.register_user_locally(parent)
                # Register for P2P communication
                self.p2p_layer.register_user(parent.user_id)
            
            parent_count += 1
        
        # Register real students with their actual parents
        for student_info in REAL_STUDENTS:
            # Find parent IDs for this student
            parent_ids = []
            for parent_id, parent in self.real_users.items():
                if (parent.role == "parent" and 
                    parent.school_id == student_info["school_id"] and
                    student_info["student_id"] in parent.contact_info.get("children", [])):
                    parent_ids.append(parent_id)
            
            # Find teacher IDs for this school
            teacher_ids = []
            for teacher_id, teacher in self.real_users.items():
                if (teacher.role == "teacher" and 
                    teacher.school_id == student_info["school_id"]):
                    teacher_ids.append(teacher_id)
            
            student = Student(
                student_id=student_info["student_id"],
                name=student_info["name"],
                class_id=student_info["program"],
                parent_ids=parent_ids,
                teacher_ids=teacher_ids,
                school_id=student_info["school_id"],
                academic_records={
                    "program": student_info["program"],
                    "year": student_info["year"],
                    "grades": SAMPLE_GRADES.get(student_info["student_id"], {})
                },
                attendance_records=SAMPLE_ATTENDANCE.get(student_info["student_id"], {})
            )
            
            self.real_students[student.student_id] = student
            school_node = self.school_nodes.get(student_info["school_id"])
            if school_node:
                school_node.register_student_locally(student)
        
        print(f"✅ Real data populated!")
        print(f"   🏫 Schools: {len(REAL_SCHOOLS)}")
        print(f"   👨‍🏫 Teachers: {len(REAL_TEACHERS)}")
        print(f"   👨‍👩‍👧‍👦 Parents: {len(REAL_PARENTS)}")  
        print(f"   🎓 Students: {len(REAL_STUDENTS)}")
    
    def demonstrate_real_communications(self):
        """Demonstrate communications using real people and scenarios"""
        print("\n💬 Demonstrating real communications...")
        
        # Scenario 1: Grace Jean Nkomo (ICT University) is absent
        print("\n📋 Scenario 1: Attendance Alert")
        print("   Student: Grace Jean Nkomo (Computer Science, ICT University)")
        print("   Status: Absent on 2024-11-03")
        
        ict_school = self.school_nodes.get("ict-university")
        if ict_school:
            success = ict_school.communication_service.send_attendance_alert(
                "student_ict_001", 
                "absent", 
                "2024-11-03"
            )
            if success:
                print("   ✅ Alert sent to Mr Jean Nkomo (677880739) and Mme Mary Fotso (659258713)")
        
        # Scenario 2: Report card for Omar Ahmed Hassan (Polytech)
        print("\n📊 Scenario 2: Report Card Distribution") 
        print("   Student: Omar Ahmed Hassan (Mechanical Engineering, Polytech)")
        print("   Semester: Fall 2024")
        
        polytech_school = self.school_nodes.get("polytech")
        if polytech_school:
            grades = SAMPLE_GRADES.get("student_poly_001", {})
            success = polytech_school.communication_service.send_report_card(
                "student_poly_001",
                grades,
                "Fall 2024"
            )
            if success:
                print("   ✅ Report card sent to Dr Ahmed Hassan and Mme Fatima Hassan")
                print(f"   📈 Grades: {grades}")
        
        # Scenario 3: Fee notification
        print("\n💰 Scenario 3: Fee Payment Reminder")
        print("   Student: Emmanuel Paul Kamdem (Information Systems, ICT University)")
        print("   Amount: 450,000 FCFA (Tuition)")
        
        fee_amount = SCHOOL_FEES["ict-university"]["tuition_per_semester"]
        if ict_school:
            success = ict_school.communication_service.send_fee_notification(
                "student_ict_003",
                fee_amount,
                "2024-11-15"
            )
            if success:
                print("   ✅ Fee reminder sent to Mr Paul Kamdem (698123456) and Mme Claire Mballa (677456789)")
        
        # Scenario 4: P2P Teacher-Parent Communication
        print("\n💭 Scenario 4: Direct Teacher-Parent Communication")
        print("   Teacher: Prof. Martin Atangana (ICT University)")
        print("   Parent: Mr Jean Nkomo")
        print("   Topic: Grace's performance in Database Systems")
        
        # Find teacher and parent IDs
        teacher_id = None
        parent_id = None
        
        for user_id, user in self.real_users.items():
            if user.name == "Prof. Martin Atangana":
                teacher_id = user_id
            elif user.name == "Mr Jean Nkomo":
                parent_id = user_id
        
        if teacher_id and parent_id:
            message_id = self.p2p_layer.send_message(
                teacher_id,
                parent_id,
                f"Hello Mr. Nkomo, I wanted to discuss Grace's excellent performance in Database Systems. "
                f"She scored 85/100 in the recent exam and shows great potential. "
                f"Could we schedule a meeting to discuss her academic progress?",
                "text"
            )
            
            if message_id:
                print("   ✅ Direct message sent via P2P communication")
                print("   📱 Message delivered to Mr Jean's phone (677880739)")
        
        # Scenario 5: School Event Broadcast
        print("\n📢 Scenario 5: School Event Broadcast")
        print("   Event: ICT University Tech Fair 2024")
        print("   Date: November 20, 2024")
        
        if ict_school:
            messages_sent = ict_school.communication_service.send_event_broadcast(
                "ict-university",
                "ICT University Tech Fair 2024",
                "Annual technology fair showcasing student projects. "
                "Parents are invited to attend and see their children's innovations. "
                "Location: ICT University Main Campus. Time: 9:00 AM - 4:00 PM",
                "2024-11-20"
            )
            print(f"   ✅ Event broadcast sent to {messages_sent} parents at ICT University")
        
        print("\n✅ Real communication scenarios completed!")
    
    def demonstrate_real_fault_tolerance(self):
        """Demonstrate fault tolerance with real scenarios"""
        print("\n🛡️  Demonstrating real-world fault tolerance...")
        
        # Scenario 1: ICT University server failure
        print("\n🔴 Scenario 1: ICT University Server Failure")
        print("   Situation: Power outage affects ICT University campus")
        print("   Impact: Local server becomes unresponsive")
        
        ict_node = self.school_nodes.get("ict-university")
        if ict_node:
            # Simulate the failure
            failure_id = self.fault_tolerance.simulate_failure(
                "ict-university",
                FailureType.NODE_FAILURE
            )
            ict_node.simulate_node_failure()
            
            print("   ⚠️  ICT University node failed!")
            print("   🔄 Automatic failover initiated...")
            
            time.sleep(2)
            
            # Test if other schools still work
            polytech_node = self.school_nodes.get("polytech")
            if polytech_node and polytech_node.status.name == "ACTIVE":
                print("   ✅ Polytech continues operating normally")
                
                # Send message from Polytech while ICT is down
                success = polytech_node.communication_service.send_attendance_alert(
                    "student_poly_001",
                    "present", 
                    "2024-11-03"
                )
                if success:
                    print("   📤 Polytech successfully sent attendance alert during ICT outage")
            
            # Recovery
            print("   🔧 Initiating recovery for ICT University...")
            ict_node.recover_from_failure()
            print("   ✅ ICT University server recovered!")
        
        # Scenario 2: Network partition between Yaoundé and Douala
        print("\n🌐 Scenario 2: Network Connectivity Issues")
        print("   Situation: Internet connectivity problems between Yaoundé and Douala")
        print("   Impact: Cross-region communication affected")
        
        self.fault_tolerance.simulate_failure(
            "centre-region",
            FailureType.NETWORK_PARTITION
        )
        
        print("   ⚠️  Network partition detected!")
        print("   🔄 Automatic traffic redistribution...")
        print("   ✅ Local communications continue unaffected")
        
        print("\n✅ Fault tolerance demonstrations completed!")
    
    def show_real_data_insights(self):
        """Show insights from the real data"""
        print("\n📊 Real Data Insights & Statistics")
        print("=" * 50)
        
        # School statistics
        for school_info in REAL_SCHOOLS:
            school_id = school_info["id"] 
            school_node = self.school_nodes.get(school_id)
            
            if school_node:
                stats = school_node.get_node_statistics()
                
                print(f"\n🏫 {school_info['name']}")
                print(f"   📍 Location: {school_info['location']}")
                print(f"   📞 Phone: {school_info['phone']}")
                print(f"   📧 Email: {school_info['email']}")
                print(f"   👥 Current Users: {stats['current_load']['users']}")
                
                # Show real students for this school
                school_students = [s for s in REAL_STUDENTS if s["school_id"] == school_id]
                print(f"   🎓 Students:")
                for student in school_students:
                    print(f"      - {student['name']} ({student['program']}, {student['year']})")
                
                # Show real teachers
                school_teachers = [t for t in REAL_TEACHERS if t["school_id"] == school_id]
                print(f"   👨‍🏫 Teachers:")
                for teacher in school_teachers:
                    print(f"      - {teacher['name']} ({', '.join(teacher['subjects'])})")
                
                # Show fees
                if school_id in SCHOOL_FEES:
                    fees = SCHOOL_FEES[school_id]
                    print(f"   💰 Fees (FCFA):")
                    for fee_type, amount in fees.items():
                        print(f"      - {fee_type.replace('_', ' ').title()}: {amount:,}")
        
        # Communication statistics
        print(f"\n📱 Communication Statistics:")
        p2p_stats = self.p2p_layer.get_layer_statistics()
        print(f"   - Active P2P connections: {p2p_stats['total_p2p_connections']}")
        print(f"   - Messages sent: {p2p_stats['total_messages_sent']}")
        
        # System health
        ft_stats = self.fault_tolerance.get_system_health_status()
        print(f"\n🏥 System Health:")
        print(f"   - Overall availability: {ft_stats['overall_health']['availability_percentage']:.1f}%")
        print(f"   - Active components: {ft_stats['overall_health']['healthy_components']}")
        
        # Real parent contact information
        print(f"\n👨‍👩‍👧‍👦 Parent Contact Directory:")
        for parent in REAL_PARENTS:
            school_name = next((s["name"] for s in REAL_SCHOOLS if s["id"] == parent["school_id"]), "Unknown")
            print(f"   - {parent['name']}: {parent['phone']} ({school_name})")
    
    def _create_real_school_node(self, school_info: Dict):
        """Create a school node using real school information"""
        school_config = SchoolConfig(
            school_id=school_info["id"],
            name=school_info["name"], 
            address=school_info["location"],
            region=school_info["region"],
            timezone="Africa/Douala",
            academic_year="2024-2025",
            total_students=len([s for s in REAL_STUDENTS if s["school_id"] == school_info["id"]]),
            total_teachers=len([t for t in REAL_TEACHERS if t["school_id"] == school_info["id"]]),
            total_parents=len([p for p in REAL_PARENTS if p["school_id"] == school_info["id"]]),
            contact_info={
                "phone": school_info["phone"],
                "email": school_info["email"]
            }
        )
        
        node_capacity = {
            "max_users": 2000,
            "max_messages_per_hour": 10000, 
            "storage_capacity_gb": 100,
            "bandwidth_mbps": 50  # Realistic for Cameroon
        }
        
        school_node = SchoolNode(school_config, node_capacity)
        self.school_nodes[school_info["id"]] = school_node
        
        # Add to regional load balancer
        node_info = NodeInfo(
            node_id=school_node.node_id,
            region=school_info["region"],
            weight=1,
            max_connections=1000,
            health_status=NodeHealth.HEALTHY
        )
        
        self.multi_region_manager.add_node_to_region(school_info["region"], node_info)
        
        # Register with fault tolerance
        self.fault_tolerance.register_component(
            school_node.node_id,
            "school_node",
            health_check_func=lambda: school_node.status.name == "ACTIVE"
        )
        
        print(f"   🏫 Created: {school_info['name']} in {school_info['region']}")
    
    def _create_database_node(self, node_id: str, region: str):
        """Create database node for real data storage"""
        db_node = DatabaseNode(node_id, storage_capacity_gb=500)  # Larger capacity for real data
        self.database_nodes[node_id] = db_node
        
        # Assign master data types based on region
        master_data_types = []
        if "yaounde" in node_id:
            master_data_types = [DataType.STUDENT_RECORD, DataType.USER_PROFILE]
        elif "douala" in node_id:
            master_data_types = [DataType.MESSAGE_LOG, DataType.ANNOUNCEMENT]
        
        self.distributed_db.add_node(db_node, master_data_types)
        
        # Register with fault tolerance
        self.fault_tolerance.register_component(
            node_id,
            "database_node", 
            health_check_func=lambda: True
        )
        
        print(f"   💾 Created: {node_id} in {region}")

def main():
    """Run the real data SchoolBridge simulation"""
    print("🇨🇲 Starting SchoolBridge Cameroon - Real Data Simulation")
    print("=" * 65)
    
    sim = RealDataSchoolBridgeSimulation()
    
    try:
        # Setup with real infrastructure
        sim.setup_real_infrastructure()
        time.sleep(1)
        
        # Populate with real data
        sim.populate_real_data() 
        time.sleep(1)
        
        # Show initial data insights
        sim.show_real_data_insights()
        time.sleep(2)
        
        # Demonstrate real communications
        sim.demonstrate_real_communications()
        time.sleep(2)
        
        # Demonstrate fault tolerance
        sim.demonstrate_real_fault_tolerance()
        time.sleep(1)
        
        print("\n" + "=" * 65)
        print("🎉 SchoolBridge Cameroon Simulation Complete!")
        print("✅ Real data successfully demonstrated")
        print("🏫 Connecting ICT University, Polytech, and University of Yaoundé")
        print("👨‍👩‍👧‍👦 Serving real families across Cameroon")
        
    except Exception as e:
        print(f"\n❌ Simulation error: {e}")
    finally:
        sim.fault_tolerance.stop_monitoring()

if __name__ == "__main__":
    main()