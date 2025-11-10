"""
Storage Service Package
Modular storage system with organized class structure
"""

# Import all the main classes for easy access
from .storage_node import StorageNode
from .file_transfer import FileTransfer, TransferResult, TransferStatus
from .network import StorageNetwork, NetworkConnection, NetworkStats
from .storage_service_manager import StorageServiceManager

# Legacy imports for backward compatibility
from .storage_virtual_node import StorageVirtualNode
from .storage_virtual_network import StorageVirtualNetwork

__version__ = "2.0.0"
__author__ = "SOP"

__all__ = [
    # New modular classes
    'StorageNode',
    'FileTransfer',
    'TransferResult', 
    'TransferStatus',
    'StorageNetwork',
    'NetworkConnection',
    'NetworkStats',
    'StorageServiceManager',
    
    # Legacy classes
    'StorageVirtualNode',
    'StorageVirtualNetwork'
]