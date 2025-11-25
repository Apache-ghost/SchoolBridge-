# Distributed Virtual Machine System

A distributed system with autonomous virtual machine nodes that can communicate, transfer files, and perform VM-like operations.

## Features

### 🖥️ **Real Virtual Machine Experience**
- **Boot Sequence**: POST (Power-On Self-Test), BIOS simulation, OS loading
- **Hardware Virtualization**: Virtual CPU, RAM, storage, network adapters with realistic specs
- **File Systems**: Full NTFS/FAT32/EXT4 support with formatting, defragmentation, fsck
- **Process Management**: Virtual processes, CPU scheduling, memory allocation
- **System Services**: Virtual services (networking, file system, security)

### 🌐 **Advanced Networking**
- **Virtual NICs**: Automatic IP/MAC assignment with realistic network interfaces
- **DHCP Simulation**: Dynamic IP allocation with lease management
- **Network Discovery**: ARP tables, ping, traceroute, network scanning
- **Bandwidth Throttling**: Configurable network speeds and latency simulation

### 💾 **Enterprise Storage Features**
- **RAID Simulation**: RAID 0/1/5 configurations with failure simulation
- **Disk Encryption**: Virtual BitLocker/LUKS encryption
- **Snapshots**: VM state snapshots and rollback functionality
- **Backup Systems**: Automated backups with compression and versioning

### 🔧 **System Administration**
- **User Management**: Multi-user support with permissions and groups
- **Security**: Firewall rules, antivirus scanning, intrusion detection
- **Monitoring**: Real-time performance metrics, system logs, alerts
- **Package Management**: Virtual package installer/updater system

## Quick Start

1. **Start Network Coordinator**:
   ```bash
   python network.py
   ```
   Choose port (default: 8888)

2. **Start Node**:
   ```bash
   python node.py
   ```
   Configure network connection and create/connect to node

3. **Available Commands**:
   
   **File System**: `ls`, `mkdir`, `rm`, `cat`, `find`, `cp`, `mv`, `chmod`, `df`
   
   **Storage**: `format`, `defrag`, `fsck`, `mount`, `umount`, `raid`, `encrypt`
   
   **System**: `hwinfo`, `top`, `ps`, `kill`, `service`, `cron`, `users`
   
   **Network**: `ping`, `traceroute`, `netstat`, `arp`, `ifconfig`, `firewall`
   
   **Security**: `passwd`, `sudo`, `antivirus`, `audit`, `keys`
   
   **Management**: `snapshot`, `backup`, `restore`, `clone`, `migrate`

## Architecture

- **Network Layer**: TCP socket communication with JSON messaging
- **Virtual Hardware**: Simulated CPU, memory, storage, and network components
- **File System**: Virtual file system with NTFS/FAT32/EXT4 support
- **Node Management**: Create new nodes or reconnect to existing ones

## Requirements

- Python 3.7+
- No external dependencies (uses standard library only)