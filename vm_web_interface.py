#!/usr/bin/env python3
"""
VM Web Interface Integration - Connects VM Hypervisor with CloudDrive Web Interface
"""

from flask import Flask, request, jsonify, render_template, session, redirect, url_for
from vm_hypervisor import VMHypervisor
from node import AutonomousNode
from network import NetworkCoordinator, NetworkInterface
import json
import threading
import time

class VMWebInterface:
    """Web interface for VM management"""
    
    def __init__(self, app, hypervisor):
        self.app = app
        self.hypervisor = hypervisor
        self.setup_routes()
    
    def setup_routes(self):
        """Setup VM management routes"""
        
        @self.app.route('/vms')
        def vm_dashboard():
            """Main VM dashboard"""
            if 'username' not in session:
                return redirect(url_for('login'))
            
            vms = self.hypervisor.get_vm_list(owner=session['username'])
            metrics = self.hypervisor.get_system_metrics(owner=session['username'])
            return render_template('vm_dashboard.html', vms=vms, metrics=metrics, user={'username': session['username']})
        
        @self.app.route('/vm/<vm_id>')
        def vm_details(vm_id):
            """VM details page"""
            if 'username' not in session:
                return redirect(url_for('login'))
            
            details = self.hypervisor.get_vm_details(vm_id)
            if not details['success']:
                return jsonify(details), 404
            
            return render_template('vm_details.html', vm=details, vm_id=vm_id)
        
        @self.app.route('/vm/<vm_id>/console')
        def vm_console(vm_id):
            """VM console interface"""
            if 'username' not in session:
                return redirect(url_for('login'))
            
            return render_template('vm_console.html', vm_id=vm_id)
        
        @self.app.route('/api/vm/create', methods=['POST'])
        def create_vm():
            """Create new VM via API"""
            if 'username' not in session:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            data = request.json
            result = self.hypervisor.create_vm(
                name=data.get('name'),
                description=data.get('description', ''),
                os_type=data.get('os_type'),
                cpu_cores=data.get('cpu_cores', 2),
                ram_mb=data.get('ram_mb', 2048),
                disk_gb=data.get('disk_gb', 20),
                network_adapters=data.get('network_adapters', 1),
                owner=session['username']
            )
            
            return jsonify(result)
        
        @self.app.route('/api/vm/<vm_id>/start', methods=['POST'])
        def start_vm(vm_id):
            """Start VM"""
            if 'username' not in session:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            result = self.hypervisor.start_vm(vm_id)
            return jsonify(result)
        
        @self.app.route('/api/vm/<vm_id>/stop', methods=['POST'])
        def stop_vm(vm_id):
            """Stop VM"""
            if 'username' not in session:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            force = request.json.get('force', False) if request.json else False
            result = self.hypervisor.stop_vm(vm_id, force)
            return jsonify(result)
        
        @self.app.route('/api/vm/<vm_id>/snapshot', methods=['POST'])
        def create_snapshot(vm_id):
            """Create VM snapshot"""
            if 'username' not in session:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            data = request.json
            result = self.hypervisor.create_snapshot(
                vm_id=vm_id,
                name=data.get('name'),
                description=data.get('description', '')
            )
            return jsonify(result)
        
        @self.app.route('/api/vm/<vm_id>/details')
        def get_vm_details(vm_id):
            """Get VM details via API"""
            if 'username' not in session:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            details = self.hypervisor.get_vm_details(vm_id)
            return jsonify(details)
        
        @self.app.route('/api/vm/<vm_id>/execute', methods=['POST'])
        def execute_vm_command(vm_id):
            """Execute command in VM"""
            if 'username' not in session:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            if vm_id not in self.hypervisor.vms:
                return jsonify({'success': False, 'error': 'VM not found'})
            
            vm = self.hypervisor.vms[vm_id]
            command = request.json.get('command', '')
            
            # Route command to appropriate VM component
            result = self._execute_vm_command(vm, command)
            return jsonify(result)
        
        @self.app.route('/api/vm/<vm_id>/filesystem', methods=['GET', 'POST'])
        def vm_filesystem_operations(vm_id):
            """Handle VM filesystem operations"""
            if 'username' not in session:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            if vm_id not in self.hypervisor.vms:
                return jsonify({'success': False, 'error': 'VM not found'})
            
            vm = self.hypervisor.vms[vm_id]
            
            if request.method == 'GET':
                operation = request.args.get('operation')
                
                if operation == 'format':
                    fs_type = request.args.get('fs_type', 'NTFS')
                    quick = request.args.get('quick', 'true').lower() == 'true'
                    result = vm['filesystem'].format_disk(fs_type, quick)
                
                elif operation == 'defrag':
                    result = vm['filesystem'].defragment()
                
                elif operation == 'fsck':
                    auto_fix = request.args.get('auto_fix', 'true').lower() == 'true'
                    result = vm['filesystem'].fsck(auto_fix)
                
                else:
                    result = {'success': False, 'error': 'Unknown filesystem operation'}
            
            else:  # POST
                data = request.json
                operation = data.get('operation')
                
                if operation == 'setup_raid':
                    result = vm['filesystem'].setup_raid(
                        data.get('raid_level'),
                        data.get('disks', [])
                    )
                
                elif operation == 'encrypt':
                    result = vm['filesystem'].encrypt_disk(
                        data.get('password'),
                        data.get('algorithm', 'AES-256')
                    )
                
                else:
                    result = {'success': False, 'error': 'Unknown filesystem operation'}
            
            return jsonify(result)
        
        @self.app.route('/api/vm/<vm_id>/network', methods=['GET', 'POST'])
        def vm_network_operations(vm_id):
            """Handle VM network operations"""
            if 'username' not in session:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            if vm_id not in self.hypervisor.vms:
                return jsonify({'success': False, 'error': 'VM not found'})
            
            vm = self.hypervisor.vms[vm_id]
            
            if request.method == 'GET':
                operation = request.args.get('operation')
                
                if operation == 'ping':
                    target = request.args.get('target', 'google.com')
                    count = int(request.args.get('count', 4))
                    result = vm['networking'].ping(target, count)
                
                elif operation == 'traceroute':
                    target = request.args.get('target', 'google.com')
                    result = vm['networking'].traceroute(target)
                
                elif operation == 'netstat':
                    result = vm['networking'].netstat()
                
                else:
                    result = {'success': False, 'error': 'Unknown network operation'}
            
            else:  # POST
                data = request.json
                operation = data.get('operation')
                
                if operation == 'firewall':
                    result = vm['networking'].configure_firewall(
                        data.get('rule_type'),
                        data.get('action'),
                        data.get('port'),
                        data.get('ip')
                    )
                
                else:
                    result = {'success': False, 'error': 'Unknown network operation'}
            
            return jsonify(result)
        
        @self.app.route('/api/vm/<vm_id>/processes')
        def vm_processes(vm_id):
            """Get VM processes"""
            if 'username' not in session:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            if vm_id not in self.hypervisor.vms:
                return jsonify({'success': False, 'error': 'VM not found'})
            
            vm = self.hypervisor.vms[vm_id]
            processes = vm['processes'].get_process_list()
            metrics = vm['processes'].get_system_metrics()
            
            return jsonify({
                'success': True,
                'processes': processes,
                'system_metrics': metrics
            })
        
        @self.app.route('/api/vm/<vm_id>/kill-process', methods=['POST'])
        def kill_vm_process(vm_id):
            """Kill VM process"""
            if 'username' not in session:
                return jsonify({'success': False, 'error': 'Not authenticated'}), 401
            
            if vm_id not in self.hypervisor.vms:
                return jsonify({'success': False, 'error': 'VM not found'})
            
            vm = self.hypervisor.vms[vm_id]
            pid = request.json.get('pid')
            signal = request.json.get('signal', 'TERM')
            
            result = vm['processes'].kill_process(pid, signal)
            return jsonify(result)
        
        @self.app.route('/api/vm/network-status')
        def vm_network_status():
            """Get global network status"""
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            network_info = self.hypervisor.get_network_status()
            return jsonify(network_info)
        
        @self.app.route('/vm-snapshots')
        def vm_snapshots():
            """VM snapshots management page"""
            if 'username' not in session:
                return redirect(url_for('login'))
            
            snapshots = self.hypervisor.get_snapshots(owner=session['username'])
            return render_template('vm_snapshots.html', snapshots=snapshots, user={'username': session['username']})
        
        @self.app.route('/vm-shared')
        def vm_shared():
            """Shared VMs page"""
            if 'username' not in session:
                return redirect(url_for('login'))
            
            shared_vms = self.hypervisor.get_shared_vms()
            return render_template('vm_shared.html', vms=shared_vms, user={'username': session['username']})
        
        @self.app.route('/vm-templates')
        def vm_templates():
            """VM templates page"""
            if 'username' not in session:
                return redirect(url_for('login'))
            
            templates = self.hypervisor.get_templates()
            return render_template('vm_templates.html', templates=templates, user={'username': session['username']})
        
        @self.app.route('/vm-network')
        def vm_network():
            """VM network management page"""
            if 'username' not in session:
                return redirect(url_for('login'))
            
            network_info = self.hypervisor.get_network_topology()
            return render_template('vm_network.html', network=network_info, user={'username': session['username']})
        
        @self.app.route('/api/vm/<vm_id>/node/connect', methods=['POST'])
        def connect_vm_node(vm_id):
            """Connect VM as autonomous node to network"""
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            result = self.hypervisor.connect_vm_as_node(vm_id)
            return jsonify(result)
        
        @self.app.route('/api/vm/<vm_id>/file-transfer', methods=['POST'])
        def vm_file_transfer(vm_id):
            """Transfer file between VMs"""
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            data = request.get_json()
            target_vm = data.get('target_vm')
            file_name = data.get('file_name')
            action = data.get('action', 'send')
            
            result = self.hypervisor.transfer_file_between_vms(vm_id, target_vm, file_name, action)
            return jsonify(result)
        
        @self.app.route('/api/vm/<vm_id>/execute-command', methods=['POST'])
        def execute_node_command(vm_id):
            """Execute command on VM node"""
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            data = request.get_json()
            command = data.get('command')
            args = data.get('args', [])
            
            result = self.hypervisor.execute_node_command(vm_id, command, args)
            return jsonify(result)
        
        @self.app.route('/api/network/traffic')
        def network_traffic():
            """Get real-time network traffic data"""
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            traffic = self.hypervisor.get_network_traffic()
            return jsonify(traffic)
        
        @self.app.route('/api/network/nodes')
        def network_nodes():
            """Get all connected nodes in the network"""
            if 'username' not in session:
                return jsonify({'error': 'Not authenticated'}), 401
            
            nodes = self.hypervisor.get_network_nodes()
            return jsonify(nodes)
    
    def _execute_vm_command(self, vm, command):
        """Execute command in VM and return result"""
        command_parts = command.strip().split()
        if not command_parts:
            return {'success': False, 'error': 'Empty command'}
        
        cmd = command_parts[0].lower()
        args = command_parts[1:] if len(command_parts) > 1 else []
        
        # System information commands
        if cmd == 'hwinfo':
            return {
                'success': True,
                'output': json.dumps(vm['hardware'].get_hardware_info(), indent=2)
            }
        
        elif cmd == 'ps' or cmd == 'top':
            processes = vm['processes'].get_process_list()[:15]
            output = "PID\tNAME\t\tUSER\tCPU%\tMEM(MB)\tSTATUS\n"
            output += "-" * 60 + "\n"
            for proc in processes:
                output += f"{proc['pid']}\t{proc['name'][:12]:<12}\t{proc['user'][:8]:<8}\t{proc['cpu_percent']}\t{proc['memory_mb']}\t{proc['status']}\n"
            
            return {'success': True, 'output': output}
        
        elif cmd == 'ifconfig':
            interfaces = vm['networking'].interfaces
            output = ""
            for name, iface in interfaces.items():
                output += f"{name}: {iface['ip']}/{iface['netmask']} ({iface['mac']}) - {iface['status']}\n"
            
            return {'success': True, 'output': output}
        
        elif cmd == 'ping' and args:
            result = vm['networking'].ping(args[0])
            output = f"PING {result['target']}\n"
            for res in result['results']:
                if res['status'] == 'success':
                    output += f"Reply from {result['target']}: time={res['rtt']}ms\n"
                else:
                    output += f"Request timeout\n"
            output += f"\nPacket loss: {result['packet_loss']}%, Average RTT: {result['avg_rtt']}ms"
            
            return {'success': True, 'output': output}
        
        elif cmd == 'netstat':
            result = vm['networking'].netstat()
            output = "Proto\tLocal Address\t\tForeign Address\t\tState\t\tPID/Process\n"
            output += "-" * 80 + "\n"
            for conn in result['connections'][:10]:
                output += f"{conn['protocol']}\t{conn['local_address'][:20]:<20}\t{conn['foreign_address'][:20]:<20}\t{conn['state']:<12}\t{conn['pid']}/{conn['process']}\n"
            
            return {'success': True, 'output': output}
        
        elif cmd == 'df':
            hw_info = vm['hardware'].get_hardware_info()
            storage = hw_info['storage']
            output = f"Filesystem\tSize\tUsed\tAvail\tUse%\n"
            output += f"/dev/sda1\t{storage['total_gb']}G\t{storage['used_gb']}G\t{storage['free_gb']}G\t{storage['usage_percent']:.0f}%\n"
            
            return {'success': True, 'output': output}
        
        elif cmd == 'free':
            hw_info = vm['hardware'].get_hardware_info()
            memory = hw_info['memory']
            output = f"Memory\t\tTotal\tUsed\tFree\n"
            output += f"RAM\t\t{memory['total_mb']}MB\t{memory['used_mb']}MB\t{memory['available_mb']}MB\n"
            
            return {'success': True, 'output': output}
        
        elif cmd == 'uptime':
            metrics = vm['processes'].get_system_metrics()
            uptime_hours = metrics['uptime_seconds'] // 3600
            uptime_mins = (metrics['uptime_seconds'] % 3600) // 60
            load = metrics['load_average']
            
            output = f"System uptime: {uptime_hours}h {uptime_mins}m\n"
            output += f"Load average: {load[0]}, {load[1]}, {load[2]}\n"
            output += f"Processes: {metrics['process_count']}, CPU: {metrics['cpu_usage_percent']}%"
            
            return {'success': True, 'output': output}
        
        else:
            return {
                'success': False,
                'error': f'Unknown command: {cmd}',
                'suggestion': 'Try: hwinfo, ps, top, ifconfig, ping <host>, netstat, df, free, uptime'
            }

def integrate_vm_with_clouddrive(cloud_drive_app):
    """Integrate VM hypervisor with existing CloudDrive application"""
    
    # Initialize hypervisor
    hypervisor = VMHypervisor()
    
    # Add VM web interface
    vm_interface = VMWebInterface(cloud_drive_app.app, hypervisor)
    
    # Add VM link to sidebar navigation
    @cloud_drive_app.app.context_processor
    def inject_vm_features():
        return dict(vm_enabled=True)
    
    return hypervisor, vm_interface

if __name__ == "__main__":
    # Test the VM interface
    from flask import Flask
    
    app = Flask(__name__)
    app.secret_key = 'test_key'
    
    hypervisor = VMHypervisor()
    vm_interface = VMWebInterface(app, hypervisor)
    
    # Create test session
    with app.test_request_context():
        from flask import session
        session['username'] = 'test_user'
        
        # Create test VM
        result = hypervisor.create_vm(
            name="Test VM",
            description="Test virtual machine",
            os_type="Ubuntu 22.04",
            owner="test_user"
        )
        
        if result['success']:
            vm_id = result['vm_id']
            print(f"Created test VM: {vm_id}")
            
            # Start VM
            start_result = hypervisor.start_vm(vm_id)
            print(f"VM start result: {start_result}")
    
    print("VM Web Interface initialized successfully!")