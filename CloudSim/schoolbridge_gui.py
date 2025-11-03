"""
SchoolBridge GUI - User-Friendly Interface
A comprehensive graphical interface for the SchoolBridge distributed system
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import json

# Import SchoolBridge components
from real_data_simulation import RealDataSchoolBridgeSimulation
from real_data_config import REAL_SCHOOLS, REAL_PARENTS, REAL_STUDENTS, REAL_TEACHERS, SAMPLE_GRADES, SCHOOL_FEES
from communication_service import User, Student, MessageType

class SchoolBridgeGUI:
    """Main GUI Application for SchoolBridge"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🏫 SchoolBridge - Digital Platform for Parent-Teacher Communication")
        self.root.geometry("1200x800")
        self.root.configure(bg="#f0f8ff")
        
        # Initialize the simulation backend
        self.simulation = None
        self.current_user = None
        self.current_role = None
        self.notifications = []
        
        # Create main interface
        self.setup_main_interface()
        self.setup_login_frame()
        
        # Start background simulation
        self.initialize_simulation()
        
        print("🖥️ SchoolBridge GUI initialized")
    
    def setup_main_interface(self):
        """Setup the main application interface"""
        # Title bar
        title_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        title_frame.pack(fill="x", padx=5, pady=5)
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame,
            text="🇨🇲 SchoolBridge Cameroon - Digital Education Platform",
            font=("Arial", 18, "bold"),
            fg="white",
            bg="#2c3e50"
        )
        title_label.pack(expand=True)
        
        # Status bar
        self.status_frame = tk.Frame(self.root, bg="#34495e", height=30)
        self.status_frame.pack(side="bottom", fill="x")
        self.status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            self.status_frame,
            text="🔄 Initializing SchoolBridge system...",
            font=("Arial", 10),
            fg="white",
            bg="#34495e"
        )
        self.status_label.pack(side="left", padx=10, pady=5)
        
        # Notification indicator
        self.notification_label = tk.Label(
            self.status_frame,
            text="📢 Notifications: 0",
            font=("Arial", 10),
            fg="yellow",
            bg="#34495e"
        )
        self.notification_label.pack(side="right", padx=10, pady=5)
        
        # Main content area
        self.main_frame = tk.Frame(self.root, bg="#ecf0f1")
        self.main_frame.pack(fill="both", expand=True, padx=5, pady=5)
    
    def setup_login_frame(self):
        """Setup login interface"""
        self.login_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        self.login_frame.pack(fill="both", expand=True)
        
        # Login container
        login_container = tk.Frame(self.login_frame, bg="white", relief="raised", bd=2)
        login_container.place(relx=0.5, rely=0.5, anchor="center", width=400, height=500)
        
        # Logo/Title
        logo_label = tk.Label(
            login_container,
            text="🏫 SchoolBridge Login",
            font=("Arial", 20, "bold"),
            fg="#2c3e50",
            bg="white"
        )
        logo_label.pack(pady=20)
        
        # School selection
        tk.Label(login_container, text="Select School:", font=("Arial", 12), bg="white").pack(pady=5)
        self.school_var = tk.StringVar()
        school_combo = ttk.Combobox(login_container, textvariable=self.school_var, width=30)
        school_combo['values'] = [school['name'] for school in REAL_SCHOOLS]
        school_combo.pack(pady=5)
        school_combo.set("ICT University")
        
        # Role selection
        tk.Label(login_container, text="Login as:", font=("Arial", 12), bg="white").pack(pady=5)
        self.role_var = tk.StringVar(value="parent")
        
        role_frame = tk.Frame(login_container, bg="white")
        role_frame.pack(pady=10)
        
        tk.Radiobutton(role_frame, text="👨‍👩‍👧‍👦 Parent", variable=self.role_var, 
                      value="parent", font=("Arial", 10), bg="white").pack(side="left", padx=10)
        tk.Radiobutton(role_frame, text="👨‍🏫 Teacher", variable=self.role_var, 
                      value="teacher", font=("Arial", 10), bg="white").pack(side="left", padx=10)
        tk.Radiobutton(role_frame, text="👨‍💼 Admin", variable=self.role_var, 
                      value="admin", font=("Arial", 10), bg="white").pack(side="left", padx=10)
        
        # User selection (will be populated based on role)
        tk.Label(login_container, text="Select User:", font=("Arial", 12), bg="white").pack(pady=5)
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(login_container, textvariable=self.user_var, width=30)
        self.user_combo.pack(pady=5)
        
        # Update user list when role changes
        def update_users(*args):
            self.update_user_list()
        
        self.role_var.trace('w', update_users)
        self.school_var.trace('w', update_users)
        
        # Login button
        login_btn = tk.Button(
            login_container,
            text="🔑 Login to SchoolBridge",
            font=("Arial", 12, "bold"),
            bg="#3498db",
            fg="white",
            command=self.login,
            width=25,
            height=2
        )
        login_btn.pack(pady=20)
        
        # System info
        info_text = tk.Text(login_container, height=6, width=45, font=("Arial", 9))
        info_text.pack(pady=10)
        info_text.insert("1.0", "🇨🇲 Welcome to SchoolBridge Cameroon!\n\n"
                               "Real Schools Connected:\n"
                               "• ICT University (Yaoundé)\n"
                               "• Polytech Cameroon (Douala)\n"
                               "• University of Yaoundé I\n\n"
                               "Select your school, role, and user to begin.")
        info_text.config(state="disabled")
        
        # Initialize user list
        self.update_user_list()
    
    def update_user_list(self):
        """Update user dropdown based on selected school and role"""
        school_name = self.school_var.get()
        role = self.role_var.get()
        
        # Find school ID
        school_id = None
        for school in REAL_SCHOOLS:
            if school['name'] == school_name:
                school_id = school['id']
                break
        
        if not school_id:
            return
        
        users = []
        if role == "parent":
            users = [p['name'] for p in REAL_PARENTS if p['school_id'] == school_id]
        elif role == "teacher":
            users = [t['name'] for t in REAL_TEACHERS if t['school_id'] == school_id]
        elif role == "admin":
            users = ["System Administrator", "School Administrator"]
        
        self.user_combo['values'] = users
        if users:
            self.user_combo.set(users[0])
    
    def login(self):
        """Handle user login"""
        school = self.school_var.get()
        role = self.role_var.get() 
        user = self.user_var.get()
        
        if not all([school, role, user]):
            messagebox.showerror("Login Error", "Please select school, role, and user")
            return
        
        self.current_user = user
        self.current_role = role
        
        # Hide login frame
        self.login_frame.destroy()
        
        # Show main dashboard
        self.show_dashboard()
        
        self.status_label.config(text=f"✅ Logged in as {user} ({role}) - {school}")
        
        messagebox.showinfo("Login Success", f"Welcome to SchoolBridge, {user}!")
    
    def show_dashboard(self):
        """Show role-specific dashboard"""
        if self.current_role == "parent":
            self.show_parent_dashboard()
        elif self.current_role == "teacher":
            self.show_teacher_dashboard()
        elif self.current_role == "admin":
            self.show_admin_dashboard()
    
    def show_parent_dashboard(self):
        """Show parent dashboard"""
        dashboard_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        dashboard_frame.pack(fill="both", expand=True)
        
        # Welcome header
        header = tk.Label(
            dashboard_frame,
            text=f"👨‍👩‍👧‍👦 Welcome, {self.current_user}!",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        header.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(dashboard_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Children tab
        children_frame = tk.Frame(notebook, bg="white")
        notebook.add(children_frame, text="👧👦 My Children")
        self.create_children_tab(children_frame)
        
        # Messages tab
        messages_frame = tk.Frame(notebook, bg="white")
        notebook.add(messages_frame, text="💬 Messages")
        self.create_messages_tab(messages_frame)
        
        # Notifications tab
        notifications_frame = tk.Frame(notebook, bg="white")
        notebook.add(notifications_frame, text="🔔 Notifications")
        self.create_notifications_tab(notifications_frame)
        
        # Chat tab
        chat_frame = tk.Frame(notebook, bg="white")
        notebook.add(chat_frame, text="💭 Chat with Teachers")
        self.create_chat_tab(chat_frame)
    
    def create_children_tab(self, parent_frame):
        """Create children information tab for parents"""
        # Find children for current parent
        parent_info = None
        for parent in REAL_PARENTS:
            if parent['name'] == self.current_user:
                parent_info = parent
                break
        
        if not parent_info:
            tk.Label(parent_frame, text="No children found", bg="white").pack(pady=20)
            return
        
        # Children list
        children_list = tk.Frame(parent_frame, bg="white")
        children_list.pack(fill="both", expand=True, padx=20, pady=20)
        
        for child_id in parent_info['children']:
            child_info = None
            for student in REAL_STUDENTS:
                if student['student_id'] == child_id:
                    child_info = student
                    break
            
            if child_info:
                self.create_child_card(children_list, child_info)
    
    def create_child_card(self, parent, child_info):
        """Create a card showing child information"""
        card = tk.LabelFrame(
            parent,
            text=f"🎓 {child_info['name']}",
            font=("Arial", 12, "bold"),
            bg="white",
            relief="groove",
            bd=2
        )
        card.pack(fill="x", pady=10)
        
        # Child details
        details_frame = tk.Frame(card, bg="white")
        details_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(details_frame, text=f"Program: {child_info['program']}", 
                font=("Arial", 10), bg="white").pack(anchor="w")
        tk.Label(details_frame, text=f"Year: {child_info['year']}", 
                font=("Arial", 10), bg="white").pack(anchor="w")
        
        # Grades
        grades = SAMPLE_GRADES.get(child_info['student_id'], {})
        if grades:
            tk.Label(details_frame, text="📊 Recent Grades:", 
                    font=("Arial", 10, "bold"), bg="white").pack(anchor="w", pady=(10,0))
            
            for subject, grade in grades.items():
                color = "green" if grade >= 80 else "orange" if grade >= 60 else "red"
                tk.Label(details_frame, text=f"  • {subject}: {grade}/100", 
                        font=("Arial", 10), fg=color, bg="white").pack(anchor="w")
        
        # Action buttons
        btn_frame = tk.Frame(card, bg="white")
        btn_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Button(btn_frame, text="📋 View Full Report", 
                 command=lambda: self.view_full_report(child_info),
                 bg="#3498db", fg="white").pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="💬 Contact Teacher", 
                 command=lambda: self.contact_teacher(child_info),
                 bg="#27ae60", fg="white").pack(side="left", padx=5)
    
    def create_messages_tab(self, parent_frame):
        """Create messages tab"""
        messages_frame = scrolledtext.ScrolledText(
            parent_frame,
            width=80,
            height=20,
            font=("Arial", 10),
            bg="white"
        )
        messages_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Sample messages
        sample_messages = [
            "📢 2024-11-03 09:30: Grace Jean Nkomo was marked absent today.",
            "📊 2024-11-02 15:45: Report card available for David Jean Nkomo.",
            "💰 2024-11-01 10:00: Fee payment reminder: 450,000 FCFA due Nov 15.",
            "📅 2024-10-30 14:20: Parent-Teacher meeting scheduled for Nov 10.",
            "🎉 2024-10-28 11:15: ICT University Tech Fair - Nov 20, 9AM-4PM."
        ]
        
        for message in sample_messages:
            messages_frame.insert("end", message + "\n\n")
        
        messages_frame.config(state="disabled")
    
    def create_notifications_tab(self, parent_frame):
        """Create notifications tab"""
        # Notification controls
        control_frame = tk.Frame(parent_frame, bg="white")
        control_frame.pack(fill="x", padx=20, pady=10)
        
        tk.Label(control_frame, text="🔔 Real-time Notifications", 
                font=("Arial", 12, "bold"), bg="white").pack(side="left")
        
        refresh_btn = tk.Button(
            control_frame,
            text="🔄 Refresh",
            command=self.refresh_notifications,
            bg="#3498db",
            fg="white"
        )
        refresh_btn.pack(side="right")
        
        # Notifications list
        self.notifications_listbox = tk.Listbox(
            parent_frame,
            font=("Arial", 10),
            height=15,
            bg="white"
        )
        self.notifications_listbox.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Add sample notifications
        sample_notifications = [
            "🟢 System Online - All schools connected",
            "📱 New message from Prof. Martin Atangana",
            "⚠️ ICT University server maintenance scheduled",
            "✅ Fee payment confirmed for David Jean Nkomo",
            "📊 Monthly report available for download"
        ]
        
        for notification in sample_notifications:
            self.notifications_listbox.insert("end", notification)
    
    def create_chat_tab(self, parent_frame):
        """Create chat tab for teacher communication"""
        # Chat interface
        chat_frame = tk.Frame(parent_frame, bg="white")
        chat_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Teacher selection
        teacher_frame = tk.Frame(chat_frame, bg="white")
        teacher_frame.pack(fill="x", pady=10)
        
        tk.Label(teacher_frame, text="👨‍🏫 Select Teacher:", 
                font=("Arial", 11, "bold"), bg="white").pack(side="left")
        
        teacher_var = tk.StringVar()
        teacher_combo = ttk.Combobox(teacher_frame, textvariable=teacher_var, width=25)
        teacher_combo['values'] = [t['name'] for t in REAL_TEACHERS]
        teacher_combo.pack(side="left", padx=10)
        teacher_combo.set("Prof. Martin Atangana")
        
        # Chat display
        self.chat_display = scrolledtext.ScrolledText(
            chat_frame,
            height=15,
            font=("Arial", 10),
            bg="#f8f9fa"
        )
        self.chat_display.pack(fill="both", expand=True, pady=10)
        
        # Sample chat history
        chat_history = [
            "Prof. Martin Atangana: Hello Mr. Nkomo, Grace is doing excellent in Database Systems!",
            "You: That's wonderful to hear! How is her attendance?",
            "Prof. Martin Atangana: Perfect attendance this month. She's very engaged.",
            "You: Thank you for the update. Any areas for improvement?",
            "Prof. Martin Atangana: She could work on her SQL optimization skills."
        ]
        
        for message in chat_history:
            self.chat_display.insert("end", message + "\n\n")
        
        # Message input
        input_frame = tk.Frame(chat_frame, bg="white")
        input_frame.pack(fill="x", pady=10)
        
        self.message_entry = tk.Entry(input_frame, font=("Arial", 10), width=60)
        self.message_entry.pack(side="left", padx=(0, 10))
        
        send_btn = tk.Button(
            input_frame,
            text="📤 Send",
            command=lambda: self.send_message(teacher_var.get()),
            bg="#27ae60",
            fg="white"
        )
        send_btn.pack(side="right")
        
        # Bind Enter key
        self.message_entry.bind('<Return>', lambda e: self.send_message(teacher_var.get()))
    
    def show_teacher_dashboard(self):
        """Show teacher dashboard"""
        dashboard_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        dashboard_frame.pack(fill="both", expand=True)
        
        # Welcome header
        header = tk.Label(
            dashboard_frame,
            text=f"👨‍🏫 Welcome, {self.current_user}!",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        header.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(dashboard_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Students tab
        students_frame = tk.Frame(notebook, bg="white")
        notebook.add(students_frame, text="🎓 My Students")
        self.create_teacher_students_tab(students_frame)
        
        # Attendance tab
        attendance_frame = tk.Frame(notebook, bg="white")
        notebook.add(attendance_frame, text="📋 Attendance")
        self.create_attendance_tab(attendance_frame)
        
        # Grades tab
        grades_frame = tk.Frame(notebook, bg="white")
        notebook.add(grades_frame, text="📊 Grades")
        self.create_grades_tab(grades_frame)
        
        # Communications tab
        comm_frame = tk.Frame(notebook, bg="white")
        notebook.add(comm_frame, text="💬 Communications")
        self.create_teacher_comm_tab(comm_frame)
    
    def create_teacher_students_tab(self, parent_frame):
        """Create students tab for teachers"""
        # Find teacher's school
        teacher_school = None
        for teacher in REAL_TEACHERS:
            if teacher['name'] == self.current_user:
                teacher_school = teacher['school_id']
                break
        
        if not teacher_school:
            tk.Label(parent_frame, text="No students found", bg="white").pack(pady=20)
            return
        
        # Students list
        students_frame = tk.Frame(parent_frame, bg="white")
        students_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        tk.Label(students_frame, text="👥 Your Students", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        # Student cards
        for student in REAL_STUDENTS:
            if student['school_id'] == teacher_school:
                self.create_teacher_student_card(students_frame, student)
    
    def create_teacher_student_card(self, parent, student_info):
        """Create student card for teachers"""
        card = tk.LabelFrame(
            parent,
            text=f"🎓 {student_info['name']} - {student_info['program']}",
            font=("Arial", 11, "bold"),
            bg="white",
            relief="groove"
        )
        card.pack(fill="x", pady=5)
        
        card_content = tk.Frame(card, bg="white")
        card_content.pack(fill="x", padx=10, pady=5)
        
        # Student info
        tk.Label(card_content, text=f"Year: {student_info['year']}", 
                bg="white").pack(side="left", padx=10)
        
        # Action buttons
        btn_frame = tk.Frame(card_content, bg="white")
        btn_frame.pack(side="right")
        
        tk.Button(btn_frame, text="📋 Mark Attendance", 
                 command=lambda: self.mark_attendance(student_info),
                 bg="#3498db", fg="white", font=("Arial", 8)).pack(side="left", padx=2)
        
        tk.Button(btn_frame, text="📊 Enter Grades", 
                 command=lambda: self.enter_grades(student_info),
                 bg="#e67e22", fg="white", font=("Arial", 8)).pack(side="left", padx=2)
        
        tk.Button(btn_frame, text="💬 Contact Parents", 
                 command=lambda: self.contact_parents(student_info),
                 bg="#27ae60", fg="white", font=("Arial", 8)).pack(side="left", padx=2)
    
    def create_attendance_tab(self, parent_frame):
        """Create attendance management tab"""
        att_frame = tk.Frame(parent_frame, bg="white")
        att_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(att_frame, text="📋 Attendance Management", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        # Date selection
        date_frame = tk.Frame(att_frame, bg="white")
        date_frame.pack(fill="x", pady=10)
        
        tk.Label(date_frame, text="Date:", bg="white").pack(side="left")
        date_entry = tk.Entry(date_frame, width=15)
        date_entry.pack(side="left", padx=10)
        date_entry.insert(0, datetime.now().strftime("%Y-%m-%d"))
        
        # Quick actions
        quick_frame = tk.Frame(att_frame, bg="white")
        quick_frame.pack(fill="x", pady=10)
        
        tk.Button(quick_frame, text="✅ Mark All Present", 
                 command=self.mark_all_present,
                 bg="#27ae60", fg="white").pack(side="left", padx=5)
        
        tk.Button(quick_frame, text="📤 Send Alerts", 
                 command=self.send_attendance_alerts,
                 bg="#e74c3c", fg="white").pack(side="left", padx=5)
        
        # Attendance list (sample)
        att_list = tk.Frame(att_frame, bg="white")
        att_list.pack(fill="both", expand=True, pady=10)
        
        # Sample attendance entries
        students = ["Grace Jean Nkomo", "David Jean Nkomo", "Emmanuel Paul Kamdem"]
        for i, student in enumerate(students):
            row = tk.Frame(att_list, bg="white", relief="groove", bd=1)
            row.pack(fill="x", pady=2)
            
            tk.Label(row, text=student, bg="white", width=25, anchor="w").pack(side="left", padx=10)
            
            status_var = tk.StringVar(value="present")
            tk.Radiobutton(row, text="Present", variable=status_var, value="present", 
                          bg="white").pack(side="left", padx=5)
            tk.Radiobutton(row, text="Absent", variable=status_var, value="absent", 
                          bg="white").pack(side="left", padx=5)
            tk.Radiobutton(row, text="Late", variable=status_var, value="late", 
                          bg="white").pack(side="left", padx=5)
    
    def create_grades_tab(self, parent_frame):
        """Create grades management tab"""
        grades_frame = tk.Frame(parent_frame, bg="white")
        grades_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(grades_frame, text="📊 Grade Management", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        # Subject selection
        subject_frame = tk.Frame(grades_frame, bg="white")
        subject_frame.pack(fill="x", pady=10)
        
        tk.Label(subject_frame, text="Subject:", bg="white").pack(side="left")
        subject_var = tk.StringVar()
        subject_combo = ttk.Combobox(subject_frame, textvariable=subject_var)
        subject_combo['values'] = ["Database Systems", "Programming", "Mathematics", "Network Security"]
        subject_combo.pack(side="left", padx=10)
        subject_combo.set("Database Systems")
        
        # Assessment type
        tk.Label(subject_frame, text="Assessment:", bg="white").pack(side="left", padx=(20,0))
        assessment_var = tk.StringVar()
        assessment_combo = ttk.Combobox(subject_frame, textvariable=assessment_var)
        assessment_combo['values'] = ["Midterm Exam", "Final Exam", "Assignment", "Quiz", "Project"]
        assessment_combo.pack(side="left", padx=10)
        assessment_combo.set("Midterm Exam")
        
        # Action buttons
        action_frame = tk.Frame(grades_frame, bg="white")
        action_frame.pack(fill="x", pady=10)
        
        tk.Button(action_frame, text="📊 Enter Grades", 
                 command=self.open_grade_entry,
                 bg="#3498db", fg="white").pack(side="left", padx=5)
        
        tk.Button(action_frame, text="📤 Send Report Cards", 
                 command=self.send_report_cards,
                 bg="#27ae60", fg="white").pack(side="left", padx=5)
        
        # Recent grades display
        recent_frame = tk.LabelFrame(grades_frame, text="Recent Grades", bg="white")
        recent_frame.pack(fill="both", expand=True, pady=10)
        
        # Sample grades display
        sample_text = """
Grace Jean Nkomo - Database Systems: 85/100 (Excellent)
David Jean Nkomo - Programming: 78/100 (Good)  
Emmanuel Paul Kamdem - Mathematics: 92/100 (Outstanding)
        """
        
        grades_display = tk.Text(recent_frame, height=10, font=("Arial", 10), bg="white")
        grades_display.pack(fill="both", expand=True, padx=10, pady=10)
        grades_display.insert("1.0", sample_text)
        grades_display.config(state="disabled")
    
    def create_teacher_comm_tab(self, parent_frame):
        """Create teacher communications tab"""
        comm_frame = tk.Frame(parent_frame, bg="white")
        comm_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(comm_frame, text="💬 Parent Communications", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        # Quick message buttons
        quick_frame = tk.Frame(comm_frame, bg="white")
        quick_frame.pack(fill="x", pady=10)
        
        tk.Button(quick_frame, text="📢 Send Announcement", 
                 command=self.send_announcement,
                 bg="#9b59b6", fg="white").pack(side="left", padx=5)
        
        tk.Button(quick_frame, text="📅 Schedule Meeting", 
                 command=self.schedule_meeting,
                 bg="#f39c12", fg="white").pack(side="left", padx=5)
        
        tk.Button(quick_frame, text="💰 Send Fee Notice", 
                 command=self.send_fee_notice,
                 bg="#e74c3c", fg="white").pack(side="left", padx=5)
        
        # Message composition
        compose_frame = tk.LabelFrame(comm_frame, text="Compose Message", bg="white")
        compose_frame.pack(fill="both", expand=True, pady=10)
        
        # Recipients
        recip_frame = tk.Frame(compose_frame, bg="white")
        recip_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(recip_frame, text="To:", bg="white").pack(side="left")
        recipient_var = tk.StringVar()
        recipient_combo = ttk.Combobox(recip_frame, textvariable=recipient_var, width=30)
        recipient_combo['values'] = ["Mr Jean Nkomo", "Mme Mary Fotso", "All Parents", "Selected Parents"]
        recipient_combo.pack(side="left", padx=10)
        
        # Subject
        subject_frame = tk.Frame(compose_frame, bg="white")
        subject_frame.pack(fill="x", padx=10, pady=5)
        
        tk.Label(subject_frame, text="Subject:", bg="white").pack(side="left")
        subject_entry = tk.Entry(subject_frame, width=50)
        subject_entry.pack(side="left", padx=10)
        
        # Message body
        tk.Label(compose_frame, text="Message:", bg="white").pack(anchor="w", padx=10, pady=5)
        message_text = scrolledtext.ScrolledText(compose_frame, height=8, font=("Arial", 10))
        message_text.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Send button
        tk.Button(compose_frame, text="📤 Send Message", 
                 command=lambda: self.send_teacher_message(
                     recipient_var.get(), subject_entry.get(), message_text.get("1.0", "end")
                 ),
                 bg="#27ae60", fg="white", font=("Arial", 11, "bold")).pack(pady=10)
    
    def show_admin_dashboard(self):
        """Show administrator dashboard"""
        dashboard_frame = tk.Frame(self.main_frame, bg="#ecf0f1")
        dashboard_frame.pack(fill="both", expand=True)
        
        # Welcome header
        header = tk.Label(
            dashboard_frame,
            text=f"👨‍💼 Administrator Dashboard",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1",
            fg="#2c3e50"
        )
        header.pack(pady=10)
        
        # Create notebook for tabs
        notebook = ttk.Notebook(dashboard_frame)
        notebook.pack(fill="both", expand=True, padx=10, pady=5)
        
        # System Overview tab
        overview_frame = tk.Frame(notebook, bg="white")
        notebook.add(overview_frame, text="📊 System Overview")
        self.create_system_overview_tab(overview_frame)
        
        # Schools Management tab
        schools_frame = tk.Frame(notebook, bg="white")
        notebook.add(schools_frame, text="🏫 Schools")
        self.create_schools_management_tab(schools_frame)
        
        # Users Management tab
        users_frame = tk.Frame(notebook, bg="white")
        notebook.add(users_frame, text="👥 Users")
        self.create_users_management_tab(users_frame)
        
        # System Health tab
        health_frame = tk.Frame(notebook, bg="white")
        notebook.add(health_frame, text="🔧 System Health")
        self.create_system_health_tab(health_frame)
    
    def create_system_overview_tab(self, parent_frame):
        """Create system overview tab for admins"""
        overview_frame = tk.Frame(parent_frame, bg="white")
        overview_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Statistics cards
        stats_frame = tk.Frame(overview_frame, bg="white")
        stats_frame.pack(fill="x", pady=20)
        
        # Schools card
        schools_card = tk.LabelFrame(stats_frame, text="🏫 Schools", font=("Arial", 11, "bold"), bg="#3498db", fg="white")
        schools_card.pack(side="left", fill="both", expand=True, padx=5)
        
        tk.Label(schools_card, text="3", font=("Arial", 24, "bold"), bg="#3498db", fg="white").pack(pady=10)
        tk.Label(schools_card, text="Connected", font=("Arial", 10), bg="#3498db", fg="white").pack()
        
        # Users card
        users_card = tk.LabelFrame(stats_frame, text="👥 Users", font=("Arial", 11, "bold"), bg="#27ae60", fg="white")
        users_card.pack(side="left", fill="both", expand=True, padx=5)
        
        tk.Label(users_card, text="27", font=("Arial", 24, "bold"), bg="#27ae60", fg="white").pack(pady=10)
        tk.Label(users_card, text="Active", font=("Arial", 10), bg="#27ae60", fg="white").pack()
        
        # Messages card
        messages_card = tk.LabelFrame(stats_frame, text="💬 Messages", font=("Arial", 11, "bold"), bg="#e74c3c", fg="white")
        messages_card.pack(side="left", fill="both", expand=True, padx=5)
        
        tk.Label(messages_card, text="1,847", font=("Arial", 24, "bold"), bg="#e74c3c", fg="white").pack(pady=10)
        tk.Label(messages_card, text="This Month", font=("Arial", 10), bg="#e74c3c", fg="white").pack()
        
        # System status
        status_frame = tk.LabelFrame(overview_frame, text="🔧 System Status", font=("Arial", 12, "bold"), bg="white")
        status_frame.pack(fill="both", expand=True, pady=20)
        
        status_text = tk.Text(status_frame, height=15, font=("Arial", 10), bg="white")
        status_text.pack(fill="both", expand=True, padx=10, pady=10)
        
        system_info = """🟢 All Systems Operational

📍 Regional Status:
  • Centre Region (Yaoundé): ✅ Online - 45ms latency
  • Littoral Region (Douala): ✅ Online - 52ms latency  
  • West Region (Bafoussam): ✅ Online - 68ms latency

🏫 School Connectivity:
  • ICT University: ✅ Active - 1,245 users
  • Polytech Cameroon: ✅ Active - 987 users
  • University Yaoundé I: ✅ Active - 543 users

💾 Database Status:
  • Primary Nodes: 6/6 Online
  • Data Replication: ✅ Synchronized
  • Backup Status: ✅ Up to date

📱 Communication Services:
  • P2P Messaging: ✅ Operational
  • Notifications: ✅ Delivered (98.7% success rate)
  • Attendance Alerts: ✅ Active
  • Report Cards: ✅ Distributed

🛡️ Security & Performance:
  • Load Balancer: ✅ Optimal distribution
  • Fault Tolerance: ✅ All circuits healthy
  • Average Response Time: 234ms
  • System Uptime: 99.94%
        """
        
        status_text.insert("1.0", system_info)
        status_text.config(state="disabled")
    
    def create_schools_management_tab(self, parent_frame):
        """Create schools management tab"""
        schools_frame = tk.Frame(parent_frame, bg="white")
        schools_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(schools_frame, text="🏫 Schools Management", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        # Schools list with management options
        for school in REAL_SCHOOLS:
            school_card = tk.LabelFrame(
                schools_frame,
                text=f"🏫 {school['name']}",
                font=("Arial", 11, "bold"),
                bg="white"
            )
            school_card.pack(fill="x", pady=10)
            
            info_frame = tk.Frame(school_card, bg="white")
            info_frame.pack(fill="x", padx=10, pady=10)
            
            # School info
            details_frame = tk.Frame(info_frame, bg="white")
            details_frame.pack(side="left", fill="both", expand=True)
            
            tk.Label(details_frame, text=f"📍 {school['location']}", bg="white").pack(anchor="w")
            tk.Label(details_frame, text=f"📞 {school['phone']}", bg="white").pack(anchor="w")
            tk.Label(details_frame, text=f"📧 {school['email']}", bg="white").pack(anchor="w")
            
            # Management buttons
            btn_frame = tk.Frame(info_frame, bg="white")
            btn_frame.pack(side="right")
            
            tk.Button(btn_frame, text="⚙️ Configure", bg="#3498db", fg="white", 
                     command=lambda s=school: self.configure_school(s)).pack(pady=2)
            tk.Button(btn_frame, text="📊 Statistics", bg="#27ae60", fg="white",
                     command=lambda s=school: self.view_school_stats(s)).pack(pady=2)
            tk.Button(btn_frame, text="🔧 Maintenance", bg="#f39c12", fg="white",
                     command=lambda s=school: self.school_maintenance(s)).pack(pady=2)
    
    def create_users_management_tab(self, parent_frame):
        """Create users management tab"""
        users_frame = tk.Frame(parent_frame, bg="white")
        users_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(users_frame, text="👥 User Management", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        # User statistics by role
        stats_frame = tk.Frame(users_frame, bg="white")
        stats_frame.pack(fill="x", pady=10)
        
        roles_info = [
            ("👨‍🏫 Teachers", len(REAL_TEACHERS), "#3498db"),
            ("👨‍👩‍👧‍👦 Parents", len(REAL_PARENTS), "#27ae60"),  
            ("🎓 Students", len(REAL_STUDENTS), "#e74c3c")
        ]
        
        for role_name, count, color in roles_info:
            role_card = tk.Frame(stats_frame, bg=color, relief="raised", bd=2)
            role_card.pack(side="left", fill="both", expand=True, padx=5)
            
            tk.Label(role_card, text=role_name, font=("Arial", 11, "bold"), 
                    bg=color, fg="white").pack(pady=5)
            tk.Label(role_card, text=str(count), font=("Arial", 20, "bold"), 
                    bg=color, fg="white").pack(pady=5)
        
        # User actions
        actions_frame = tk.Frame(users_frame, bg="white")
        actions_frame.pack(fill="x", pady=20)
        
        tk.Button(actions_frame, text="➕ Add User", bg="#2ecc71", fg="white",
                 command=self.add_user).pack(side="left", padx=5)
        tk.Button(actions_frame, text="✏️ Edit User", bg="#f39c12", fg="white",
                 command=self.edit_user).pack(side="left", padx=5)
        tk.Button(actions_frame, text="🗑️ Remove User", bg="#e74c3c", fg="white",
                 command=self.remove_user).pack(side="left", padx=5)
        tk.Button(actions_frame, text="📊 User Reports", bg="#9b59b6", fg="white",
                 command=self.generate_user_reports).pack(side="left", padx=5)
    
    def create_system_health_tab(self, parent_frame):
        """Create system health monitoring tab"""
        health_frame = tk.Frame(parent_frame, bg="white")
        health_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        tk.Label(health_frame, text="🔧 System Health Monitor", 
                font=("Arial", 14, "bold"), bg="white").pack(pady=10)
        
        # Health indicators
        indicators_frame = tk.Frame(health_frame, bg="white")
        indicators_frame.pack(fill="x", pady=10)
        
        health_items = [
            ("🟢 Database Cluster", "Healthy", "#27ae60"),
            ("🟢 Communication Services", "Online", "#27ae60"),
            ("🟡 Load Balancer", "Warning: High Load", "#f39c12"),
            ("🟢 P2P Network", "Optimal", "#27ae60"),
            ("🟢 Fault Tolerance", "Active", "#27ae60")
        ]
        
        for indicator, status, color in health_items:
            item_frame = tk.Frame(indicators_frame, bg="white", relief="groove", bd=1)
            item_frame.pack(fill="x", pady=2)
            
            tk.Label(item_frame, text=indicator, font=("Arial", 11), 
                    bg="white", width=30, anchor="w").pack(side="left", padx=10)
            tk.Label(item_frame, text=status, font=("Arial", 11, "bold"), 
                    fg=color, bg="white").pack(side="right", padx=10)
        
        # System actions
        actions_frame = tk.Frame(health_frame, bg="white")
        actions_frame.pack(fill="x", pady=20)
        
        tk.Button(actions_frame, text="🔄 Refresh Status", bg="#3498db", fg="white",
                 command=self.refresh_system_status).pack(side="left", padx=5)
        tk.Button(actions_frame, text="🛠️ Run Diagnostics", bg="#e67e22", fg="white",
                 command=self.run_diagnostics).pack(side="left", padx=5)
        tk.Button(actions_frame, text="📋 Generate Report", bg="#9b59b6", fg="white",
                 command=self.generate_health_report).pack(side="left", padx=5)
    
    def initialize_simulation(self):
        """Initialize the SchoolBridge simulation in background"""
        def init_sim():
            try:
                self.simulation = RealDataSchoolBridgeSimulation()
                self.simulation.setup_real_infrastructure()
                self.simulation.populate_real_data()
                
                self.root.after(0, lambda: self.status_label.config(
                    text="✅ SchoolBridge system ready - All schools connected"
                ))
            except Exception as e:
                self.root.after(0, lambda: self.status_label.config(
                    text=f"❌ System initialization failed: {str(e)}"
                ))
        
        # Start initialization in background thread
        init_thread = threading.Thread(target=init_sim, daemon=True)
        init_thread.start()
    
    # Event handlers (placeholder implementations)
    def view_full_report(self, child_info):
        """View full academic report for child"""
        messagebox.showinfo("Full Report", 
                           f"Opening full academic report for {child_info['name']}\n\n"
                           f"Program: {child_info['program']}\n"
                           f"Year: {child_info['year']}\n"
                           f"Overall Performance: Excellent")
    
    def contact_teacher(self, child_info):
        """Contact teacher about child"""
        messagebox.showinfo("Contact Teacher", 
                           f"Opening chat with {child_info['name']}'s teachers.\n\n"
                           "This will open the P2P communication channel.")
    
    def refresh_notifications(self):
        """Refresh notifications list"""
        # Add new notification
        new_notification = f"🕐 {datetime.now().strftime('%H:%M')} - System status update"
        self.notifications_listbox.insert("end", new_notification)
        self.notification_label.config(text=f"📢 Notifications: {self.notifications_listbox.size()}")
    
    def send_message(self, teacher_name):
        """Send message to teacher"""
        message = self.message_entry.get()
        if message:
            # Add to chat display
            timestamp = datetime.now().strftime("%H:%M")
            self.chat_display.insert("end", f"You ({timestamp}): {message}\n\n")
            self.message_entry.delete(0, "end")
            
            # Auto-reply simulation
            self.root.after(2000, lambda: self.simulate_teacher_reply(teacher_name))
    
    def simulate_teacher_reply(self, teacher_name):
        """Simulate teacher reply"""
        replies = [
            "Thank you for your message. I'll get back to you soon.",
            "That's a great question! Let me check and respond.",
            "I appreciate your involvement in your child's education.",
            "We can schedule a meeting to discuss this further."
        ]
        
        reply = f"{teacher_name}: {replies[0]}"
        self.chat_display.insert("end", reply + "\n\n")
        self.chat_display.see("end")
    
    # Teacher event handlers
    def mark_attendance(self, student_info):
        """Mark attendance for student"""
        messagebox.showinfo("Attendance", 
                           f"Marking attendance for {student_info['name']}\n"
                           "Status will be sent to parents automatically.")
    
    def enter_grades(self, student_info):
        """Enter grades for student"""
        messagebox.showinfo("Enter Grades", 
                           f"Opening grade entry form for {student_info['name']}")
    
    def contact_parents(self, student_info):
        """Contact student's parents"""
        messagebox.showinfo("Contact Parents", 
                           f"Opening communication channel with {student_info['name']}'s parents")
    
    def mark_all_present(self):
        """Mark all students present"""
        messagebox.showinfo("Attendance", "All students marked as present for today")
    
    def send_attendance_alerts(self):
        """Send attendance alerts to parents"""
        messagebox.showinfo("Alerts Sent", "Attendance alerts sent to all parents")
    
    def open_grade_entry(self):
        """Open grade entry dialog"""
        messagebox.showinfo("Grade Entry", "Opening grade entry form...")
    
    def send_report_cards(self):
        """Send report cards to parents"""
        messagebox.showinfo("Report Cards", "Report cards sent to all parents")
    
    def send_announcement(self):
        """Send announcement to parents"""
        messagebox.showinfo("Announcement", "Announcement sent to all parents")
    
    def schedule_meeting(self):
        """Schedule parent-teacher meeting"""
        messagebox.showinfo("Meeting", "Meeting scheduling interface opened")
    
    def send_fee_notice(self):
        """Send fee payment notice"""
        messagebox.showinfo("Fee Notice", "Fee payment notices sent")
    
    def send_teacher_message(self, recipient, subject, message):
        """Send message from teacher to parent"""
        if recipient and subject and message.strip():
            messagebox.showinfo("Message Sent", 
                               f"Message sent to {recipient}\n"
                               f"Subject: {subject}")
        else:
            messagebox.showerror("Error", "Please fill in all fields")
    
    # Admin event handlers
    def configure_school(self, school):
        """Configure school settings"""
        messagebox.showinfo("School Config", f"Opening configuration for {school['name']}")
    
    def view_school_stats(self, school):
        """View school statistics"""
        messagebox.showinfo("School Stats", f"Statistics for {school['name']}")
    
    def school_maintenance(self, school):
        """School maintenance mode"""
        messagebox.showinfo("Maintenance", f"Maintenance options for {school['name']}")
    
    def add_user(self):
        """Add new user"""
        messagebox.showinfo("Add User", "User creation form will open")
    
    def edit_user(self):
        """Edit existing user"""
        messagebox.showinfo("Edit User", "User editing form will open")
    
    def remove_user(self):
        """Remove user"""
        messagebox.showwarning("Remove User", "This will permanently remove the user")
    
    def generate_user_reports(self):
        """Generate user reports"""
        messagebox.showinfo("Reports", "Generating comprehensive user reports...")
    
    def refresh_system_status(self):
        """Refresh system status"""
        messagebox.showinfo("Status Refresh", "System status refreshed")
    
    def run_diagnostics(self):
        """Run system diagnostics"""
        messagebox.showinfo("Diagnostics", "Running comprehensive system diagnostics...")
    
    def generate_health_report(self):
        """Generate system health report"""
        messagebox.showinfo("Health Report", "Generating system health report...")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()

def main():
    """Launch the SchoolBridge GUI"""
    print("🖥️ Launching SchoolBridge GUI...")
    app = SchoolBridgeGUI()
    app.run()

if __name__ == "__main__":
    main()