#!/usr/bin/env python3
"""
Fixed Live File Transfer with Dynamic Bandwidth Control
Shows real-time transfer with proper input handling
"""

import time
import threading
import sys
import os
import msvcrt  # For Windows key detection
from datetime import datetime

class InteractiveTransferSimulator:
    def __init__(self):
        self.current_bandwidth = 4.0  # Start at 4 Mbps
        self.file_size_mb = 800  # 800 MB file
        self.transferred_mb = 0.0
        self.transfer_active = False
        self.start_time = None
        self.bandwidth_lock = threading.Lock()
        self.last_display_time = 0
        self.command_buffer = ""
        
    def format_progress_bar(self, percentage, width=50):
        """Create a visual progress bar"""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {percentage:.1f}%"
    
    def format_speed_indicator(self, speed):
        """Visual speed indicator"""
        if speed < 8:
            return "🐌 SLOW"
        elif speed < 12:
            return "🚶 MEDIUM" 
        else:
            return "🚀 FAST"
    
    def transfer_worker(self):
        """Background thread handling the file transfer"""
        self.start_time = time.time()
        self.transfer_active = True
        
        while self.transferred_mb < self.file_size_mb and self.transfer_active:
            # Calculate transfer amount for this second
            with self.bandwidth_lock:
                current_speed = self.current_bandwidth
            
            # Transfer rate per second (MB/s)
            transfer_rate = current_speed
            self.transferred_mb += transfer_rate
            
            # Don't exceed file size
            if self.transferred_mb > self.file_size_mb:
                self.transferred_mb = self.file_size_mb
            
            time.sleep(1)  # 1 second interval
        
        self.transfer_active = False
    
    def process_command(self, command):
        """Process user command"""
        command = command.strip().lower()
        
        if command == 'quit' or command == 'q':
            self.transfer_active = False
            return "🛑 Transfer stopped by user"
        elif command.startswith('set '):
            try:
                new_bandwidth = float(command.split()[1])
                if 1 <= new_bandwidth <= 100:
                    with self.bandwidth_lock:
                        old_bandwidth = self.current_bandwidth
                        self.current_bandwidth = new_bandwidth
                    return f"💫 Bandwidth: {old_bandwidth} → {new_bandwidth} Mbps"
                else:
                    return "❌ Bandwidth must be between 1-100 Mbps"
            except (ValueError, IndexError):
                return "❌ Usage: set <number> (e.g., 'set 16')"
        elif command == 'help' or command == 'h':
            return "📝 Commands: set <speed>, quit, help"
        elif command == '':
            return ""
        else:
            return f"❌ Unknown: '{command}'. Type 'help' for commands"
    
    def display_status(self):
        """Display current transfer status"""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        
        with self.bandwidth_lock:
            current_speed = self.current_bandwidth
        
        percentage = (self.transferred_mb / self.file_size_mb) * 100
        remaining_mb = self.file_size_mb - self.transferred_mb
        eta = remaining_mb / current_speed if current_speed > 0 else float('inf')
        
        # Clear and display
        os.system('cls')
        print("="*80)
        print("📁 LIVE FILE TRANSFER - Dynamic Bandwidth Control")
        print("="*80)
        
        # Progress
        progress_bar = self.format_progress_bar(percentage)
        print(f"Progress: {progress_bar}")
        print()
        
        # Stats
        print(f"⏱️  Time:        {elapsed_time:.1f}s")
        print(f"📊 Bandwidth:    {current_speed:.1f} Mbps {self.format_speed_indicator(current_speed)}")
        print(f"📈 Transferred:  {self.transferred_mb:.1f} MB / {self.file_size_mb} MB")
        print(f"📉 Remaining:    {remaining_mb:.1f} MB")
        if eta != float('inf'):
            print(f"⏰ ETA:          {eta:.1f}s")
        else:
            print(f"⏰ ETA:          Calculating...")
        
        print()
        print("-"*80)
        print("💻 COMMANDS: 'set 16' | 'set 8' | 'set 20' | 'quit'")
        print("-"*80)
        print(f"Type command: {self.command_buffer}", end='', flush=True)

    def run_interactive(self):
        """Run with interactive input"""
        print("🚀 Starting Interactive File Transfer...")
        print("📋 File: 800 MB | Initial Speed: 4 Mbps")
        print("🎛️  Type commands during transfer to change speed!")
        print()
        input("Press Enter to start...")
        
        # Start transfer thread
        transfer_thread = threading.Thread(target=self.transfer_worker, daemon=True)
        transfer_thread.start()
        
        # Main loop with real-time input
        self.command_buffer = ""
        
        while self.transfer_active or self.transferred_mb < self.file_size_mb:
            # Update display every 0.5 seconds
            current_time = time.time()
            if current_time - self.last_display_time > 0.5:
                self.display_status()
                self.last_display_time = current_time
            
            # Check for keyboard input (Windows)
            if msvcrt.kbhit():
                char = msvcrt.getch().decode('utf-8', errors='ignore')
                
                if char == '\r':  # Enter key
                    if self.command_buffer:
                        result = self.process_command(self.command_buffer)
                        if result:
                            print(f"\n{result}")
                            time.sleep(1)  # Show message briefly
                        self.command_buffer = ""
                elif char == '\x08':  # Backspace
                    if self.command_buffer:
                        self.command_buffer = self.command_buffer[:-1]
                elif char == '\x03':  # Ctrl+C
                    self.transfer_active = False
                    break
                elif len(char) == 1 and ord(char) >= 32:  # Printable character
                    self.command_buffer += char
            
            time.sleep(0.1)  # Small delay to prevent high CPU usage
        
        # Final status
        total_time = time.time() - self.start_time if self.start_time else 0
        average_speed = self.file_size_mb / total_time if total_time > 0 else 0
        
        print("\n" + "="*80)
        print("✅ TRANSFER COMPLETED!")
        print(f"📦 Size: {self.file_size_mb} MB | ⏱️ Time: {total_time:.1f}s | 📊 Avg: {average_speed:.1f} MB/s")
        print("="*80)

def main():
    """Main function"""
    try:
        simulator = InteractiveTransferSimulator()
        simulator.run_interactive()
    except KeyboardInterrupt:
        print("\n👋 Transfer interrupted!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()