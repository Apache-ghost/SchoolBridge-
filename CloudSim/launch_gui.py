"""
SchoolBridge GUI Launcher
Easy way to start the SchoolBridge graphical interface
"""
import sys
import os

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from schoolbridge_gui import main
    
    if __name__ == "__main__":
        print("=" * 60)
        print("🇨🇲 Welcome to SchoolBridge Cameroon")
        print("🖥️ Starting Graphical User Interface...")
        print("=" * 60)
        main()
        
except ImportError as e:
    print(f"❌ Error importing SchoolBridge GUI: {e}")
    print("Please ensure all required files are present.")
    input("Press Enter to exit...")
except Exception as e:
    print(f"❌ Error starting SchoolBridge: {e}")
    input("Press Enter to exit...")