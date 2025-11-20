# Distributed Virtual Machine System

A distributed system with autonomous nodes that behave like real virtual machines.

## Overview

This project creates a network of virtual machines that can communicate, share files, and run system commands just like real VMs in a data center.

## Key Features

- **Virtual Machines**: Full VM simulation with boot sequence, hardware specs, and OS commands
- **Network Communication**: Automatic IP/MAC assignment and inter-VM communication
- **File Systems**: Support for NTFS/FAT32/EXT4 with formatting and disk management
- **System Administration**: Process management, user accounts, security tools
- **Enterprise Features**: RAID arrays, encryption, snapshots, backups

## Quick Start

1. Start network: `python network.py`
2. Start VMs: `python node.py` 
3. Use VM commands: `ls`, `ps`, `netstat`, `firewall`, `backup`, etc.

## Commands

**File Operations**: `ls`, `mkdir`, `rm`, `cp`, `mv`, `format`, `mount`
**System Admin**: `ps`, `kill`, `users`, `service`, `top`, `hwinfo`  
**Networking**: `ping`, `traceroute`, `netstat`, `ifconfig`, `firewall`
**Security**: `passwd`, `sudo`, `antivirus`, `encrypt`, `audit`
**VM Management**: `snapshot`, `clone`, `backup`, `restore`

## Technical Details

- **Language**: Python 3.7+
- **Architecture**: TCP socket communication with JSON messaging
- **Dependencies**: None (uses standard library only)
- **Storage**: Virtual file systems with persistent data