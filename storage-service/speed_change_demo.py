#!/usr/bin/env python3
"""
Direct Transfer Speed Demo
Shows transfer changing from 4 Mbps to 16 Mbps with clear visualization
"""

import time
import os

def format_progress_bar(percentage, width=50):
    """Create a visual progress bar"""
    filled = int(width * percentage / 100)
    bar = '█' * filled + '░' * (width - filled)
    return f"[{bar}] {percentage:.1f}%"

def clear_screen():
    """Clear the terminal screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_transfer_status(transferred, total, speed, elapsed_time, phase):
    """Display transfer status"""
    percentage = (transferred / total) * 100
    remaining = total - transferred
    eta = remaining / speed if speed > 0 else 0
    
    # Speed indicator
    if speed < 8:
        status_icon = "🐌 SLOW"
    elif speed < 12:
        status_icon = "🚶 MEDIUM"
    else:
        status_icon = "🚀 FAST"
    
    clear_screen()
    print("="*80)
    print("📁 DYNAMIC BANDWIDTH TRANSFER DEMONSTRATION")
    print("="*80)
    print(f"Phase: {phase}")
    print()
    
    # Progress bar
    progress_bar = format_progress_bar(percentage)
    print(f"Progress: {progress_bar}")
    print()
    
    # Statistics
    print(f"⏱️  Elapsed Time:     {elapsed_time:.1f} seconds")
    print(f"📊 Current Speed:     {speed:.1f} Mbps {status_icon}")
    print(f"📈 Transferred:       {transferred:.1f} MB / {total} MB")
    print(f"📉 Remaining:         {remaining:.1f} MB")
    if eta > 0:
        print(f"⏰ ETA:               {eta:.1f} seconds")
    print("="*80)

def main():
    """Main transfer demonstration"""
    print("🚀 DYNAMIC BANDWIDTH TRANSFER DEMO")
    print("="*50)
    print("This demo shows a file transfer that:")
    print("1. Starts at 4 Mbps (SLOW)")
    print("2. Changes to 16 Mbps (FAST) during transfer")
    print("3. Shows real-time speed impact")
    print()
    
    input("Press Enter to start the demonstration...")
    
    # Transfer settings
    file_size_mb = 800  # 800 MB file
    transferred_mb = 0.0
    start_time = time.time()
    
    print("\n🔄 Starting transfer at 4 Mbps...")
    time.sleep(2)
    
    # Phase 1: Transfer at 4 Mbps for 10 seconds
    current_speed = 4.0
    phase_1_duration = 10  # 10 seconds at 4 Mbps
    
    for second in range(phase_1_duration):
        elapsed_time = time.time() - start_time
        transferred_mb += current_speed  # Transfer 4 MB per second
        
        show_transfer_status(transferred_mb, file_size_mb, current_speed, elapsed_time, 
                           "🐌 PHASE 1 - Transferring at 4 Mbps (SLOW)")
        
        if second == 5:
            print("\n💭 Transfer is quite slow at 4 Mbps...")
            print("⏳ Let's wait a bit more and then speed it up!")
        
        time.sleep(1)
    
    # Transition message
    show_transfer_status(transferred_mb, file_size_mb, current_speed, 
                        time.time() - start_time, "🔄 SPEED CHANGE INITIATED")
    print("\n🚀 INCREASING SPEED TO 16 MBPS...")
    print("💫 Bandwidth adjustment in progress...")
    time.sleep(3)
    
    # Phase 2: Transfer at 16 Mbps
    current_speed = 16.0
    
    while transferred_mb < file_size_mb:
        elapsed_time = time.time() - start_time
        transferred_mb += current_speed  # Transfer 16 MB per second
        
        if transferred_mb > file_size_mb:
            transferred_mb = file_size_mb
        
        show_transfer_status(transferred_mb, file_size_mb, current_speed, elapsed_time,
                           "🚀 PHASE 2 - Transferring at 16 Mbps (FAST)")
        
        # Add some comments during fast phase
        progress_percent = (transferred_mb / file_size_mb) * 100
        if 50 <= progress_percent < 55:
            print("\n⚡ Much faster now! 4x speed increase!")
        elif 80 <= progress_percent < 85:
            print("\n🎯 Almost done - high speed transfer is efficient!")
        
        time.sleep(1)
        
        if transferred_mb >= file_size_mb:
            break
    
    # Final summary
    total_time = time.time() - start_time
    average_speed = file_size_mb / total_time
    
    show_transfer_status(file_size_mb, file_size_mb, current_speed, total_time,
                        "✅ TRANSFER COMPLETED")
    
    print("\n🎊 TRANSFER ANALYSIS:")
    print("="*50)
    print(f"📦 Total File Size:   {file_size_mb} MB")
    print(f"⏱️  Total Time:        {total_time:.1f} seconds")
    print(f"📊 Average Speed:     {average_speed:.1f} MB/s")
    print(f"🔄 Speed Change:      4 Mbps → 16 Mbps (4x faster)")
    print(f"💡 Time Saved:       By increasing speed, transfer completed much faster!")
    print("="*50)
    
    print("\n📈 SPEED IMPACT:")
    phase_1_time = 10  # 10 seconds at 4 Mbps
    phase_1_transferred = 40  # 40 MB in 10 seconds
    remaining_at_4mbps = (file_size_mb - phase_1_transferred) / 4  # Time if kept at 4 Mbps
    actual_remaining_time = total_time - phase_1_time
    time_saved = remaining_at_4mbps - actual_remaining_time
    
    print(f"🐌 If kept at 4 Mbps:     {phase_1_time + remaining_at_4mbps:.1f} seconds total")
    print(f"🚀 With speed boost:      {total_time:.1f} seconds total")
    print(f"⏰ Time saved:            {time_saved:.1f} seconds")
    print("="*50)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Demo interrupted!")
    except Exception as e:
        print(f"\n❌ Error: {e}")