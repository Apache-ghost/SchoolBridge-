#!/usr/bin/env python3
"""
Simple Step-by-Step Transfer Demo
Shows transfer speed changes clearly - you can pause and change speed
"""

import time
import os

class StepByStepTransfer:
    def __init__(self):
        self.current_bandwidth = 4.0  # Start at 4 Mbps
        self.file_size_mb = 800  # 800 MB file
        self.transferred_mb = 0.0
        self.start_time = None
        
    def format_progress_bar(self, percentage, width=50):
        """Create a visual progress bar"""
        filled = int(width * percentage / 100)
        bar = '█' * filled + '░' * (width - filled)
        return f"[{bar}] {percentage:.1f}%"
    
    def show_status(self):
        """Show current transfer status"""
        elapsed_time = time.time() - self.start_time if self.start_time else 0
        percentage = (self.transferred_mb / self.file_size_mb) * 100
        remaining_mb = self.file_size_mb - self.transferred_mb
        eta = remaining_mb / self.current_bandwidth if self.current_bandwidth > 0 else 0
        
        # Speed status
        if self.current_bandwidth < 8:
            status = "🐌 SLOW"
        elif self.current_bandwidth < 12:
            status = "🚶 MEDIUM"
        else:
            status = "🚀 FAST"
        
        # Clear screen
        os.system('cls')
        
        print("="*80)
        print("📁 FILE TRANSFER SIMULATION - STEP BY STEP CONTROL")
        print("="*80)
        
        # Progress bar
        progress_bar = self.format_progress_bar(percentage)
        print(f"Progress: {progress_bar}")
        print()
        
        # Statistics
        print(f"⏱️  Elapsed Time:     {elapsed_time:.1f} seconds")
        print(f"📊 Current Speed:     {self.current_bandwidth:.1f} Mbps {status}")
        print(f"📈 Transferred:       {self.transferred_mb:.1f} MB / {self.file_size_mb} MB")
        print(f"📉 Remaining:         {remaining_mb:.1f} MB")
        print(f"⏰ ETA:               {eta:.1f} seconds")
        print()
        print("="*80)
    
    def process_transfer_step(self):
        """Process one step of transfer (5 seconds worth)"""
        step_duration = 5  # 5 seconds per step
        transfer_amount = self.current_bandwidth * step_duration
        
        self.transferred_mb += transfer_amount
        if self.transferred_mb > self.file_size_mb:
            self.transferred_mb = self.file_size_mb
        
        # Simulate the time passing
        time.sleep(0.1)  # Just a tiny delay for realism
    
    def run(self):
        """Run the step-by-step transfer"""
        print("🚀 Step-by-Step File Transfer Simulation")
        print("="*60)
        print("📦 File Size: 800 MB")
        print("🎯 Initial Speed: 4 Mbps")
        print("🎛️  You can change speed between steps!")
        print()
        print("HOW IT WORKS:")
        print("1. Transfer runs in 5-second steps")
        print("2. After each step, you can change the speed")
        print("3. Type your new speed and press Enter")
        print("4. Or just press Enter to continue at current speed")
        print()
        
        input("Press Enter to start...")
        
        self.start_time = time.time()
        step_number = 1
        
        while self.transferred_mb < self.file_size_mb:
            # Show current status
            self.show_status()
            
            print(f"🔄 STEP {step_number} - Transferring for 5 seconds at {self.current_bandwidth} Mbps...")
            print("="*80)
            
            # Process transfer step
            self.process_transfer_step()
            step_number += 1
            
            # Check if transfer is complete
            if self.transferred_mb >= self.file_size_mb:
                break
            
            # Ask user for speed change
            self.show_status()
            print("🎛️  SPEED CONTROL")
            print("="*80)
            print(f"Current speed: {self.current_bandwidth} Mbps")
            print()
            print("Options:")
            print("  - Type '16' and press Enter → Change to 16 Mbps")
            print("  - Type '8' and press Enter  → Change to 8 Mbps")
            print("  - Type '20' and press Enter → Change to 20 Mbps")
            print("  - Just press Enter          → Keep current speed")
            print("  - Type 'quit'               → Stop transfer")
            print()
            
            try:
                user_input = input("👉 Enter new speed (or press Enter to continue): ").strip()
                
                if user_input.lower() == 'quit':
                    print("🛑 Transfer stopped by user")
                    break
                elif user_input == '':
                    print(f"✅ Continuing at {self.current_bandwidth} Mbps...")
                    time.sleep(1)
                else:
                    try:
                        new_speed = float(user_input)
                        if 1 <= new_speed <= 100:
                            old_speed = self.current_bandwidth
                            self.current_bandwidth = new_speed
                            print(f"💫 Speed changed: {old_speed} → {new_speed} Mbps")
                            time.sleep(1)
                        else:
                            print("❌ Speed must be between 1-100 Mbps")
                            time.sleep(2)
                    except ValueError:
                        print(f"❌ Invalid input: '{user_input}'. Using current speed.")
                        time.sleep(2)
            except KeyboardInterrupt:
                print("\n🛑 Transfer interrupted")
                break
        
        # Final summary
        total_time = time.time() - self.start_time if self.start_time else 0
        average_speed = self.file_size_mb / total_time if total_time > 0 else 0
        
        self.show_status()
        print("✅ TRANSFER COMPLETED!")
        print("="*80)
        print(f"📦 Total Size:        {self.file_size_mb} MB")
        print(f"⏱️  Total Time:        {total_time:.1f} seconds")
        print(f"📊 Average Speed:     {average_speed:.1f} MB/s")
        print(f"🎯 Final Speed:       {self.current_bandwidth} Mbps")
        print("="*80)

def main():
    """Main function"""
    try:
        transfer = StepByStepTransfer()
        transfer.run()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

if __name__ == "__main__":
    main()