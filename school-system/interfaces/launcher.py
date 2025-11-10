"""
SchoolBridge Distributed System - User-Friendly Launcher
Choose how you want to explore the distributed system
"""
import os
import sys
import time

class SchoolBridgeLauncher:
    def __init__(self):
        self.title = "🇨🇲 SCHOOLBRIDGE DISTRIBUTED SYSTEM EXPLORER"
        
    def clear_screen(self):
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def print_header(self):
        print("=" * 70)
        print(self.title.center(70))
        print("=" * 70)
        print("🏫 Cameroon Educational Network - Distributed Architecture")
        print("📍 Multiple autonomous school nodes working as one system")
        print("=" * 70)
        
    def show_system_overview(self):
        print("\n🌍 SYSTEM OVERVIEW:")
        print("┌─────────────────────────────────────────────────────────────────┐")
        print("│  SchoolBridge implements a TRUE distributed system where:        │")
        print("│                                                                 │")
        print("│  🏫 Each School = Autonomous Computing Node                     │")
        print("│     • ICT University (Yaoundé - Centre Region)                 │")  
        print("│     • Polytech Cameroon (Douala - Littoral Region)             │")
        print("│     • University of Yaoundé I (Bafoussam - West Region)        │")
        print("│                                                                 │")
        print("│  🌐 Network Communication                                       │")
        print("│     • P2P messaging between teachers/parents                    │")
        print("│     • Inter-node data synchronization                          │")
        print("│     • Multi-region load balancing                              │")
        print("│                                                                 │")
        print("│  🛡️ Fault Tolerance                                            │")
        print("│     • 6 distributed database replicas                          │")
        print("│     • Automatic failure detection & recovery                   │")
        print("│     • No single point of failure                               │")
        print("└─────────────────────────────────────────────────────────────────┘")
        
    def show_exploration_options(self):
        print("\n🎯 HOW DO YOU WANT TO EXPLORE THE SYSTEM?")
        print()
        print("📱 INTERACTIVE MODES:")
        print("1. 🖥️  Terminal Mode - Step-by-step system demonstration")
        print("   → Watch live distributed system initialization")
        print("   → See autonomous nodes being created in real-time")
        print("   → Interactive prompts to control the flow")
        print()
        
        print("2. 🎭 Role-Playing UI - Login as different users")
        print("   → Teacher dashboard (send messages, view students)")
        print("   → Parent dashboard (check grades, communicate)")
        print("   → Student dashboard (view assignments, messages)")
        print("   → Admin dashboard (system management)")
        print()
        
        print("3. 🔬 Technical Analysis - Architecture deep-dive")
        print("   → Detailed distributed system compliance check")
        print("   → Node autonomy demonstration")
        print("   → Network communication analysis")
        print()
        
        print("4. 📊 Live System Monitor - Real-time status")
        print("   → Watch nodes processing messages")
        print("   → See fault tolerance in action")
        print("   → Monitor cross-region communication")
        print()
        
        print("0. 🚪 Exit")
        
    def get_user_choice(self):
        while True:
            try:
                choice = input("\n👉 Enter your choice (0-4): ").strip()
                if choice in ['0', '1', '2', '3', '4']:
                    return int(choice)
                else:
                    print("❌ Invalid choice. Please enter 0, 1, 2, 3, or 4.")
            except KeyboardInterrupt:
                print("\n\n👋 Goodbye!")
                sys.exit(0)
            except Exception:
                print("❌ Invalid input. Please try again.")
                
    def launch_terminal_mode(self):
        self.clear_screen()
        print("🖥️ LAUNCHING TERMINAL MODE...")
        print("=" * 50)
        print("📋 This will show you step-by-step:")
        print("   • Distributed system initialization")
        print("   • Autonomous node creation")
        print("   • Real-time network setup")
        print("   • Interactive exploration")
        print()
        
        confirm = input("🚀 Ready to start? (y/n): ").lower()
        if confirm == 'y':
            print("\n🎬 Starting distributed system demonstration...")
            time.sleep(1)
            os.system('python interactive_demo_fixed.py')
        else:
            print("📍 Returning to main menu...")
            time.sleep(1)
            
    def launch_ui_mode(self):
        self.clear_screen()
        print("🎭 LAUNCHING ROLE-PLAYING UI...")
        print("=" * 50)
        print("👤 You can login as:")
        print("   • 👨‍🏫 Teacher - Send messages, manage classes")
        print("   • 👨‍👩‍👧‍👦 Parent - Check grades, communicate with teachers")
        print("   • 🎓 Student - View assignments, read messages")
        print("   • 👔 Admin - System management and monitoring")
        print()
        
        confirm = input("🚀 Ready to explore? (y/n): ").lower()
        if confirm == 'y':
            print("\n🎬 Starting role-playing interface...")
            time.sleep(1)
            os.system('python interactive_schoolbridge_fixed.py')
        else:
            print("📍 Returning to main menu...")
            time.sleep(1)
            
    def launch_technical_analysis(self):
        self.clear_screen()
        print("🔬 LAUNCHING TECHNICAL ANALYSIS...")
        print("=" * 50)
        print("📊 This will analyze:")
        print("   • Distributed system compliance")
        print("   • Autonomous node behavior")
        print("   • Network architecture")
        print("   • Fault tolerance mechanisms")
        print()
        
        confirm = input("🚀 Ready to analyze? (y/n): ").lower()
        if confirm == 'y':
            print("\n🔍 Starting technical analysis...")
            time.sleep(1)
            os.system('python analyze_distributed.py')
            input("\nPress ENTER to return to menu...")
        else:
            print("📍 Returning to main menu...")
            time.sleep(1)
            
    def launch_system_monitor(self):
        self.clear_screen()
        print("📊 LAUNCHING LIVE SYSTEM MONITOR...")
        print("=" * 50)
        print("⚡ This will show:")
        print("   • Real-time node status")
        print("   • Message processing")
        print("   • Cross-region communication")
        print("   • Fault tolerance events")
        print()
        
        confirm = input("🚀 Ready to monitor? (y/n): ").lower()
        if confirm == 'y':
            print("\n📡 Starting live system monitoring...")
            time.sleep(1)
            os.system('python demonstrate_autonomy.py')
            input("\nPress ENTER to return to menu...")
        else:
            print("📍 Returning to main menu...")
            time.sleep(1)
    
    def run(self):
        while True:
            self.clear_screen()
            self.print_header()
            self.show_system_overview()
            self.show_exploration_options()
            
            choice = self.get_user_choice()
            
            if choice == 0:
                self.clear_screen()
                print("👋 Thank you for exploring SchoolBridge!")
                print("🌍 Remember: This is a true distributed system where")
                print("   multiple autonomous computers work together as one!")
                sys.exit(0)
                
            elif choice == 1:
                self.launch_terminal_mode()
                
            elif choice == 2:
                self.launch_ui_mode()
                
            elif choice == 3:
                self.launch_technical_analysis()
                
            elif choice == 4:
                self.launch_system_monitor()

if __name__ == "__main__":
    launcher = SchoolBridgeLauncher()
    try:
        launcher.run()
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye!")
        sys.exit(0)