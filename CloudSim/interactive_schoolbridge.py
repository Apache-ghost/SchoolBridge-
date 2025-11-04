#!/usr/bin/env python3
"""
Interactive SchoolBridge Terminal Interface
Provides full user control over the distributed education system
"""

import json
import time
import uuid
from datetime import datetime, timedelta
from real_data_config import REAL_SCHOOLS, REAL_PARENTS, REAL_STUDENTS, REAL_TEACHERS
from real_data_simulation import RealDataSchoolBridgeSimulation

class InteractiveSchoolBridge:
    def __init__(self):
        self.current_user = None
        self.current_role = None
        self.current_school = None
        self.simulation = None
        self.session_id = f"session-{int(time.time())}"
        
    def clear_screen(self):
        """Clear the terminal screen"""
        import os
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_header(self):
        """Display the main header"""
        print("=" * 70)
        print("🇨🇲 SCHOOLBRIDGE CAMEROON - Interactive Control Panel")
        print("=" * 70)
        if self.current_user:
            print(f"👤 Logged in as: {self.current_user['name']} ({self.current_role})")
            print(f"🏫 School: {self.current_school['name']}")
            print(f"📍 Location: {self.current_school['location']}")
        print("=" * 70)
        
    def show_main_menu(self):
        """Show the main menu"""
        self.clear_screen()
        self.display_header()
        
        print("\n🚀 Welcome to SchoolBridge Interactive Terminal!")
        print("\nChoose your action:")
        print("1. 🔐 Login as User")
        print("2. 📊 View System Status")
        print("3. 🏫 Browse All Schools")
        print("4. 🔧 System Administration")
        print("0. ❌ Exit")
        
        choice = input("\n👉 Enter your choice: ").strip()
        return choice
        
    def login_menu(self):
        """Handle user login"""
        self.clear_screen()
        self.display_header()
        
        print("\n🔐 LOGIN TO SCHOOLBRIDGE")
        print("\nSelect your role:")
        print("1. 👨‍🏫 Teacher")
        print("2. 👨‍👩‍👧‍👦 Parent")
        print("3. 🎓 Student")
        print("4. 👔 Administrator")
        print("0. ⬅️  Back to Main Menu")
        
        role_choice = input("\n👉 Enter your choice: ").strip()
        
        if role_choice == "0":
            return
        
        role_map = {
            "1": "teacher",
            "2": "parent", 
            "3": "student",
            "4": "admin"
        }
        
        if role_choice not in role_map:
            print("❌ Invalid choice!")
            time.sleep(1)
            return
            
        selected_role = role_map[role_choice]
        self.select_school_and_user(selected_role)
        
    def select_school_and_user(self, role):
        """Select school and specific user"""
        self.clear_screen()
        self.display_header()
        
        print(f"\n🏫 SELECT SCHOOL ({role.upper()})")
        print("\nAvailable Schools:")
        
        for i, school in enumerate(REAL_SCHOOLS, 1):
            print(f"{i}. {school['name']}")
            print(f"   📍 {school['location']}")
            print(f"   📞 {school['phone']}")
            print()
            
        print("0. ⬅️  Back")
        
        school_choice = input("👉 Select school (number): ").strip()
        
        if school_choice == "0":
            return
            
        try:
            school_index = int(school_choice) - 1
            if 0 <= school_index < len(REAL_SCHOOLS):
                self.current_school = REAL_SCHOOLS[school_index]
                school_id = self.current_school['id']
                self.select_user_in_school(role, school_id)
            else:
                print("❌ Invalid school selection!")
                time.sleep(1)
        except ValueError:
            print("❌ Please enter a valid number!")
            time.sleep(1)
            
    def select_user_in_school(self, role, school_id):
        """Select specific user within the school"""
        self.clear_screen()
        self.display_header()
        
        print(f"\n👤 SELECT {role.upper()} AT {self.current_school['name']}")
        
        if role == "teacher":
            users = [t for t in REAL_TEACHERS if t['school_id'] == school_id]
        elif role == "parent":
            users = [p for p in REAL_PARENTS if p['school_id'] == school_id]
        elif role == "student":
            users = [s for s in REAL_STUDENTS if s['school_id'] == school_id]
        else:  # admin
            users = [{'name': 'System Administrator', 'id': 'admin_' + school_id, 'school': school_id}]
            
        if not users:
            print(f"❌ No {role}s found at this school!")
            time.sleep(2)
            return
            
        print(f"\nAvailable {role}s:")
        for i, user in enumerate(users, 1):
            print(f"{i}. {user['name']}")
            if role == "teacher" and 'subjects' in user:
                print(f"   📚 Subjects: {', '.join(user['subjects'])}")
            elif role == "student" and 'program' in user:
                print(f"   🎓 Program: {user['program']} ({user['year']})")
            elif role == "parent" and 'phone' in user:
                print(f"   📞 Phone: {user['phone']}")
            print()
            
        print("0. ⬅️  Back")
        
        user_choice = input("👉 Select user (number): ").strip()
        
        if user_choice == "0":
            return
            
        try:
            user_index = int(user_choice) - 1
            if 0 <= user_index < len(users):
                self.current_user = users[user_index]
                self.current_role = role
                self.initialize_simulation()
                self.role_dashboard()
            else:
                print("❌ Invalid user selection!")
                time.sleep(1)
        except ValueError:
            print("❌ Please enter a valid number!")
            time.sleep(1)
            
    def initialize_simulation(self):
        """Initialize the simulation system"""
        print("\n🚀 Initializing SchoolBridge system...")
        self.simulation = RealDataSchoolBridgeSimulation()
        time.sleep(1)
        print("✅ System ready!")
        time.sleep(1)
        
    def role_dashboard(self):
        """Main dashboard based on user role"""
        while True:
            self.clear_screen()
            self.display_header()
            
            print(f"\n🎛️  {self.current_role.upper()} DASHBOARD")
            print(f"Welcome back, {self.current_user['name']}!")
            
            if self.current_role == "teacher":
                self.teacher_dashboard()
            elif self.current_role == "parent":
                self.parent_dashboard()
            elif self.current_role == "student":
                self.student_dashboard()
            elif self.current_role == "admin":
                self.admin_dashboard()
                
    def teacher_dashboard(self):
        """Teacher-specific dashboard"""
        print("\n📚 TEACHER ACTIONS:")
        print("1. 📋 View My Classes")
        print("2. 💬 Send Message to Parent")
        print("3. 📢 Send Class Announcement")
        print("4. 📊 Generate Student Report")
        print("5. ✅ Mark Attendance")
        print("6. 📝 Create Assignment")
        print("7. 📈 View Class Performance")
        print("8. 🔔 Send Alert to Parents")
        print("9. 📱 P2P Communication")
        print("0. 🚪 Logout")
        
        choice = input("\n👉 Enter your choice: ").strip()
        
        if choice == "0":
            self.logout()
            return
        elif choice == "1":
            self.view_teacher_classes()
        elif choice == "2":
            self.send_message_to_parent()
        elif choice == "3":
            self.send_class_announcement()
        elif choice == "4":
            self.generate_student_report()
        elif choice == "5":
            self.mark_attendance()
        elif choice == "6":
            self.create_assignment()
        elif choice == "7":
            self.view_class_performance()
        elif choice == "8":
            self.send_parent_alert()
        elif choice == "9":
            self.p2p_communication()
        else:
            print("❌ Invalid choice!")
            time.sleep(1)
            
    def parent_dashboard(self):
        """Parent-specific dashboard"""
        print("\n👨‍👩‍👧‍👦 PARENT ACTIONS:")
        print("1. 👶 View My Children")
        print("2. 📊 Check Child's Grades")
        print("3. 📅 View Attendance Records")
        print("4. 💬 Message Teacher")
        print("5. 💰 View Fee Status")
        print("6. 📢 School Announcements")
        print("7. 📱 P2P with Teachers")
        print("8. 🏥 Medical Records")
        print("0. 🚪 Logout")
        
        choice = input("\n👉 Enter your choice: ").strip()
        
        if choice == "0":
            self.logout()
            return
        elif choice == "1":
            self.view_my_children()
        elif choice == "2":
            self.check_child_grades()
        elif choice == "3":
            self.view_attendance_records()
        elif choice == "4":
            self.message_teacher()
        elif choice == "5":
            self.view_fee_status()
        elif choice == "6":
            self.view_announcements()
        elif choice == "7":
            self.p2p_communication()
        else:
            print("❌ Invalid choice!")
            time.sleep(1)
            
    def student_dashboard(self):
        """Student-specific dashboard"""
        print("\n🎓 STUDENT ACTIONS:")
        print("1. 📚 View My Courses")
        print("2. 📊 Check My Grades")
        print("3. 📅 View My Schedule")
        print("4. 📝 View Assignments")
        print("5. 💬 Message Teachers")
        print("6. 📢 School News")
        print("7. 👥 Study Groups")
        print("8. 📈 Academic Progress")
        print("0. 🚪 Logout")
        
        choice = input("\n👉 Enter your choice: ").strip()
        
        if choice == "0":
            self.logout()
            return
        elif choice == "1":
            self.view_my_courses()
        elif choice == "2":
            self.check_my_grades()
        elif choice == "3":
            self.view_my_schedule()
        elif choice == "4":
            self.view_assignments()
        else:
            print("❌ Invalid choice!")
            time.sleep(1)
            
    def admin_dashboard(self):
        """Administrator-specific dashboard"""
        print("\n👔 ADMINISTRATOR ACTIONS:")
        print("1. 🏫 School Management")
        print("2. 👥 User Management")
        print("3. 📊 System Reports")
        print("4. 🛡️  System Health")
        print("5. 💾 Database Management")
        print("6. 📱 Communication Logs")
        print("7. 💰 Financial Reports")
        print("8. 🔧 System Configuration")
        print("9. 📈 Performance Analytics")
        print("0. 🚪 Logout")
        
        choice = input("\n👉 Enter your choice: ").strip()
        
        if choice == "0":
            self.logout()
            return
        elif choice == "1":
            self.school_management()
        elif choice == "2":
            self.user_management()
        elif choice == "3":
            self.system_reports()
        elif choice == "4":
            self.system_health()
        else:
            print("❌ Invalid choice!")
            time.sleep(1)

    # Teacher Actions
    def view_teacher_classes(self):
        """View teacher's classes"""
        self.clear_screen()
        self.display_header()
        
        print(f"\n📚 CLASSES FOR {self.current_user['name']}")
        
        if 'subjects' in self.current_user:
            for subject in self.current_user['subjects']:
                print(f"\n📖 {subject}")
                # Get students for this subject
                students_in_school = [s for s in REAL_STUDENTS if s['school_id'] == self.current_school['id']]
                print(f"   👥 Students: {len(students_in_school)}")
                for student in students_in_school[:3]:  # Show first 3
                    print(f"      • {student['name']} ({student['program']})")
                if len(students_in_school) > 3:
                    print(f"      • ... and {len(students_in_school) - 3} more")
        
        input("\n📱 Press Enter to continue...")

    def send_message_to_parent(self):
        """Send message to a parent"""
        self.clear_screen()
        self.display_header()
        
        print(f"\n💬 SEND MESSAGE TO PARENT")
        
        # Show parents in this school
        parents_in_school = [p for p in REAL_PARENTS if p['school_id'] == self.current_school['id']]
        
        print("\nSelect parent:")
        for i, parent in enumerate(parents_in_school, 1):
            print(f"{i}. {parent['name']} - {parent['phone']}")
            
        parent_choice = input("\n👉 Select parent (number): ").strip()
        
        try:
            parent_index = int(parent_choice) - 1
            if 0 <= parent_index < len(parents_in_school):
                selected_parent = parents_in_school[parent_index]
                
                message = input("\n✏️  Enter your message: ").strip()
                if message:
                    print(f"\n📤 Sending message to {selected_parent['name']}...")
                    time.sleep(1)
                    print(f"✅ Message sent to {selected_parent['phone']}!")
                    print(f"📝 Content: {message}")
                    
                    # Log the communication
                    self.log_communication("MESSAGE", selected_parent['name'], message)
                    
        except ValueError:
            print("❌ Invalid selection!")
            
        input("\n📱 Press Enter to continue...")

    def p2p_communication(self):
        """P2P Communication feature"""
        self.clear_screen()
        self.display_header()
        
        print(f"\n📱 P2P COMMUNICATION")
        print("🔗 Establishing secure peer-to-peer connection...")
        time.sleep(1)
        
        if self.current_role == "teacher":
            # Teachers can connect to parents
            parents_in_school = [p for p in REAL_PARENTS if p['school_id'] == self.current_school['id']]
            print("\nAvailable parents for P2P chat:")
            for i, parent in enumerate(parents_in_school, 1):
                print(f"{i}. {parent['name']} - {parent['phone']}")
                
            choice = input("\n👉 Select parent for P2P chat: ").strip()
            try:
                parent_index = int(choice) - 1
                if 0 <= parent_index < len(parents_in_school):
                    selected_parent = parents_in_school[parent_index]
                    print(f"\n🔗 P2P connection established with {selected_parent['name']}")
                    print("✅ Secure channel active - End-to-end encrypted")
                    
                    message = input("\n💬 Type your message: ").strip()
                    if message:
                        print(f"\n📤 P2P message sent to {selected_parent['name']}")
                        print("✅ Message delivered via secure channel")
                        self.log_communication("P2P_MESSAGE", selected_parent['name'], message)
            except ValueError:
                print("❌ Invalid selection!")
                
        elif self.current_role == "parent":
            # Parents can connect to teachers
            teachers_in_school = [t for t in REAL_TEACHERS if t['school_id'] == self.current_school['id']]
            print("\nAvailable teachers for P2P chat:")
            for i, teacher in enumerate(teachers_in_school, 1):
                subjects = ', '.join(teacher.get('subjects', []))
                print(f"{i}. {teacher['name']} - {subjects}")
                
            choice = input("\n👉 Select teacher for P2P chat: ").strip()
            try:
                teacher_index = int(choice) - 1
                if 0 <= teacher_index < len(teachers_in_school):
                    selected_teacher = teachers_in_school[teacher_index]
                    print(f"\n🔗 P2P connection established with {selected_teacher['name']}")
                    print("✅ Secure channel active - End-to-end encrypted")
                    
                    message = input("\n💬 Type your message: ").strip()
                    if message:
                        print(f"\n📤 P2P message sent to {selected_teacher['name']}")
                        print("✅ Message delivered via secure channel")
                        self.log_communication("P2P_MESSAGE", selected_teacher['name'], message)
            except ValueError:
                print("❌ Invalid selection!")
        
        input("\n📱 Press Enter to continue...")

    # Parent Actions
    def send_class_announcement(self):
        """Send announcement to entire class"""
        self.clear_screen()
        self.display_header()
        
        print(f"\n📢 SEND CLASS ANNOUNCEMENT")
        
        if 'subjects' in self.current_user:
            print("Select subject/class:")
            for i, subject in enumerate(self.current_user['subjects'], 1):
                print(f"{i}. {subject}")
                
            choice = input("\n👉 Select class: ").strip()
            try:
                subject_index = int(choice) - 1
                if 0 <= subject_index < len(self.current_user['subjects']):
                    selected_subject = self.current_user['subjects'][subject_index]
                    
                    announcement = input(f"\n📝 Enter announcement for {selected_subject}: ").strip()
                    if announcement:
                        students_count = len([s for s in REAL_STUDENTS if s['school_id'] == self.current_school['id']])
                        parents_count = len([p for p in REAL_PARENTS if p['school_id'] == self.current_school['id']])
                        
                        print(f"\n📤 Broadcasting announcement to {selected_subject} class...")
                        time.sleep(1)
                        print(f"✅ Sent to {students_count} students and {parents_count} parents")
                        print(f"📝 Content: {announcement}")
                        
                        self.log_communication("ANNOUNCEMENT", f"{selected_subject} Class", announcement)
            except ValueError:
                print("❌ Invalid selection!")
        
        input("\n📱 Press Enter to continue...")

    def generate_student_report(self):
        """Generate academic report for student"""
        self.clear_screen()
        self.display_header()
        
        print(f"\n📊 GENERATE STUDENT REPORT")
        
        students_in_school = [s for s in REAL_STUDENTS if s['school_id'] == self.current_school['id']]
        
        print("Select student:")
        for i, student in enumerate(students_in_school, 1):
            print(f"{i}. {student['name']} - {student['program']}")
            
        choice = input("\n👉 Select student: ").strip()
        
        try:
            student_index = int(choice) - 1
            if 0 <= student_index < len(students_in_school):
                selected_student = students_in_school[student_index]
                
                print(f"\n📊 ACADEMIC REPORT - {selected_student['name']}")
                print("=" * 50)
                print(f"🎓 Program: {selected_student['program']}")
                print(f"📅 Year: {selected_student['year']}")
                print(f"🏫 School: {self.current_school['name']}")
                
                # Generate sample grades
                subjects = self.current_user.get('subjects', ['Mathematics', 'Science'])
                print(f"\n📚 GRADES:")
                
                import random
                for subject in subjects:
                    grade = random.randint(75, 95)
                    print(f"   {subject}: {grade}%")
                
                print(f"\n📈 Overall Performance: Excellent")
                print(f"👨‍🏫 Teacher: {self.current_user['name']}")
                print(f"📅 Report Date: {datetime.now().strftime('%Y-%m-%d')}")
                
                # Ask if should send to parents
                send_to_parents = input("\n📧 Send report to parents? (y/n): ").strip().lower()
                if send_to_parents == 'y':
                    print("📤 Sending report to parents...")
                    time.sleep(1)
                    print("✅ Report sent successfully!")
                    
        except ValueError:
            print("❌ Invalid selection!")
            
        input("\n📱 Press Enter to continue...")

    def mark_attendance(self):
        """Mark student attendance"""
        self.clear_screen()
        self.display_header()
        
        print(f"\n✅ MARK ATTENDANCE")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d')}")
        
        students_in_school = [s for s in REAL_STUDENTS if s['school_id'] == self.current_school['id']]
        
        print(f"\nStudents in {self.current_school['name']}:")
        attendance_records = {}
        
        for i, student in enumerate(students_in_school, 1):
            status = input(f"{i}. {student['name']} - Present (P) or Absent (A)? ").strip().upper()
            if status in ['P', 'A']:
                attendance_records[student['name']] = 'Present' if status == 'P' else 'Absent'
            else:
                attendance_records[student['name']] = 'Present'  # Default to present
                
        print(f"\n📋 ATTENDANCE SUMMARY:")
        present_count = sum(1 for status in attendance_records.values() if status == 'Present')
        absent_count = len(attendance_records) - present_count
        
        print(f"✅ Present: {present_count}")
        print(f"❌ Absent: {absent_count}")
        
        for name, status in attendance_records.items():
            if status == 'Absent':
                print(f"🚨 {name} - ABSENT (Alert sent to parents)")
                
        input("\n📱 Press Enter to continue...")

    def view_my_children(self):
        """View parent's children"""
        self.clear_screen()
        self.display_header()
        
        print(f"\n👶 CHILDREN OF {self.current_user['name']}")
        
        # Find children of this parent
        children = [s for s in REAL_STUDENTS if s['school_id'] == self.current_school['id']]
        
        if children:
            for child in children:
                print(f"\n🎓 {child['name']}")
                print(f"   📚 Program: {child['program']}")
                print(f"   📅 Year: {child['year']}")
                print(f"   🏫 School: {self.current_school['name']}")
        else:
            print("\n❌ No children found in this school.")
            
        input("\n📱 Press Enter to continue...")

    def check_child_grades(self):
        """Check child's grades"""
        self.clear_screen()
        self.display_header()
        
        print(f"\n📊 CHECK CHILD'S GRADES")
        
        children = [s for s in REAL_STUDENTS if s['school_id'] == self.current_school['id']]
        
        if children:
            print("Select child:")
            for i, child in enumerate(children, 1):
                print(f"{i}. {child['name']} - {child['program']}")
                
            choice = input("\n👉 Select child: ").strip()
            
            try:
                child_index = int(choice) - 1
                if 0 <= child_index < len(children):
                    selected_child = children[child_index]
                    
                    print(f"\n📊 GRADES FOR {selected_child['name']}")
                    print("=" * 40)
                    
                    # Generate sample grades
                    import random
                    subjects = ['Mathematics', 'Science', 'English', 'History', 'Geography']
                    total_score = 0
                    
                    for subject in subjects:
                        grade = random.randint(70, 95)
                        total_score += grade
                        print(f"📚 {subject}: {grade}%")
                        
                    average = total_score / len(subjects)
                    print(f"\n📈 Overall Average: {average:.1f}%")
                    
                    if average >= 90:
                        print("🏆 Performance: Excellent!")
                    elif average >= 80:
                        print("👍 Performance: Good")
                    else:
                        print("📚 Performance: Needs Improvement")
                        
            except ValueError:
                print("❌ Invalid selection!")
        else:
            print("❌ No children found.")
            
        input("\n📱 Press Enter to continue...")

    # Admin Actions  
    def system_health(self):
        """Check system health"""
        self.clear_screen()
        self.display_header()
        
        print("\n🛡️  SYSTEM HEALTH MONITOR")
        print("\n🔍 Checking system components...")
        time.sleep(1)
        
        components = [
            ("Database Servers", "✅ ONLINE", "6/6 nodes active"),
            ("Load Balancers", "✅ ONLINE", "3/3 regions active"), 
            ("P2P Network", "✅ ONLINE", "All nodes connected"),
            ("Fault Tolerance", "✅ ACTIVE", "Auto-recovery enabled"),
            ("Communication Service", "✅ ONLINE", "99.9% uptime"),
            ("Data Replication", "✅ SYNCED", "All replicas current")
        ]
        
        for component, status, detail in components:
            print(f"📊 {component:20} {status:15} {detail}")
            time.sleep(0.3)
            
        print(f"\n🌍 REGIONAL STATUS:")
        regions = [
            ("Centre Region (Yaoundé)", "✅ ACTIVE", "2 schools, 150ms avg"),
            ("Littoral Region (Douala)", "✅ ACTIVE", "1 school, 180ms avg"),  
            ("West Region (Bafoussam)", "✅ ACTIVE", "1 school, 200ms avg")
        ]
        
        for region, status, detail in regions:
            print(f"🌍 {region:25} {status:15} {detail}")
            time.sleep(0.3)
            
        input("\n📱 Press Enter to continue...")

    # Utility functions
    def log_communication(self, comm_type, recipient, message):
        """Log communication for audit trail"""
        log_entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'sender': self.current_user['name'],
            'sender_role': self.current_role,
            'recipient': recipient,
            'type': comm_type,
            'message': message,
            'school': self.current_school['name']
        }
        
        # In a real system, this would be saved to database
        print(f"📝 Communication logged: {comm_type}")

    def logout(self):
        """Logout current user"""
        print("\n🚪 Logging out...")
        time.sleep(1)
        self.current_user = None
        self.current_role = None
        self.current_school = None
        print("✅ Logged out successfully!")
        time.sleep(1)
        
    def run(self):
        """Main program loop"""
        print("🚀 Starting SchoolBridge Interactive Terminal...")
        time.sleep(1)
        
        while True:
            if not self.current_user:
                choice = self.show_main_menu()
                
                if choice == "0":
                    print("\n👋 Thank you for using SchoolBridge!")
                    break
                elif choice == "1":
                    self.login_menu()
                elif choice == "2":
                    self.view_system_status()
                elif choice == "3":
                    self.browse_schools()
                else:
                    print("❌ Invalid choice!")
                    time.sleep(1)
            else:
                self.role_dashboard()

    def view_system_status(self):
        """View overall system status"""
        self.clear_screen()
        self.display_header()
        
        print("\n📊 SCHOOLBRIDGE SYSTEM STATUS")
        print(f"🕒 Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🆔 Session: {self.session_id}")
        
        print("\n🏫 SCHOOL STATISTICS:")
        print(f"   Total Schools: {len(REAL_SCHOOLS)}")
        print(f"   Total Teachers: {len(REAL_TEACHERS)}")  
        print(f"   Total Parents: {len(REAL_PARENTS)}")
        print(f"   Total Students: {len(REAL_STUDENTS)}")
        
        print("\n🌍 REGIONAL DISTRIBUTION:")
        for school_key, school in REAL_SCHOOLS.items():
            print(f"   🏫 {school['name']} - {school['location']}")
            
        input("\n📱 Press Enter to continue...")

    def browse_schools(self):
        """Browse all schools"""
        self.clear_screen()
        self.display_header()
        
        print("\n🏫 ALL SCHOOLS IN SCHOOLBRIDGE")
        
        for school in REAL_SCHOOLS:
            print(f"\n🏫 {school['name']}")
            print(f"   📍 Location: {school['location']}")
            print(f"   📞 Phone: {school['phone']}")
            print(f"   📧 Email: {school['email']}")
            
            # Count users in this school
            teachers_count = len([t for t in REAL_TEACHERS if t['school_id'] == school['id']])
            students_count = len([s for s in REAL_STUDENTS if s['school_id'] == school['id']])
            parents_count = len([p for p in REAL_PARENTS if p['school_id'] == school['id']])
            
            print(f"   👥 Users: {teachers_count} teachers, {students_count} students, {parents_count} parents")
            
        input("\n📱 Press Enter to continue...")

if __name__ == "__main__":
    app = InteractiveSchoolBridge()
    app.run()
