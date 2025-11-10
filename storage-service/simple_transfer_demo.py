#!/usr/bin/env python3
"""
Simple File Transfer with Manual Speed Control
Works better in PowerShell - uses separate input/display windows
"""

import time
import threading
import sys
import os

class SimpleTransferDemo:
    def __init__(self):
        self.current_bandwidth = 4.0  # Start at 4 Mbps
        self.file_size_mb = 800  # 800 MB file
        self.transferred_mb = 0.0
        self.transfer_active = False
        self.start_time = None
        self.bandwidth_lock = threading.Lock()
        self.messages = []
        
    def format_progress_bar(self, percentage, width=40):
        """Create a visual progress bar"""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {percentage:.1f}%"
    
    def transfer_worker(self):
        """Background thread handling the file transfer"""
        self.start_time = time.time()
        self.transfer_active = True
        
        while self.transferred_mb < self.file_size_mb and self.transfer_active:
            with self.bandwidth_lock:
                current_speed = self.current_bandwidth
            
            # Transfer rate per second
            self.transferred_mb += current_speed
            
            if self.transferred_mb > self.file_size_mb:
                self.transferred_mb = self.file_size_mb
            
            time.sleep(1)
        
        self.transfer_active = False
    
    def display_worker(self):
        """Display updates in a loop"""
        while self.transfer_active or self.transferred_mb < self.file_size_mb:
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            
            with self.bandwidth_lock:
                current_speed = self.current_bandwidth
            
            percentage = (self.transferred_mb / self.file_size_mb) * 100
            remaining_mb = self.file_size_mb - self.transferred_mb
            eta = remaining_mb / current_speed if current_speed > 0 else 0
            
            # Status indicator
            if current_speed < 8:
                status = "🐌 SLOW"
            elif current_speed < 12:
                status = "🚶 MEDIUM"
            else:
                status = "🚀 FAST"
            
            # Clear and show status
            print("\n" + "="*70)
            print("📁 FILE TRANSFER SIMULATION")
            print("="*70)
            progress_bar = self.format_progress_bar(percentage)
            print(f"Progress: {progress_bar}")
            print(f"⏱️  Elapsed:     {elapsed_time:.1f} seconds")
            print(f"📊 Speed:       {current_speed:.1f} Mbps {status}")
            print(f"📈 Transferred: {self.transferred_mb:.1f} MB / {self.file_size_mb} MB")
            print(f"📉 Remaining:   {remaining_mb:.1f} MB")
            print(f"⏰ ETA:         {eta:.1f} seconds")
            print("="*70)
            
            # Show recent messages
            if self.messages:
                print("📢 Recent updates:")
                for msg in self.messages[-3:]:  # Show last 3 messages
                    print(f"   {msg}")
                print("-"*70)
            
            print("💡 CONTROLS:")
            print("   Type: set 16    (change to 16 Mbps)")
            print("   Type: set 8     (change to 8 Mbps)")  
            print("   Type: set 20    (change to 20 Mbps)")
            print("   Type: quit      (stop transfer)")
            print("="*70)
            
            if not self.transfer_active and self.transferred_mb >= self.file_size_mb:
                break
                
            time.sleep(2)  # Update every 2 seconds for readability
    
    def input_worker(self):
        """Handle user input"""
        while self.transfer_active:
            try:
                command = input("\n👉 Enter command: ").strip().lower()
                
                if command == 'quit' or command == 'q':
                    self.transfer_active = False
                    self.messages.append("🛑 Transfer stopped by user")
                    break
                elif command.startswith('set '):
                    try:
                        new_speed = float(command.split()[1])
                        if 1 <= new_speed <= 100:
                            with self.bandwidth_lock:
                                old_speed = self.current_bandwidth
                                self.current_bandwidth = new_speed
                            msg = f"💫 Speed changed: {old_speed} → {new_speed} Mbps"
                            self.messages.append(msg)
                            print(f"✅ {msg}")
                        else:
                            print("❌ Speed must be between 1-100 Mbps")
                    except (ValueError, IndexError):
                        print("❌ Usage: set <number> (example: set 16)")
                elif command == 'help' or command == '':
                    print("📝 Available commands:")
                    print("   set 16  - Change speed to 16 Mbps")
                    print("   set 4   - Change speed to 4 Mbps")
                    print("   quit    - Stop transfer")
                else:
                    print(f"❌ Unknown command: '{command}'. Try 'set 16' or 'quit'")
                    
            except (EOFError, KeyboardInterrupt):
                self.transfer_active = False
                break
    
    def run(self):
        """Run the transfer simulation"""
        print("🚀 Starting File Transfer Simulation")
        print("="*50)
        print("📦 File Size: 800 MB")
        print("🎯 Initial Speed: 4 Mbps")
        print("🎛️  You can change speed during transfer!")
        print()
        
        input("Press Enter to start the transfer...")
        print("🔥 Transfer starting in 3 seconds...")
        time.sleep(1)
        print("🔥 Transfer starting in 2 seconds...")
        time.sleep(1)
        print("🔥 Transfer starting in 1 second...")
        time.sleep(1)
        print("🚀 TRANSFER STARTED!\n")
        
        # Start threads
        transfer_thread = threading.Thread(target=self.transfer_worker, daemon=True)
        display_thread = threading.Thread(target=self.display_worker, daemon=True)
        input_thread = threading.Thread(target=self.input_worker, daemon=True)
        
        transfer_thread.start()
        display_thread.start()
        input_thread.start()
        
        # Wait for transfer to complete
        try:
            transfer_thread.join()
            time.sleep(3)  # Let display show final status
        except KeyboardInterrupt:
            self.transfer_active = False
        
        # Final summary
        total_time = time.time() - self.start_time if self.start_time else 0
        average_speed = self.file_size_mb / total_time if total_time > 0 else 0
        
        print("\n" + "="*70)
        print("✅ TRANSFER COMPLETED!")
        print("="*70)
        print(f"📦 Total transferred: {self.file_size_mb} MB")
        print(f"⏱️  Total time: {total_time:.1f} seconds")
        print(f"📊 Average speed: {average_speed:.1f} MB/s")
        print("="*70)

def main():
    """Main function"""
    try:
        demo = SimpleTransferDemo()
        demo.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()