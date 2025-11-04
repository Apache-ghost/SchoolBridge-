"""
SchoolBridge - User-Friendly Interface
Simple and functional GUI for the SchoolBridge distributed system
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import threading
import time
from datetime import datetime

# Import SchoolBridge components
from real_data_simulation import RealDataSchoolBridgeSimulation
from real_data_config import REAL_SCHOOLS, REAL_PARENTS, REAL_STUDENTS, REAL_TEACHERS, SAMPLE_GRADES, SCHOOL_FEES

class SchoolBridgeApp:
    """Main SchoolBridge Application"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SchoolBridge - Digital Education Platform")
        self.root.geometry("1000x700")
        self.root.configure(bg="#f0f0f0")
        
        # Application state
        self.simulation = None
        self.current_user = None
        self.current_role = None
        self.selected_school = None
        
        # Initialize interface
        self.create_main_interface()
        self.show_welcome_screen()
        
        # Initialize backend
        self.initialize_schoolbridge()
        
        print("🚀 SchoolBridge GUI Application Started")
    
    def create_main_interface(self):
        """Create the main application structure"""
        # Header
        self.header_frame = tk.Frame(self.root, bg="#2c3e50", height=80)
        self.header_frame.pack(fill="x")
        self.header_frame.pack_propagate(False)
        
        self.title_label = tk.Label(
            self.header_frame,
            text="🏫 SchoolBridge Cameroon",
            font=("Arial", 20, "bold"),
            bg="#2c3e50",
            fg="white"
        )
        self.title_label.pack(pady=20)
        
        # Main content area
        self.main_frame = tk.Frame(self.root, bg="#f0f0f0")
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Status bar
        self.status_frame = tk.Frame(self.root, bg="#34495e", height=30)
        self.status_frame.pack(fill="x")
        
        self.status_label = tk.Label(
            self.status_frame,
            text="Starting SchoolBridge...",
            font=("Arial", 10),
            bg="#34495e",
            fg="white"
        )
        self.status_label.pack(pady=5)
    
    def show_welcome_screen(self):
        """Show the welcome and login screen"""
        self.clear_main_frame()
        
        # Welcome container
        welcome_frame = tk.Frame(self.main_frame, bg="white", relief="solid", bd=1)
        welcome_frame.place(relx=0.5, rely=0.5, anchor="center", width=600, height=500)
        
        # Welcome title
        tk.Label(
            welcome_frame,
            text="Welcome to SchoolBridge! 🎓",
            font=("Arial", 24, "bold"),
            bg="white",
            fg="#2c3e50"
        ).pack(pady=30)
        
        tk.Label(
            welcome_frame,
            text="Connect schools, parents, and students across Cameroon",
            font=("Arial", 12),
            bg="white",
            fg="#7f8c8d"
        ).pack()
        
        # Login section
        login_frame = tk.LabelFrame(welcome_frame, text="Login", font=("Arial", 14, "bold"), bg="white")
        login_frame.pack(pady=30, padx=50, fill="both", expand=True)
        
        # School selection
        tk.Label(login_frame, text="Select Your School:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", pady=(10, 5))
        
        self.school_var = tk.StringVar()
        school_combo = ttk.Combobox(login_frame, textvariable=self.school_var, font=("Arial", 11))
        school_combo['values'] = [school['name'] for school in REAL_SCHOOLS]
        school_combo.pack(fill="x", pady=(0, 10))
        school_combo.bind('<<ComboboxSelected>>', self.on_school_selected)
        
        # Role selection
        tk.Label(login_frame, text="Select Your Role:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", pady=(10, 5))
        
        self.role_var = tk.StringVar()
        role_frame = tk.Frame(login_frame, bg="white")
        role_frame.pack(fill="x", pady=(0, 10))
        
        roles = [("parent", "👨‍👩‍👧‍👦 Parent"), ("teacher", "👨‍🏫 Teacher"), ("admin", "👨‍💼 Administrator")]
        for role_id, role_text in roles:
            tk.Radiobutton(
                role_frame,
                text=role_text,
                variable=self.role_var,
                value=role_id,
                font=("Arial", 11),
                bg="white",
                command=self.on_role_selected
            ).pack(anchor="w")
        
        # User selection
        tk.Label(login_frame, text="Select Your Account:", font=("Arial", 12, "bold"), bg="white").pack(anchor="w", pady=(10, 5))
        
        self.user_var = tk.StringVar()
        self.user_combo = ttk.Combobox(login_frame, textvariable=self.user_var, font=("Arial", 11))
        self.user_combo.pack(fill="x", pady=(0, 20))
        
        # Login button
        login_btn = tk.Button(
            login_frame,
            text="🚀 Enter SchoolBridge",
            font=("Arial", 14, "bold"),
            bg="#3498db",
            fg="white",
            pady=10,
            command=self.handle_login
        )
        login_btn.pack(fill="x")
        
        # Set default values
        if REAL_SCHOOLS:
            school_combo.set(REAL_SCHOOLS[0]['name'])
            self.on_school_selected()
        self.role_var.set("parent")
        self.on_role_selected()
    
    def on_school_selected(self, event=None):
        """Handle school selection"""
        self.selected_school = self.school_var.get()
        self.update_user_list()
        self.update_status(f"Selected school: {self.selected_school}")
    
    def on_role_selected(self):
        """Handle role selection"""
        self.update_user_list()
        role = self.role_var.get()
        self.update_status(f"Selected role: {role}")
    
    def update_user_list(self):
        """Update the user list based on school and role"""
        school_name = self.school_var.get()
        role = self.role_var.get()
        
        if not school_name or not role:
            return
        
        # Find school ID
        school_id = None
        for school in REAL_SCHOOLS:
            if school['name'] == school_name:
                school_id = school['id']
                break
        
        if not school_id:
            return
        
        # Get users based on role
        users = []
        if role == "parent":
            users = [f"{p['name']} ({p['phone']})" for p in REAL_PARENTS if p['school_id'] == school_id]
        elif role == "teacher":
            users = [t['name'] for t in REAL_TEACHERS if t['school_id'] == school_id]
        elif role == "admin":
            users = ["System Administrator", f"{school_name} Administrator"]
        
        # Update combobox
        self.user_combo['values'] = users
        if users:
            self.user_combo.set(users[0])
    
    def handle_login(self):
        """Handle login process"""
        school = self.school_var.get()
        role = self.role_var.get()
        user = self.user_var.get()
        
        if not all([school, role, user]):
            messagebox.showwarning("Incomplete Login", "Please select school, role, and user")
            return
        
        # Set current user info
        self.current_user = user.split(" (")[0] if " (" in user else user
        self.current_role = role
        self.selected_school = school
        
        # Show main dashboard
        self.show_dashboard()
        self.update_status(f"Logged in as {self.current_user} ({role}) at {school}")
        
        messagebox.showinfo("Login Successful", f"Welcome to SchoolBridge, {self.current_user}!")
    
    def show_dashboard(self):
        """Show the main dashboard"""
        self.clear_main_frame()
        
        # Update header
        self.title_label.config(text=f"🏫 SchoolBridge - {self.selected_school}")
        
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.main_frame)
        self.notebook.pack(fill="both", expand=True, pady=10)
        
        # Create tabs based on role
        if self.current_role == "parent":
            self.create_parent_tabs()
        elif self.current_role == "teacher":
            self.create_teacher_tabs()
        elif self.current_role == "admin":
            self.create_admin_tabs()
        
        # User info panel
        self.create_user_panel()
    
    def create_parent_tabs(self):
        """Create parent dashboard tabs"""
        # Children tab
        children_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(children_frame, text="👧👦 My Children")
        self.create_children_view(children_frame)
        
        # Messages tab
        messages_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(messages_frame, text="💬 Messages")
        self.create_messages_view(messages_frame)
        
        # Reports tab
        reports_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(reports_frame, text="📊 Reports")
        self.create_reports_view(reports_frame)
        
        # Fees tab
        fees_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(fees_frame, text="💰 School Fees")
        self.create_fees_view(fees_frame)
    
    def create_teacher_tabs(self):
        """Create teacher dashboard tabs"""
        # Students tab
        students_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(students_frame, text="🎓 Students")
        self.create_students_management(students_frame)
        
        # Attendance tab
        attendance_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(attendance_frame, text="📋 Attendance")
        self.create_attendance_view(attendance_frame)
        
        # Grades tab
        grades_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(grades_frame, text="📝 Grades")
        self.create_grades_management(grades_frame)
        
        # Communication tab
        comm_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(comm_frame, text="📞 Communication")
        self.create_communication_view(comm_frame)
    
    def create_admin_tabs(self):
        """Create admin dashboard tabs"""
        # Overview tab
        overview_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(overview_frame, text="📊 Overview")
        self.create_admin_overview(overview_frame)
        
        # Schools tab
        schools_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(schools_frame, text="🏫 Schools")
        self.create_schools_management(schools_frame)
        
        # Users tab
        users_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(users_frame, text="👥 Users")
        self.create_users_management(users_frame)
        
        # System tab
        system_frame = tk.Frame(self.notebook, bg="white")
        self.notebook.add(system_frame, text="⚙️ System")
        self.create_system_view(system_frame)
    
    def create_children_view(self, parent):
        """Create children overview for parents"""
        # Find parent's children
        parent_info = None
        for p in REAL_PARENTS:
            if p['name'] == self.current_user:
                parent_info = p
                break
        
        if parent_info and parent_info['children']:
            for child_id in parent_info['children']:
                child_info = None
                for student in REAL_STUDENTS:
                    if student['student_id'] == child_id:
                        child_info = student
                        break
                
                if child_info:
                    # Child card
                    child_frame = tk.LabelFrame(
                        parent, 
                        text=f"🎓 {child_info['name']}", 
                        font=("Arial", 12, "bold"),
                        bg="white"
                    )
                    child_frame.pack(fill="x", padx=20, pady=10)
                    
                    # Child details
                    details_frame = tk.Frame(child_frame, bg="white")
                    details_frame.pack(fill="x", padx=10, pady=10)
                    
                    tk.Label(
                        details_frame,
                        text=f"Program: {child_info['program']}",
                        font=("Arial", 11),
                        bg="white"
                    ).grid(row=0, column=0, sticky="w", padx=(0, 20))
                    
                    tk.Label(
                        details_frame,
                        text=f"Year: {child_info['year']}",
                        font=("Arial", 11),
                        bg="white"
                    ).grid(row=0, column=1, sticky="w")
                    
                    # Grades summary
                    grades = SAMPLE_GRADES.get(child_id, {})
                    if grades:
                        avg_grade = sum(grades.values()) / len(grades)
                        status_color = "#27ae60" if avg_grade >= 70 else "#f39c12" if avg_grade >= 50 else "#e74c3c"
                        
                        tk.Label(
                            details_frame,
                            text=f"Average: {avg_grade:.1f}%",
                            font=("Arial", 11, "bold"),
                            fg=status_color,
                            bg="white"
                        ).grid(row=1, column=0, sticky="w", pady=(5, 0))
                        
                        status = "Excellent" if avg_grade >= 80 else "Good" if avg_grade >= 70 else "Needs Improvement"
                        tk.Label(
                            details_frame,
                            text=f"Status: {status}",
                            font=("Arial", 11),
                            fg=status_color,
                            bg="white"
                        ).grid(row=1, column=1, sticky="w", pady=(5, 0))
                    
                    # Action buttons
                    btn_frame = tk.Frame(child_frame, bg="white")
                    btn_frame.pack(fill="x", padx=10, pady=(0, 10))
                    
                    tk.Button(
                        btn_frame,
                        text="📋 View Report Card",
                        command=lambda c=child_info: self.show_report_card(c),
                        bg="#3498db",
                        fg="white",
                        font=("Arial", 9)
                    ).pack(side="left", padx=(0, 10))
                    
                    tk.Button(
                        btn_frame,
                        text="👨‍🏫 Contact Teachers",
                        command=lambda c=child_info: self.contact_teachers(c),
                        bg="#2ecc71",
                        fg="white",
                        font=("Arial", 9)
                    ).pack(side="left")
        else:
            tk.Label(
                parent,
                text="No children found for this account.",
                font=("Arial", 14),
                bg="white",
                fg="#7f8c8d"
            ).pack(expand=True)
    
    def create_messages_view(self, parent):
        """Create messages view"""
        # Messages header
        header_frame = tk.Frame(parent, bg="#ecf0f1")
        header_frame.pack(fill="x", padx=10, pady=10)
        
        tk.Label(
            header_frame,
            text="📬 Recent Messages",
            font=("Arial", 16, "bold"),
            bg="#ecf0f1"
        ).pack(side="left", pady=10)
        
        tk.Button(
            header_frame,
            text="✉️ New Message",
            command=self.compose_message,
            bg="#e67e22",
            fg="white",
            font=("Arial", 10)
        ).pack(side="right", pady=10)
        
        # Messages list
        messages_frame = tk.Frame(parent, bg="white")
        messages_frame.pack(fill="both", expand=True, padx=10, pady=(0, 10))
        
        # Sample messages
        sample_messages = [
            {"from": "Mrs. Johnson (Math Teacher)", "subject": "Grace - Excellent Performance", "time": "2 hours ago", "type": "good"},
            {"from": "School Administration", "subject": "Fee Payment Reminder", "time": "1 day ago", "type": "warning"},
            {"from": "Mr. Paul (Physics)", "subject": "David - Assignment Missing", "time": "2 days ago", "type": "alert"},
            {"from": "School Nurse", "subject": "Health Check-up Schedule", "time": "3 days ago", "type": "info"}
        ]
        
        for i, msg in enumerate(sample_messages):
            msg_frame = tk.Frame(messages_frame, bg="white", relief="solid", bd=1)
            msg_frame.pack(fill="x", pady=2)
            
            # Message type indicator
            type_colors = {"good": "#27ae60", "warning": "#f39c12", "alert": "#e74c3c", "info": "#3498db"}
            indicator = tk.Frame(msg_frame, bg=type_colors.get(msg["type"], "#bdc3c7"), width=5)
            indicator.pack(side="left", fill="y")
            
            # Message content
            content_frame = tk.Frame(msg_frame, bg="white")
            content_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
            
            tk.Label(
                content_frame,
                text=msg["from"],
                font=("Arial", 10, "bold"),
                bg="white"
            ).pack(anchor="w")
            
            tk.Label(
                content_frame,
                text=msg["subject"],
                font=("Arial", 11),
                bg="white"
            ).pack(anchor="w")
            
            tk.Label(
                content_frame,
                text=msg["time"],
                font=("Arial", 9),
                fg="#7f8c8d",
                bg="white"
            ).pack(anchor="w")
    
    def create_reports_view(self, parent):
        """Create reports view for parents"""
        tk.Label(
            parent,
            text="📊 Academic Reports",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=20)
        
        # Report cards section
        reports_frame = tk.LabelFrame(parent, text="Available Report Cards", font=("Arial", 12, "bold"), bg="white")
        reports_frame.pack(fill="x", padx=20, pady=10)
        
        # Sample report cards
        reports = [
            {"period": "Term 1 2024", "status": "Available", "date": "Sept 2024"},
            {"period": "Mid-term Assessment", "status": "Available", "date": "Oct 2024"},
            {"period": "Term 2 2024", "status": "In Progress", "date": "Expected Dec 2024"}
        ]
        
        for report in reports:
            report_frame = tk.Frame(reports_frame, bg="white")
            report_frame.pack(fill="x", padx=10, pady=5)
            
            tk.Label(
                report_frame,
                text=report["period"],
                font=("Arial", 11, "bold"),
                bg="white"
            ).pack(side="left")
            
            status_color = "#27ae60" if report["status"] == "Available" else "#f39c12"
            tk.Label(
                report_frame,
                text=report["status"],
                font=("Arial", 10),
                fg=status_color,
                bg="white"
            ).pack(side="left", padx=(20, 0))
            
            tk.Label(
                report_frame,
                text=report["date"],
                font=("Arial", 10),
                fg="#7f8c8d",
                bg="white"
            ).pack(side="right")
            
            if report["status"] == "Available":
                tk.Button(
                    report_frame,
                    text="📄 Download",
                    command=lambda p=report["period"]: self.download_report(p),
                    bg="#3498db",
                    fg="white",
                    font=("Arial", 9)
                ).pack(side="right", padx=(0, 10))
    
    def create_fees_view(self, parent):
        """Create fees view"""
        tk.Label(
            parent,
            text="💰 School Fees Management",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=20)
        
        # Fees summary
        summary_frame = tk.LabelFrame(parent, text="Fees Summary", font=("Arial", 12, "bold"), bg="white")
        summary_frame.pack(fill="x", padx=20, pady=10)
        
        # Sample fees data
        total_fees = 450000  # CFA
        paid_fees = 300000   # CFA
        balance = total_fees - paid_fees
        
        tk.Label(
            summary_frame,
            text=f"Total Annual Fees: {total_fees:,} CFA",
            font=("Arial", 12),
            bg="white"
        ).pack(anchor="w", padx=10, pady=5)
        
        tk.Label(
            summary_frame,
            text=f"Amount Paid: {paid_fees:,} CFA",
            font=("Arial", 12),
            fg="#27ae60",
            bg="white"
        ).pack(anchor="w", padx=10, pady=5)
        
        tk.Label(
            summary_frame,
            text=f"Outstanding Balance: {balance:,} CFA",
            font=("Arial", 12, "bold"),
            fg="#e74c3c" if balance > 0 else "#27ae60",
            bg="white"
        ).pack(anchor="w", padx=10, pady=5)
        
        # Payment button
        if balance > 0:
            tk.Button(
                summary_frame,
                text="💳 Make Payment",
                command=self.make_payment,
                bg="#e67e22",
                fg="white",
                font=("Arial", 12, "bold"),
                pady=5
            ).pack(pady=10)
    
    def create_students_management(self, parent):
        """Create student management for teachers"""
        tk.Label(
            parent,
            text="🎓 Student Management",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=20)
        
        # Find students for this teacher's school
        teacher_school_id = None
        for teacher in REAL_TEACHERS:
            if teacher['name'] == self.current_user:
                teacher_school_id = teacher['school_id']
                break
        
        if teacher_school_id:
            students = [s for s in REAL_STUDENTS if s['school_id'] == teacher_school_id]
            
            # Students list
            students_frame = tk.LabelFrame(parent, text="Your Students", font=("Arial", 12, "bold"), bg="white")
            students_frame.pack(fill="both", expand=True, padx=20, pady=10)
            
            # Create treeview for students
            columns = ("Name", "Program", "Year", "Status")
            tree = ttk.Treeview(students_frame, columns=columns, show="headings", height=10)
            
            for col in columns:
                tree.heading(col, text=col)
                tree.column(col, width=150)
            
            # Add students to tree
            for student in students:
                tree.insert("", "end", values=(
                    student['name'],
                    student['program'],
                    student['year'],
                    "Active"
                ))
            
            tree.pack(fill="both", expand=True, padx=10, pady=10)
    
    def create_attendance_view(self, parent):
        """Create attendance management"""
        tk.Label(
            parent,
            text="📋 Attendance Management",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=20)
        
        # Date selector
        date_frame = tk.Frame(parent, bg="white")
        date_frame.pack(pady=10)
        
        tk.Label(date_frame, text="Select Date:", font=("Arial", 12), bg="white").pack(side="left")
        
        from datetime import date
        today = date.today()
        date_var = tk.StringVar(value=today.strftime("%Y-%m-%d"))
        
        tk.Entry(date_frame, textvariable=date_var, font=("Arial", 12)).pack(side="left", padx=10)
        
        tk.Button(
            date_frame,
            text="📅 Mark Attendance",
            command=lambda: self.mark_attendance(date_var.get()),
            bg="#2ecc71",
            fg="white",
            font=("Arial", 11)
        ).pack(side="left", padx=10)
        
        # Attendance summary
        summary_text = """
        Today's Attendance Summary:
        • Total Students: 25
        • Present: 23
        • Absent: 2
        • Attendance Rate: 92%
        """
        
        tk.Label(
            parent,
            text=summary_text,
            font=("Arial", 12),
            bg="white",
            justify="left"
        ).pack(pady=20)
    
    def create_grades_management(self, parent):
        """Create grades management"""
        tk.Label(
            parent,
            text="📝 Grades Management",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=20)
        
        # Subject selector
        subject_frame = tk.Frame(parent, bg="white")
        subject_frame.pack(pady=10)
        
        tk.Label(subject_frame, text="Subject:", font=("Arial", 12), bg="white").pack(side="left")
        
        subject_var = tk.StringVar()
        subject_combo = ttk.Combobox(subject_frame, textvariable=subject_var)
        subject_combo['values'] = ["Mathematics", "Physics", "Chemistry", "Biology", "English", "French"]
        subject_combo.pack(side="left", padx=10)
        
        tk.Button(
            subject_frame,
            text="📊 Enter Grades",
            command=lambda: self.enter_grades(subject_var.get()),
            bg="#9b59b6",
            fg="white",
            font=("Arial", 11)
        ).pack(side="left", padx=10)
        
        # Grade summary
        summary_text = """
        Recent Grade Entries:
        • Mathematics Test - 15 students graded
        • Physics Lab Report - 12 students graded  
        • Chemistry Quiz - 18 students graded
        """
        
        tk.Label(
            parent,
            text=summary_text,
            font=("Arial", 12),
            bg="white",
            justify="left"
        ).pack(pady=20)
    
    def create_communication_view(self, parent):
        """Create communication tools for teachers"""
        tk.Label(
            parent,
            text="📞 Communication Center",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=20)
        
        # Communication options
        comm_frame = tk.Frame(parent, bg="white")
        comm_frame.pack(pady=20)
        
        tk.Button(
            comm_frame,
            text="📧 Send Message to Parents",
            command=self.send_parent_message,
            bg="#3498db",
            fg="white",
            font=("Arial", 12),
            width=25,
            pady=5
        ).pack(pady=5)
        
        tk.Button(
            comm_frame,
            text="📢 Send Class Announcement",
            command=self.send_announcement,
            bg="#e67e22",
            fg="white",
            font=("Arial", 12),
            width=25,
            pady=5
        ).pack(pady=5)
        
        tk.Button(
            comm_frame,
            text="🚨 Send Alert/Notification",
            command=self.send_alert,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12),
            width=25,
            pady=5
        ).pack(pady=5)
    
    def create_admin_overview(self, parent):
        """Create admin overview dashboard"""
        tk.Label(
            parent,
            text="📊 System Overview",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=20)
        
        # Statistics grid
        stats_frame = tk.Frame(parent, bg="white")
        stats_frame.pack(pady=20)
        
        # Sample statistics
        stats = [
            ("🏫 Total Schools", "3", "#3498db"),
            ("👨‍🏫 Teachers", "7", "#2ecc71"),
            ("👨‍👩‍👧‍👦 Parents", "12", "#e67e22"),
            ("🎓 Students", "8", "#9b59b6")
        ]
        
        for i, (label, value, color) in enumerate(stats):
            stat_frame = tk.Frame(stats_frame, bg=color, width=180, height=100)
            stat_frame.grid(row=0, column=i, padx=10, pady=10)
            stat_frame.pack_propagate(False)
            
            tk.Label(
                stat_frame,
                text=value,
                font=("Arial", 24, "bold"),
                bg=color,
                fg="white"
            ).pack(expand=True)
            
            tk.Label(
                stat_frame,
                text=label,
                font=("Arial", 10),
                bg=color,
                fg="white"
            ).pack(side="bottom", pady=(0, 10))
        
        # System status
        status_text = """
        System Status:
        ✅ All schools online
        ✅ Database replication healthy
        ✅ Message delivery operational
        ✅ Payment system active
        """
        
        tk.Label(
            parent,
            text=status_text,
            font=("Arial", 12),
            bg="white",
            justify="left"
        ).pack(pady=30)
    
    def create_schools_management(self, parent):
        """Create schools management for admin"""
        tk.Label(
            parent,
            text="🏫 Schools Management",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=20)
        
        # Schools list
        for school in REAL_SCHOOLS:
            school_frame = tk.LabelFrame(parent, text=school['name'], font=("Arial", 12, "bold"), bg="white")
            school_frame.pack(fill="x", padx=20, pady=10)
            
            details_frame = tk.Frame(school_frame, bg="white")
            details_frame.pack(fill="x", padx=10, pady=10)
            
            tk.Label(
                details_frame,
                text=f"Location: {school['location']}",
                font=("Arial", 11),
                bg="white"
            ).pack(anchor="w")
            
            tk.Label(
                details_frame,
                text=f"Type: {school['type']}",
                font=("Arial", 11),
                bg="white"
            ).pack(anchor="w")
            
            # Count students and teachers
            student_count = len([s for s in REAL_STUDENTS if s['school_id'] == school['id']])
            teacher_count = len([t for t in REAL_TEACHERS if t['school_id'] == school['id']])
            
            tk.Label(
                details_frame,
                text=f"Students: {student_count} | Teachers: {teacher_count}",
                font=("Arial", 11),
                bg="white"
            ).pack(anchor="w")
    
    def create_users_management(self, parent):
        """Create users management for admin"""
        tk.Label(
            parent,
            text="👥 Users Management",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=20)
        
        # User statistics
        stats_text = f"""
        User Statistics:
        👨‍🏫 Teachers: {len(REAL_TEACHERS)}
        👨‍👩‍👧‍👦 Parents: {len(REAL_PARENTS)}
        🎓 Students: {len(REAL_STUDENTS)}
        👨‍💼 Administrators: 3
        """
        
        tk.Label(
            parent,
            text=stats_text,
            font=("Arial", 12),
            bg="white",
            justify="left"
        ).pack(pady=20)
        
        # Management buttons
        btn_frame = tk.Frame(parent, bg="white")
        btn_frame.pack(pady=20)
        
        tk.Button(
            btn_frame,
            text="➕ Add New User",
            command=self.add_user,
            bg="#2ecc71",
            fg="white",
            font=("Arial", 12)
        ).pack(side="left", padx=10)
        
        tk.Button(
            btn_frame,
            text="📝 Manage Permissions",
            command=self.manage_permissions,
            bg="#f39c12",
            fg="white",
            font=("Arial", 12)
        ).pack(side="left", padx=10)
    
    def create_system_view(self, parent):
        """Create system management view"""
        tk.Label(
            parent,
            text="⚙️ System Management",
            font=("Arial", 16, "bold"),
            bg="white"
        ).pack(pady=20)
        
        # System controls
        controls_frame = tk.Frame(parent, bg="white")
        controls_frame.pack(pady=20)
        
        tk.Button(
            controls_frame,
            text="🔄 Restart System",
            command=self.restart_system,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 12),
            width=20
        ).pack(pady=5)
        
        tk.Button(
            controls_frame,
            text="💾 Backup Data",
            command=self.backup_data,
            bg="#34495e",
            fg="white",
            font=("Arial", 12),
            width=20
        ).pack(pady=5)
        
        tk.Button(
            controls_frame,
            text="📊 View Logs",
            command=self.view_logs,
            bg="#95a5a6",
            fg="white",
            font=("Arial", 12),
            width=20
        ).pack(pady=5)
    
    def create_user_panel(self):
        """Create user info and logout panel"""
        user_frame = tk.Frame(self.main_frame, bg="#ecf0f1", height=60)
        user_frame.pack(fill="x", pady=(10, 0))
        user_frame.pack_propagate(False)
        
        tk.Label(
            user_frame,
            text=f"👤 {self.current_user} ({self.current_role.title()})",
            font=("Arial", 12, "bold"),
            bg="#ecf0f1"
        ).pack(side="left", padx=20, pady=20)
        
        tk.Button(
            user_frame,
            text="🚪 Logout",
            command=self.logout,
            bg="#e74c3c",
            fg="white",
            font=("Arial", 11)
        ).pack(side="right", padx=20, pady=15)
    
    # Event handlers and utility methods
    def show_report_card(self, child):
        """Show report card for a child"""
        messagebox.showinfo("Report Card", f"Opening report card for {child['name']}")
    
    def contact_teachers(self, child):
        """Contact teachers for a child"""
        messagebox.showinfo("Contact Teachers", f"Contacting teachers for {child['name']}")
    
    def compose_message(self):
        """Compose a new message"""
        messagebox.showinfo("New Message", "Opening message composer")
    
    def download_report(self, period):
        """Download a report"""
        messagebox.showinfo("Download", f"Downloading report for {period}")
    
    def make_payment(self):
        """Make fee payment"""
        messagebox.showinfo("Payment", "Opening payment gateway")
    
    def mark_attendance(self, date):
        """Mark attendance"""
        messagebox.showinfo("Attendance", f"Marking attendance for {date}")
    
    def enter_grades(self, subject):
        """Enter grades"""
        messagebox.showinfo("Grades", f"Entering grades for {subject}")
    
    def send_parent_message(self):
        """Send message to parents"""
        messagebox.showinfo("Message", "Sending message to parents")
    
    def send_announcement(self):
        """Send class announcement"""
        messagebox.showinfo("Announcement", "Sending class announcement")
    
    def send_alert(self):
        """Send alert notification"""
        messagebox.showinfo("Alert", "Sending alert notification")
    
    def add_user(self):
        """Add new user"""
        messagebox.showinfo("Add User", "Opening user creation form")
    
    def manage_permissions(self):
        """Manage user permissions"""
        messagebox.showinfo("Permissions", "Opening permissions management")
    
    def restart_system(self):
        """Restart system"""
        result = messagebox.askyesno("Restart System", "Are you sure you want to restart the system?")
        if result:
            messagebox.showinfo("Restart", "System restart initiated")
    
    def backup_data(self):
        """Backup system data"""
        messagebox.showinfo("Backup", "Data backup started")
    
    def view_logs(self):
        """View system logs"""
        messagebox.showinfo("Logs", "Opening system logs viewer")
    
    def logout(self):
        """Logout user"""
        result = messagebox.askyesno("Logout", "Are you sure you want to logout?")
        if result:
            self.current_user = None
            self.current_role = None
            self.selected_school = None
            self.title_label.config(text="🏫 SchoolBridge Cameroon")
            self.show_welcome_screen()
            self.update_status("Logged out successfully")
    
    def clear_main_frame(self):
        """Clear all widgets from main frame"""
        for widget in self.main_frame.winfo_children():
            widget.destroy()
    
    def update_status(self, message):
        """Update status bar message"""
        self.status_label.config(text=message)
        self.root.update_idletasks()
    
    def initialize_schoolbridge(self):
        """Initialize SchoolBridge simulation in background"""
        def init():
            try:
                self.simulation = RealDataSchoolBridgeSimulation()
                self.root.after(0, lambda: self.update_status("Initializing distributed infrastructure..."))
                
                self.simulation.setup_real_infrastructure()
                self.root.after(0, lambda: self.update_status("Setting up school nodes..."))
                
                self.simulation.populate_real_data()
                self.root.after(0, lambda: self.update_status("✅ SchoolBridge system ready - All services online"))
                
            except Exception as e:
                error_msg = f"❌ System initialization failed: {str(e)}"
                self.root.after(0, lambda: self.update_status(error_msg))
                print(f"SchoolBridge initialization error: {e}")
        
        threading.Thread(target=init, daemon=True).start()
    
    def run(self):
        """Start the application"""
        self.root.mainloop()

def main():
    """Launch SchoolBridge Application"""
    print("🚀 Starting SchoolBridge - Digital Education Platform")
    app = SchoolBridgeApp()
    app.run()

if __name__ == "__main__":
    main()