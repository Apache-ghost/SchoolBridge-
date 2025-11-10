#!/usr/bin/env python3
"""
Live File Transfer with Dynamic Bandwidth Control
Shows real-time transfer from 4 Mbps to 16 Mbps with visual feedback
"""

import time
import threading
import sys
import os
from datetime import datetime

class LiveTransferSimulator:
    def __init__(self):
        self.current_bandwidth = 4.0  # Start at 4 Mbps
        self.file_size_mb = 800  # 800 MB file
        self.transferred_mb = 0.0
        self.transfer_active = False
        self.start_time = None
        self.bandwidth_lock = threading.Lock()
        
    def format_progress_bar(self, percentage, width=40):
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
    
    def calculate_eta(self, remaining_mb, current_speed):
        """Calculate estimated time to completion"""
        if current_speed <= 0:
            return float('inf')
        return remaining_mb / current_speed
    
    def transfer_worker(self):
        """Background thread handling the file transfer"""
        self.start_time = time.time()
        self.transfer_active = True
        
        while self.transferred_mb < self.file_size_mb and self.transfer_active:
            # Calculate transfer amount for this second
            with self.bandwidth_lock:
                current_speed = self.current_bandwidth
            
            # Transfer rate per second (assuming 1 second intervals)
            transfer_rate = current_speed  # MB/s
            self.transferred_mb += transfer_rate
            
            # Don't exceed file size
            if self.transferred_mb > self.file_size_mb:
                self.transferred_mb = self.file_size_mb
            
            time.sleep(1)  # 1 second interval
        
        self.transfer_active = False
    
    def input_worker(self):
        """Background thread handling user input"""
        print("📝 Commands:")
        print("  'set X' - Change bandwidth to X Mbps (e.g., 'set 16')")
        print("  'quit' - Stop transfer")
        print("  Just press Enter to see current status")
        print()
        
        while self.transfer_active:
            try:
                command = input().strip().lower()
                
                if command == 'quit':
                    self.transfer_active = False
                    break
                elif command.startswith('set '):
                    try:
                        new_bandwidth = float(command.split()[1])
                        if 1 <= new_bandwidth <= 100:
                            with self.bandwidth_lock:
                                old_bandwidth = self.current_bandwidth
                                self.current_bandwidth = new_bandwidth
                            print(f"💫 Bandwidth changed: {old_bandwidth} → {new_bandwidth} Mbps")
                        else:
                            print("❌ Bandwidth must be between 1 and 100 Mbps")
                    except (ValueError, IndexError):
                        print("❌ Usage: set <number> (e.g., set 16)")
                elif command == '':
                    # Just show status, don't print error
                    pass
                else:
                    print("❌ Unknown command. Use 'set X', 'quit', or press Enter")
                    
            except EOFError:
                self.transfer_active = False
                break
            except KeyboardInterrupt:
                self.transfer_active = False
                break
    
    def display_worker(self):
        """Background thread handling display updates"""
        print("\n" + "="*80)
        print("📁 LIVE FILE TRANSFER SIMULATION")
        print("="*80)
        print(f"📦 File Size: {self.file_size_mb} MB")
        print(f"🎯 Initial Speed: {self.current_bandwidth} Mbps")
        print("="*80)
        
        while self.transfer_active or self.transferred_mb < self.file_size_mb:
            elapsed_time = time.time() - self.start_time if self.start_time else 0
            
            with self.bandwidth_lock:
                current_speed = self.current_bandwidth
            
            percentage = (self.transferred_mb / self.file_size_mb) * 100
            remaining_mb = self.file_size_mb - self.transferred_mb
            eta = self.calculate_eta(remaining_mb, current_speed)
            
            # Actual transfer speed (considering efficiency)
            actual_speed = current_speed * 0.8  # 80% efficiency
            
            # Clear screen (Windows compatible)
            os.system('cls' if os.name == 'nt' else 'clear')
            
            print("="*80)
            print("📁 LIVE FILE TRANSFER - Dynamic Bandwidth Control")
            print("="*80)
            
            # Progress bar
            progress_bar = self.format_progress_bar(percentage)
            print(f"Progress: {progress_bar}")
            print()
            
            # Transfer statistics
            print(f"⏱️  Elapsed Time:     {elapsed_time:.1f} seconds")
            print(f"📊 Bandwidth Setting: {current_speed:.1f} Mbps")
            print(f"🔥 Actual Speed:      {actual_speed:.1f} Mbps")
            print(f"📈 Transferred:       {self.transferred_mb:.1f} MB / {self.file_size_mb} MB")
            print(f"📉 Remaining:         {remaining_mb:.1f} MB")
            
            if eta != float('inf'):
                print(f"⏰ ETA:               {eta:.1f} seconds")
            else:
                print(f"⏰ ETA:               Calculating...")
            
            print(f"🎯 Status:            {self.format_speed_indicator(current_speed)}")
            
            print("\n" + "-"*80)
            print("💻 CONTROL PANEL")
            print("-"*80)
            print("📝 Commands: 'set 16' (change to 16 Mbps) | 'set 4' (back to 4 Mbps) | 'quit'")
            print("💡 Try: set 8, set 12, set 20, etc.")
            print("▶️  Type command and press Enter:")
            
            if not self.transfer_active and self.transferred_mb >= self.file_size_mb:
                break
                
            time.sleep(0.5)  # Update display twice per second
        
        # Transfer completed
        total_time = time.time() - self.start_time if self.start_time else 0
        average_speed = self.file_size_mb / total_time if total_time > 0 else 0
        
        print("\n" + "="*80)
        print("✅ TRANSFER COMPLETED!")
        print("="*80)
        print(f"📦 Total Size:        {self.file_size_mb} MB")
        print(f"⏱️  Total Time:        {total_time:.1f} seconds")
        print(f"📊 Average Speed:     {average_speed:.1f} MB/s")
        print(f"🎯 Final Status:      COMPLETED")
        print("="*80)

    def run(self):
        """Run the live transfer simulation"""
        print("🚀 Starting Live File Transfer Simulation...")
        print("📋 Simulation: 800 MB file transfer starting at 4 Mbps")
        print("🎛️  You can change the bandwidth during transfer!")
        print()
        input("Press Enter to start the transfer...")
        
        # Start all worker threads
        transfer_thread = threading.Thread(target=self.transfer_worker, daemon=True)
        input_thread = threading.Thread(target=self.input_worker, daemon=True)
        display_thread = threading.Thread(target=self.display_worker, daemon=True)
        
        transfer_thread.start()
        input_thread.start()
        display_thread.start()
        
        try:
            # Wait for transfer to complete
            transfer_thread.join()
            
            # Give display a moment to show completion
            time.sleep(2)
            
        except KeyboardInterrupt:
            print("\n🛑 Transfer interrupted by user")
            self.transfer_active = False

def main():
    """Main function"""
    print("🎬 Live File Transfer with Dynamic Bandwidth Control")
    print("=" * 60)
    print("This simulation shows a file transfer that starts at 4 Mbps")
    print("and allows you to change the speed to 16 Mbps (or any other value)")
    print("during the transfer process.")
    print()
    
    simulator = LiveTransferSimulator()
    
    try:
        simulator.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()