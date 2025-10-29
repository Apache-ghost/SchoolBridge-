// Parent Management Service for SchoolBridge
// Handles parent profiles, parent-child relationships, and parent data management

class ParentService {
  constructor() {
    this.storageKey = 'schoolbridge_parents';
    this.relationshipKey = 'schoolbridge_parent_relationships';
    this.initializeStorage();
  }

  initializeStorage() {
    // Initialize parents storage if it doesn't exist
    if (!localStorage.getItem(this.storageKey)) {
      localStorage.setItem(this.storageKey, JSON.stringify([]));
    }
    
    // Initialize relationships storage if it doesn't exist
    if (!localStorage.getItem(this.relationshipKey)) {
      localStorage.setItem(this.relationshipKey, JSON.stringify([]));
    }
  }

  // Generate unique parent ID
  generateParentId() {
    const parents = this.getAllParents().parents;
    const currentYear = new Date().getFullYear();
    let counter = 1;
    
    if (parents.length > 0) {
      const lastParent = parents[parents.length - 1];
      if (lastParent.parentId) {
        const lastNumber = parseInt(lastParent.parentId.split('_')[1]);
        counter = lastNumber + 1;
      }
    }
    
    return `PB${currentYear}_${counter.toString().padStart(3, '0')}`;
  }

  // Register a new parent
  registerParent(parentData) {
    try {
      const parents = JSON.parse(localStorage.getItem(this.storageKey));
      
      // Validate required fields
      if (!parentData.name || !parentData.email || !parentData.phone) {
        return {
          success: false,
          message: 'Name, email, and phone are required fields'
        };
      }

      // Check if parent already exists (by email or phone)
      const existingParent = parents.find(parent => 
        parent.email === parentData.email || parent.phone === parentData.phone
      );
      
      if (existingParent) {
        return {
          success: false,
          message: 'Parent with this email or phone already exists'
        };
      }

      // Create new parent object
      const newParent = {
        id: Date.now().toString(),
        parentId: this.generateParentId(),
        name: parentData.name,
        email: parentData.email,
        phone: parentData.phone,
        address: parentData.address || '',
        occupation: parentData.occupation || '',
        emergencyContact: parentData.emergencyContact || '',
        relationship: parentData.relationship || 'Parent', // Parent, Guardian, etc.
        preferredCommunication: parentData.preferredCommunication || 'email', // email, sms, both
        isActive: true,
        registeredAt: new Date().toISOString(),
        lastLoginAt: null,
        profilePhoto: parentData.profilePhoto || null,
        notes: parentData.notes || ''
      };

      parents.push(newParent);
      localStorage.setItem(this.storageKey, JSON.stringify(parents));

      return {
        success: true,
        message: 'Parent registered successfully',
        parent: newParent
      };
    } catch (error) {
      console.error('Error registering parent:', error);
      return {
        success: false,
        message: 'Failed to register parent'
      };
    }
  }

  // Link parent to child (student)
  linkParentToChild(parentId, studentId, relationshipType = 'Parent') {
    try {
      const relationships = JSON.parse(localStorage.getItem(this.relationshipKey));
      
      // Check if relationship already exists
      const existingRelationship = relationships.find(rel => 
        rel.parentId === parentId && rel.studentId === studentId
      );
      
      if (existingRelationship) {
        return {
          success: false,
          message: 'Relationship already exists'
        };
      }

      // Create new relationship
      const newRelationship = {
        id: Date.now().toString(),
        parentId: parentId,
        studentId: studentId,
        relationshipType: relationshipType, // Parent, Guardian, Emergency Contact, etc.
        isPrimary: relationships.filter(rel => rel.studentId === studentId).length === 0, // First parent is primary
        linkedAt: new Date().toISOString(),
        isActive: true,
        permissions: {
          viewGrades: true,
          viewAttendance: true,
          receiveNotifications: true,
          pickupAuthorization: relationshipType === 'Parent' || relationshipType === 'Guardian',
          emergencyContact: true
        }
      };

      relationships.push(newRelationship);
      localStorage.setItem(this.relationshipKey, JSON.stringify(relationships));

      return {
        success: true,
        message: 'Parent-child relationship created successfully',
        relationship: newRelationship
      };
    } catch (error) {
      console.error('Error linking parent to child:', error);
      return {
        success: false,
        message: 'Failed to create parent-child relationship'
      };
    }
  }

  // Get all parents
  getAllParents() {
    try {
      const parents = JSON.parse(localStorage.getItem(this.storageKey));
      return {
        success: true,
        parents: parents.filter(parent => parent.isActive)
      };
    } catch (error) {
      console.error('Error getting parents:', error);
      return {
        success: false,
        message: 'Failed to retrieve parents',
        parents: []
      };
    }
  }

  // Get parent by ID
  getParentById(parentId) {
    try {
      const parents = JSON.parse(localStorage.getItem(this.storageKey));
      const parent = parents.find(p => p.id === parentId || p.parentId === parentId);
      
      if (!parent) {
        return {
          success: false,
          message: 'Parent not found'
        };
      }

      return {
        success: true,
        parent: parent
      };
    } catch (error) {
      console.error('Error getting parent:', error);
      return {
        success: false,
        message: 'Failed to retrieve parent'
      };
    }
  }

  // Get parent's children
  getParentChildren(parentId) {
    try {
      const relationships = JSON.parse(localStorage.getItem(this.relationshipKey) || '[]');
      
      const parentRelationships = relationships.filter(rel => 
        rel.parentId === parentId && rel.isActive
      );

      const children = [];
      
      // Import studentService dynamically
      import('./studentService').then(({ default: studentService }) => {
        parentRelationships.forEach(rel => {
          const studentResult = studentService.getStudentById(rel.studentId);
          if (studentResult.success) {
            children.push({
              ...studentResult.student,
              relationshipType: rel.relationshipType,
              isPrimary: rel.isPrimary,
              permissions: rel.permissions,
              linkedAt: rel.linkedAt
            });
          }
        });
      }).catch(console.error);

      // For now, let's also check if we can get children from parent's data directly
      const parents = JSON.parse(localStorage.getItem(this.storageKey) || '[]');
      const parent = parents.find(p => p.id === parentId);
      
      if (parent && parent.children) {
        return {
          success: true,
          children: parent.children
        };
      }

      return {
        success: true,
        children: children
      };
    } catch (error) {
      console.error('Error getting parent children:', error);
      return {
        success: false,
        message: 'Failed to retrieve children',
        children: []
      };
    }
  }

  // Get child's parents
  getChildParents(studentId) {
    try {
      const relationships = JSON.parse(localStorage.getItem(this.relationshipKey));
      const parents = JSON.parse(localStorage.getItem(this.storageKey));
      
      const childRelationships = relationships.filter(rel => 
        rel.studentId === studentId && rel.isActive
      );

      const childParents = [];
      childRelationships.forEach(rel => {
        const parent = parents.find(p => p.id === rel.parentId);
        if (parent) {
          childParents.push({
            ...parent,
            relationshipType: rel.relationshipType,
            isPrimary: rel.isPrimary,
            permissions: rel.permissions,
            linkedAt: rel.linkedAt
          });
        }
      });

      return {
        success: true,
        parents: childParents
      };
    } catch (error) {
      console.error('Error getting child parents:', error);
      return {
        success: false,
        message: 'Failed to retrieve parents',
        parents: []
      };
    }
  }

  // Get comprehensive parent profile with children and activities
  getParentProfile(parentId) {
    try {
      const parentResult = this.getParentById(parentId);
      if (!parentResult.success) {
        return parentResult;
      }

      const childrenResult = this.getParentChildren(parentId);
      const parent = parentResult.parent;
      const children = childrenResult.success ? childrenResult.children : [];

      // Get recent activities for this parent
      const recentActivities = this.getParentRecentActivities(parentId);

      // Calculate parent statistics
      const stats = {
        totalChildren: children.length,
        activeChildren: children.filter(child => child.isActive !== false).length,
        averageAttendance: children.length > 0 ? 
          children.reduce((sum, child) => sum + (child.attendanceRate || 95), 0) / children.length : 0,
        totalNotifications: recentActivities.filter(activity => activity.type === 'notification').length,
        unreadMessages: recentActivities.filter(activity => activity.type === 'message' && !activity.read).length
      };

      return {
        success: true,
        profile: {
          parent: parent,
          children: children,
          recentActivities: recentActivities,
          statistics: stats,
          lastUpdated: new Date().toISOString()
        }
      };
    } catch (error) {
      console.error('Error getting parent profile:', error);
      return {
        success: false,
        message: 'Failed to retrieve parent profile'
      };
    }
  }

  // Get parent's recent activities (mock data for now)
  getParentRecentActivities(parentId) {
    // This would typically fetch from a backend API
    // For now, returning mock data based on parent's children
    const activities = [
      {
        id: '1',
        type: 'grade_update',
        title: 'New Grade Posted',
        description: 'Mathematics test grade posted for John Doe',
        timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(), // 2 hours ago
        read: false,
        priority: 'medium'
      },
      {
        id: '2',
        type: 'attendance',
        title: 'Attendance Alert',
        description: 'Student arrived late today',
        timestamp: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(), // 5 hours ago
        read: true,
        priority: 'low'
      },
      {
        id: '3',
        type: 'message',
        title: 'Teacher Message',
        description: 'Message from Math teacher about homework',
        timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(), // 1 day ago
        read: false,
        priority: 'high'
      },
      {
        id: '4',
        type: 'event',
        title: 'School Event',
        description: 'Parent-Teacher Conference scheduled',
        timestamp: new Date(Date.now() - 2 * 24 * 60 * 60 * 1000).toISOString(), // 2 days ago
        read: true,
        priority: 'medium'
      }
    ];

    return activities;
  }

  // Update parent information
  updateParent(parentId, updateData) {
    try {
      const parents = JSON.parse(localStorage.getItem(this.storageKey));
      const parentIndex = parents.findIndex(p => p.id === parentId || p.parentId === parentId);
      
      if (parentIndex === -1) {
        return {
          success: false,
          message: 'Parent not found'
        };
      }

      // Update parent data
      parents[parentIndex] = {
        ...parents[parentIndex],
        ...updateData,
        updatedAt: new Date().toISOString()
      };

      localStorage.setItem(this.storageKey, JSON.stringify(parents));

      return {
        success: true,
        message: 'Parent updated successfully',
        parent: parents[parentIndex]
      };
    } catch (error) {
      console.error('Error updating parent:', error);
      return {
        success: false,
        message: 'Failed to update parent'
      };
    }
  }

  // Search parents
  searchParents(query) {
    try {
      const parents = JSON.parse(localStorage.getItem(this.storageKey));
      const searchQuery = query.toLowerCase().trim();
      
      if (!searchQuery) {
        return this.getAllParents();
      }

      const filteredParents = parents.filter(parent => 
        parent.isActive && (
          parent.name.toLowerCase().includes(searchQuery) ||
          parent.email.toLowerCase().includes(searchQuery) ||
          parent.phone.includes(searchQuery) ||
          parent.parentId.toLowerCase().includes(searchQuery)
        )
      );

      return {
        success: true,
        parents: filteredParents
      };
    } catch (error) {
      console.error('Error searching parents:', error);
      return {
        success: false,
        message: 'Failed to search parents',
        parents: []
      };
    }
  }

  // Get parent statistics
  getParentStatistics() {
    try {
      const parents = JSON.parse(localStorage.getItem(this.storageKey));
      const relationships = JSON.parse(localStorage.getItem(this.relationshipKey));
      
      const totalParents = parents.filter(p => p.isActive).length;
      const activeParents = parents.filter(p => p.isActive && p.lastLoginAt).length;
      const totalRelationships = relationships.filter(r => r.isActive).length;
      
      // Communication preferences
      const emailPreferred = parents.filter(p => p.preferredCommunication === 'email').length;
      const smsPreferred = parents.filter(p => p.preferredCommunication === 'sms').length;
      const bothPreferred = parents.filter(p => p.preferredCommunication === 'both').length;

      // Relationship types
      const relationshipStats = {};
      relationships.forEach(rel => {
        relationshipStats[rel.relationshipType] = (relationshipStats[rel.relationshipType] || 0) + 1;
      });

      return {
        success: true,
        statistics: {
          totalParents,
          activeParents,
          totalRelationships,
          communicationPreferences: {
            email: emailPreferred,
            sms: smsPreferred,
            both: bothPreferred
          },
          relationshipTypes: relationshipStats,
          averageChildrenPerParent: totalParents > 0 ? (totalRelationships / totalParents).toFixed(2) : 0
        }
      };
    } catch (error) {
      console.error('Error getting parent statistics:', error);
      return {
        success: false,
        message: 'Failed to get statistics',
        statistics: {}
      };
    }
  }

  // Deactivate parent (soft delete)
  deactivateParent(parentId) {
    try {
      const parents = JSON.parse(localStorage.getItem(this.storageKey));
      const parentIndex = parents.findIndex(p => p.id === parentId || p.parentId === parentId);
      
      if (parentIndex === -1) {
        return {
          success: false,
          message: 'Parent not found'
        };
      }

      parents[parentIndex].isActive = false;
      parents[parentIndex].deactivatedAt = new Date().toISOString();
      
      localStorage.setItem(this.storageKey, JSON.stringify(parents));

      return {
        success: true,
        message: 'Parent deactivated successfully'
      };
    } catch (error) {
      console.error('Error deactivating parent:', error);
      return {
        success: false,
        message: 'Failed to deactivate parent'
      };
    }
  }
}

const parentService = new ParentService();
export default parentService;