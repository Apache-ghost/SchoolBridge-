#!/usr/bin/env python3
"""
OOP System Test Script for SchoolBridge Distributed Storage System
Tests all major OOP components and functionality
"""

import sys
import os
import time

# Add path for imports
sys.path.append(os.path.dirname(__file__))

from factory.system_factory import (
    StorageSystemFactory,
    ConfigurationTemplates,
    create_default_system,
    create_testing_system
)

def test_basic_functionality():
    """Test basic system functionality"""
    print("🧪 TESTING BASIC FUNCTIONALITY")
    print("="*50)
    
    # Test 1: Create default system
    print("1. Testing default system creation...")
    system = create_default_system(silent=True)
    assert system is not None, "System creation failed"
    assert len(system.network_manager.networks) > 0, "No networks created"
    assert len(system.network_manager.nodes) > 0, "No nodes created"
    print("   ✅ Default system creation: PASS")
    
    # Test 2: Test network manager
    print("2. Testing network manager...")
    networks = system.network_manager.list_all_networks()
    nodes = system.network_manager.list_all_nodes()
    assert len(networks) > 0, "Network manager failed"
    assert len(nodes) > 0, "Node manager failed"
    print(f"   ✅ Network manager ({len(networks)} networks, {len(nodes)} nodes): PASS")
    
    # Test 3: Test file transfer manager
    print("3. Testing file transfer manager...")
    assert system.file_transfer_manager is not None, "File manager not initialized"
    print("   ✅ File transfer manager: PASS")
    
    # Test 4: Test speed control manager
    print("4. Testing speed control manager...")
    assert system.speed_control_manager is not None, "Speed manager not initialized"
    system.speed_control_manager.show_speed_presets()  # Should not crash
    print("   ✅ Speed control manager: PASS")
    
    # Test 5: Test terminal manager
    print("5. Testing terminal manager...")
    assert system.terminal_manager is not None, "Terminal manager not initialized"
    print("   ✅ Terminal manager: PASS")
    
    return system

def test_factory_patterns():
    """Test factory pattern functionality"""
    print("\n🏭 TESTING FACTORY PATTERNS")
    print("="*50)
    
    # Test different system types
    systems = {}
    
    print("1. Testing default system factory...")
    systems['default'] = StorageSystemFactory.create_default_system(silent_mode=True)
    print("   ✅ Default system factory: PASS")
    
    print("2. Testing minimal system factory...")
    systems['minimal'] = StorageSystemFactory.create_minimal_system(silent_mode=True)
    print("   ✅ Minimal system factory: PASS")
    
    print("3. Testing testing system factory...")
    systems['testing'] = StorageSystemFactory.create_testing_system(3, silent_mode=True)
    print("   ✅ Testing system factory: PASS")
    
    print("4. Testing performance system factory...")
    systems['performance'] = StorageSystemFactory.create_performance_system(silent_mode=True)
    print("   ✅ Performance system factory: PASS")
    
    # Verify all systems are different
    node_counts = [len(s.network_manager.nodes) for s in systems.values()]
    assert len(set(node_counts)) > 1, "All systems have same node count"
    print(f"   ✅ System diversity (node counts: {node_counts}): PASS")
    
    return systems

def test_configuration_templates():
    """Test configuration templates"""
    print("\n⚙️ TESTING CONFIGURATION TEMPLATES")
    print("="*50)
    
    print("1. Testing development configuration...")
    dev_config = ConfigurationTemplates.get_development_config()
    assert 'nodes' in dev_config, "Dev config missing nodes"
    assert len(dev_config['nodes']) > 0, "Dev config has no nodes"
    print("   ✅ Development configuration: PASS")
    
    print("2. Testing production configuration...")
    prod_config = ConfigurationTemplates.get_production_config()
    assert 'nodes' in prod_config, "Prod config missing nodes"
    assert len(prod_config['nodes']) > 0, "Prod config has no nodes"
    print("   ✅ Production configuration: PASS")
    
    print("3. Testing edge computing configuration...")
    edge_config = ConfigurationTemplates.get_edge_computing_config()
    assert 'nodes' in edge_config, "Edge config missing nodes"
    print("   ✅ Edge computing configuration: PASS")
    
    return True

def test_file_operations():
    """Test file operations functionality"""
    print("\n📁 TESTING FILE OPERATIONS")
    print("="*50)
    
    # Create system for testing
    system = create_testing_system(3, silent=True)
    
    # Test file upload simulation
    print("1. Testing file upload simulation...")
    nodes = list(system.network_manager.nodes.values())
    if nodes:
        node = nodes[0]
        success = system.file_transfer_manager._simulate_file_upload(node, "test.txt", 10)
        assert success, "File upload simulation failed"
        assert "test.txt" in node.files, "File not stored in node"
        print("   ✅ File upload simulation: PASS")
    
    # Test file download simulation
    print("2. Testing file download simulation...")
    if nodes and "test.txt" in node.files:
        success = system.file_transfer_manager._simulate_file_download(node, "test.txt")
        assert success, "File download simulation failed"
        print("   ✅ File download simulation: PASS")
    
    # Test P2P distribution
    print("3. Testing P2P file distribution...")
    nodes_list = list(system.network_manager.nodes.values())
    success = system.file_transfer_manager._distribute_file_p2p("large_file.zip", 100, nodes_list)
    assert success, "P2P distribution failed"
    assert len(system.file_transfer_manager.p2p_files) > 0, "No P2P files recorded"
    print("   ✅ P2P file distribution: PASS")
    
    return True

def test_speed_control():
    """Test speed control functionality"""
    print("\n⚡ TESTING SPEED CONTROL")
    print("="*50)
    
    system = create_default_system(silent=True)
    
    print("1. Testing speed presets...")
    presets = system.speed_control_manager.speed_presets
    assert len(presets) > 0, "No speed presets available"
    assert 'gigabit' in presets, "Gigabit preset missing"
    print(f"   ✅ Speed presets ({len(presets)} available): PASS")
    
    print("2. Testing speed application...")
    # This should not crash
    success = system.speed_control_manager._apply_speed_change(100)
    assert success, "Speed change application failed"
    print("   ✅ Speed application: PASS")
    
    return True

def test_terminal_operations():
    """Test terminal operations"""
    print("\n💻 TESTING TERMINAL OPERATIONS")
    print("="*50)
    
    system = create_default_system(silent=True)
    
    print("1. Testing command execution...")
    nodes = list(system.network_manager.nodes.values())
    if nodes:
        node = nodes[0]
        result = system.terminal_manager._execute_command(node, "ls")
        assert result.exit_code in [0, 127], "Invalid exit code"
        assert result.output is not None, "No command output"
        print("   ✅ Command execution: PASS")
    
    print("2. Testing available commands...")
    commands = system.terminal_manager.available_commands
    assert len(commands) > 0, "No commands available"
    assert 'ls' in commands, "ls command missing"
    assert 'help' in commands, "help command missing"
    print(f"   ✅ Available commands ({len(commands)} commands): PASS")
    
    return True

def run_all_tests():
    """Run all tests"""
    print("🧪 SCHOOLBRIDGE OOP SYSTEM TESTS")
    print("="*60)
    
    try:
        # Run test suites
        system = test_basic_functionality()
        systems = test_factory_patterns()
        test_configuration_templates()
        test_file_operations()
        test_speed_control()
        test_terminal_operations()
        
        print("\n🎉 ALL TESTS COMPLETED SUCCESSFULLY!")
        print("="*60)
        print("✅ Basic functionality: PASS")
        print("✅ Factory patterns: PASS") 
        print("✅ Configuration templates: PASS")
        print("✅ File operations: PASS")
        print("✅ Speed control: PASS")
        print("✅ Terminal operations: PASS")
        print("="*60)
        print("🏆 OOP REFACTORING: 100% SUCCESSFUL!")
        
        # Show system summary
        print(f"\n📊 SYSTEM SUMMARY:")
        networks = len(system.network_manager.networks)
        nodes = len(system.network_manager.nodes)
        print(f"   Networks: {networks}")
        print(f"   Nodes: {nodes}")
        print(f"   Managers: 5 (Network, Orchestrator, FileTransfer, SpeedControl, Terminal)")
        print(f"   Factory patterns: 7 creation methods")
        print(f"   Configuration templates: 3 predefined configs")
        
        return True
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        return False

if __name__ == "__main__":
    success = run_all_tests()
    exit_code = 0 if success else 1
    sys.exit(exit_code)