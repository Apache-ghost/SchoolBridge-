const express = require('express');
const multer = require('multer');
const cors = require('cors');
const path = require('path');
const fs = require('fs').promises;
const crypto = require('crypto');
const EventEmitter = require('events');

class ResourceSharingService extends EventEmitter {
    constructor() {
        super();
        this.app = express();
        
        // Resource management
        this.resources = new Map(); // resourceId -> resource data
        this.sharedResources = new Map(); // shareId -> sharing metadata
        this.resourceCategories = new Map(); // categoryId -> category info
        this.accessPermissions = new Map(); // permissionId -> access rules
        this.resourceSubscriptions = new Map(); // schoolId -> subscribed resources
        this.collaborativeSpaces = new Map(); // spaceId -> collaborative workspace
        
        // Analytics and insights
        this.sharingAnalytics = {
            totalShares: 0,
            popularResources: new Map(),
            crossSchoolCollaborations: new Map(),
            resourceImpact: new Map()
        };
        
        // Resource types
        this.resourceTypes = {
            'lesson-plan': { name: 'Lesson Plans', icon: '📚', category: 'academic' },
            'assignment': { name: 'Assignments', icon: '📝', category: 'academic' },
            'presentation': { name: 'Presentations', icon: '📊', category: 'teaching-materials' },
            'video': { name: 'Educational Videos', icon: '🎥', category: 'multimedia' },
            'document': { name: 'Documents', icon: '📄', category: 'general' },
            'template': { name: 'Templates', icon: '📋', category: 'tools' },
            'best-practice': { name: 'Best Practices', icon: '⭐', category: 'knowledge' },
            'policy': { name: 'Policies', icon: '📜', category: 'administrative' },
            'announcement-template': { name: 'Announcement Templates', icon: '📢', category: 'communication' },
            'event-plan': { name: 'Event Plans', icon: '🎉', category: 'events' }
        };
        
        this.setupStorage();
        this.setupMiddleware();
        this.setupRoutes();
        this.initializeCategories();
        
        console.log('🔗 ResourceSharingService initialized for inter-school collaboration');
    }
    
    setupStorage() {
        // Configure multer for file uploads
        this.upload = multer({
            storage: multer.diskStorage({
                destination: async (req, file, cb) => {
                    const uploadsDir = path.join(__dirname, 'uploads');
                    await fs.mkdir(uploadsDir, { recursive: true });
                    cb(null, uploadsDir);
                },
                filename: (req, file, cb) => {
                    const uniqueName = `${Date.now()}-${crypto.randomUUID()}-${file.originalname}`;
                    cb(null, uniqueName);
                }
            }),
            limits: {
                fileSize: 100 * 1024 * 1024 // 100MB limit
            },
            fileFilter: (req, file, cb) => {
                // Allow various educational file types
                const allowedTypes = /\.(pdf|doc|docx|ppt|pptx|xls|xlsx|txt|md|mp4|avi|mov|jpg|jpeg|png|gif)$/i;
                if (allowedTypes.test(file.originalname)) {
                    cb(null, true);
                } else {
                    cb(new Error('File type not supported'), false);
                }
            }
        });
    }
    
    setupMiddleware() {
        this.app.use(cors());
        this.app.use(express.json({ limit: '50mb' }));
        this.app.use('/uploads', express.static(path.join(__dirname, 'uploads')));
    }
    
    setupRoutes() {
        // Health check
        this.app.get('/health', (req, res) => {
            res.json({
                status: 'healthy',
                service: 'resource-sharing',
                timestamp: new Date().toISOString(),
                totalResources: this.resources.size,
                activeShares: Array.from(this.sharedResources.values()).filter(share => share.status === 'active').length,
                collaborativeSpaces: this.collaborativeSpaces.size
            });
        });
        
        // Resource management
        this.app.post('/api/resources/upload', this.upload.single('file'), async (req, res) => {
            try {
                const resource = await this.createResource(req.file, req.body);
                res.json({ success: true, resource });
            } catch (error) {
                console.error('❌ Upload failed:', error);
                res.status(500).json({ error: 'Upload failed' });
            }
        });
        
        this.app.get('/api/resources', (req, res) => {
            const { category, type, schoolId, searchTerm, page = 1, limit = 20 } = req.query;
            const resources = this.getResources({ category, type, schoolId, searchTerm, page: parseInt(page), limit: parseInt(limit) });
            res.json(resources);
        });
        
        this.app.get('/api/resources/:resourceId', (req, res) => {
            const { resourceId } = req.params;
            const resource = this.getResourceById(resourceId);
            if (resource) {
                res.json(resource);
            } else {
                res.status(404).json({ error: 'Resource not found' });
            }
        });
        
        this.app.put('/api/resources/:resourceId', async (req, res) => {
            try {
                const { resourceId } = req.params;
                const updated = await this.updateResource(resourceId, req.body);
                res.json({ success: true, resource: updated });
            } catch (error) {
                console.error('❌ Update failed:', error);
                res.status(500).json({ error: 'Update failed' });
            }
        });
        
        this.app.delete('/api/resources/:resourceId', async (req, res) => {
            try {
                const { resourceId } = req.params;
                await this.deleteResource(resourceId);
                res.json({ success: true });
            } catch (error) {
                console.error('❌ Delete failed:', error);
                res.status(500).json({ error: 'Delete failed' });
            }
        });
        
        // Resource sharing
        this.app.post('/api/resources/:resourceId/share', async (req, res) => {
            try {
                const { resourceId } = req.params;
                const { targetSchools, permissions, message } = req.body;
                const share = await this.shareResource(resourceId, targetSchools, permissions, message);
                res.json({ success: true, share });
            } catch (error) {
                console.error('❌ Sharing failed:', error);
                res.status(500).json({ error: 'Sharing failed' });
            }
        });
        
        this.app.get('/api/resources/shared/incoming', (req, res) => {
            const { schoolId } = req.query;
            const incomingShares = this.getIncomingShares(schoolId);
            res.json({ shares: incomingShares });
        });
        
        this.app.get('/api/resources/shared/outgoing', (req, res) => {
            const { schoolId } = req.query;
            const outgoingShares = this.getOutgoingShares(schoolId);
            res.json({ shares: outgoingShares });
        });
        
        this.app.post('/api/resources/shared/:shareId/accept', async (req, res) => {
            try {
                const { shareId } = req.params;
                const { acceptedBy, schoolId } = req.body;
                await this.acceptResourceShare(shareId, acceptedBy, schoolId);
                res.json({ success: true });
            } catch (error) {
                console.error('❌ Accept failed:', error);
                res.status(500).json({ error: 'Accept failed' });
            }
        });
        
        this.app.post('/api/resources/shared/:shareId/decline', async (req, res) => {
            try {
                const { shareId } = req.params;
                const { declinedBy, schoolId, reason } = req.body;
                await this.declineResourceShare(shareId, declinedBy, schoolId, reason);
                res.json({ success: true });
            } catch (error) {
                console.error('❌ Decline failed:', error);
                res.status(500).json({ error: 'Decline failed' });
            }
        });
        
        // Collaborative spaces
        this.app.post('/api/collaborative-spaces', async (req, res) => {
            try {
                const space = await this.createCollaborativeSpace(req.body);
                res.json({ success: true, space });
            } catch (error) {
                console.error('❌ Space creation failed:', error);
                res.status(500).json({ error: 'Space creation failed' });
            }
        });
        
        this.app.get('/api/collaborative-spaces', (req, res) => {
            const { schoolId, participantSchoolId } = req.query;
            const spaces = this.getCollaborativeSpaces(schoolId, participantSchoolId);
            res.json({ spaces });
        });
        
        this.app.post('/api/collaborative-spaces/:spaceId/join', async (req, res) => {
            try {
                const { spaceId } = req.params;
                const { schoolId, userId } = req.body;
                await this.joinCollaborativeSpace(spaceId, schoolId, userId);
                res.json({ success: true });
            } catch (error) {
                console.error('❌ Join space failed:', error);
                res.status(500).json({ error: 'Join space failed' });
            }
        });
        
        this.app.post('/api/collaborative-spaces/:spaceId/resources', this.upload.single('file'), async (req, res) => {
            try {
                const { spaceId } = req.params;
                const resource = await this.addResourceToSpace(spaceId, req.file, req.body);
                res.json({ success: true, resource });
            } catch (error) {
                console.error('❌ Add to space failed:', error);
                res.status(500).json({ error: 'Add to space failed' });
            }
        });
        
        // Resource discovery and recommendations
        this.app.get('/api/resources/discover', (req, res) => {
            const { schoolId, interests, subjects } = req.query;
            const recommendations = this.discoverResources(schoolId, interests, subjects);
            res.json({ recommendations });
        });
        
        this.app.get('/api/resources/popular', (req, res) => {
            const { timeframe = 'month', category, type } = req.query;
            const popular = this.getPopularResources(timeframe, category, type);
            res.json({ resources: popular });
        });
        
        this.app.get('/api/resources/trending', (req, res) => {
            const { schoolIds, category } = req.query;
            const trending = this.getTrendingResources(schoolIds, category);
            res.json({ resources: trending });
        });
        
        // Analytics and insights
        this.app.get('/api/analytics/sharing', (req, res) => {
            const { schoolId, timeRange } = req.query;
            const analytics = this.getSharingAnalytics(schoolId, timeRange);
            res.json(analytics);
        });
        
        this.app.get('/api/analytics/collaboration', (req, res) => {
            const { districtId, timeRange } = req.query;
            const collaboration = this.getCollaborationAnalytics(districtId, timeRange);
            res.json(collaboration);
        });
        
        this.app.get('/api/analytics/impact', (req, res) => {
            const { resourceId, timeRange } = req.query;
            const impact = this.getResourceImpact(resourceId, timeRange);
            res.json(impact);
        });
        
        // Categories and organization
        this.app.get('/api/categories', (req, res) => {
            const categories = Array.from(this.resourceCategories.values());
            res.json({ categories });
        });
        
        this.app.post('/api/categories', async (req, res) => {
            try {
                const category = await this.createCategory(req.body);
                res.json({ success: true, category });
            } catch (error) {
                console.error('❌ Category creation failed:', error);
                res.status(500).json({ error: 'Category creation failed' });
            }
        });
        
        // Resource subscriptions
        this.app.post('/api/resources/subscribe', async (req, res) => {
            try {
                const { schoolId, resourceIds, categoryIds } = req.body;
                await this.subscribeToResources(schoolId, resourceIds, categoryIds);
                res.json({ success: true });
            } catch (error) {
                console.error('❌ Subscription failed:', error);
                res.status(500).json({ error: 'Subscription failed' });
            }
        });
        
        this.app.get('/api/resources/subscriptions/:schoolId', (req, res) => {
            const { schoolId } = req.params;
            const subscriptions = this.getResourceSubscriptions(schoolId);
            res.json({ subscriptions });
        });
    }
    
    async createResource(file, metadata) {
        const resourceId = `resource_${Date.now()}_${crypto.randomUUID()}`;
        
        const resource = {
            id: resourceId,
            title: metadata.title,
            description: metadata.description,
            type: metadata.type,
            category: metadata.category,
            subjects: metadata.subjects ? metadata.subjects.split(',') : [],
            gradeLevel: metadata.gradeLevel,
            createdBy: metadata.createdBy,
            createdBySchool: metadata.createdBySchool,
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            file: file ? {
                originalName: file.originalname,
                filename: file.filename,
                size: file.size,
                mimetype: file.mimetype,
                path: file.path
            } : null,
            content: metadata.content, // For text-based resources
            tags: metadata.tags ? metadata.tags.split(',').map(tag => tag.trim()) : [],
            visibility: metadata.visibility || 'school', // 'school', 'district', 'public'
            permissions: {
                canView: metadata.canView || 'all',
                canDownload: metadata.canDownload || 'teachers',
                canModify: metadata.canModify || 'creator',
                canShare: metadata.canShare || 'teachers'
            },
            metrics: {
                views: 0,
                downloads: 0,
                shares: 0,
                likes: 0,
                comments: 0
            },
            status: 'active'
        };
        
        this.resources.set(resourceId, resource);
        
        // Update analytics
        this.sharingAnalytics.totalShares++;
        
        console.log(`📚 New resource created: ${resource.title} by ${resource.createdBySchool}`);
        
        // Emit event for real-time notifications
        this.emit('resource-created', resource);
        
        return resource;
    }
    
    getResources(filters = {}) {
        let resources = Array.from(this.resources.values());
        
        // Apply filters
        if (filters.category) {
            resources = resources.filter(r => r.category === filters.category);
        }
        
        if (filters.type) {
            resources = resources.filter(r => r.type === filters.type);
        }
        
        if (filters.schoolId) {
            resources = resources.filter(r => 
                r.createdBySchool === filters.schoolId || 
                r.visibility === 'public' ||
                this.hasAccessPermission(filters.schoolId, r.id)
            );
        }
        
        if (filters.searchTerm) {
            const term = filters.searchTerm.toLowerCase();
            resources = resources.filter(r =>
                r.title.toLowerCase().includes(term) ||
                r.description.toLowerCase().includes(term) ||
                r.tags.some(tag => tag.toLowerCase().includes(term))
            );
        }
        
        // Sort by relevance/popularity
        resources.sort((a, b) => {
            const scoreA = this.calculateResourceScore(a);
            const scoreB = this.calculateResourceScore(b);
            return scoreB - scoreA;
        });
        
        // Pagination
        const startIndex = (filters.page - 1) * filters.limit;
        const paginatedResources = resources.slice(startIndex, startIndex + filters.limit);
        
        return {
            resources: paginatedResources,
            total: resources.length,
            page: filters.page,
            totalPages: Math.ceil(resources.length / filters.limit)
        };
    }
    
    async shareResource(resourceId, targetSchools, permissions, message) {
        const resource = this.resources.get(resourceId);
        if (!resource) {
            throw new Error('Resource not found');
        }
        
        const shareId = `share_${Date.now()}_${crypto.randomUUID()}`;
        
        const share = {
            id: shareId,
            resourceId,
            resource: resource,
            sharedBy: permissions.sharedBy,
            sharedBySchool: permissions.sharedBySchool,
            targetSchools,
            message,
            permissions: {
                canView: permissions.canView !== undefined ? permissions.canView : resource.permissions.canView,
                canDownload: permissions.canDownload !== undefined ? permissions.canDownload : resource.permissions.canDownload,
                canModify: permissions.canModify !== undefined ? permissions.canModify : false,
                canReshare: permissions.canReshare !== undefined ? permissions.canReshare : false
            },
            sharedAt: new Date().toISOString(),
            status: 'pending',
            responses: new Map() // schoolId -> { status, respondedBy, respondedAt, message }
        };
        
        this.sharedResources.set(shareId, share);
        
        // Update resource metrics
        resource.metrics.shares++;
        this.resources.set(resourceId, resource);
        
        // Update analytics
        if (!this.sharingAnalytics.crossSchoolCollaborations.has(share.sharedBySchool)) {
            this.sharingAnalytics.crossSchoolCollaborations.set(share.sharedBySchool, new Set());
        }
        targetSchools.forEach(schoolId => {
            this.sharingAnalytics.crossSchoolCollaborations.get(share.sharedBySchool).add(schoolId);
        });
        
        console.log(`🔗 Resource shared: ${resource.title} to ${targetSchools.length} schools`);
        
        // Emit sharing event
        this.emit('resource-shared', {
            share,
            resource,
            targetSchools
        });
        
        // Send notifications to target schools
        await this.sendSharingNotifications(share);
        
        return share;
    }
    
    async createCollaborativeSpace(spaceData) {
        const spaceId = `space_${Date.now()}_${crypto.randomUUID()}`;
        
        const space = {
            id: spaceId,
            name: spaceData.name,
            description: spaceData.description,
            type: spaceData.type, // 'project', 'curriculum', 'resources', 'discussion'
            createdBy: spaceData.createdBy,
            createdBySchool: spaceData.createdBySchool,
            participantSchools: new Set(spaceData.participantSchools || []),
            members: new Map(), // userId -> { schoolId, role, joinedAt }
            resources: new Map(), // resourceId -> resource
            discussions: new Map(), // discussionId -> discussion
            activities: [], // Activity log
            settings: {
                visibility: spaceData.visibility || 'participants',
                canInvite: spaceData.canInvite || 'moderators',
                canAddResources: spaceData.canAddResources || 'all',
                canModerate: spaceData.canModerate || 'creators'
            },
            createdAt: new Date().toISOString(),
            updatedAt: new Date().toISOString(),
            status: 'active'
        };
        
        this.collaborativeSpaces.set(spaceId, space);
        
        console.log(`🤝 Collaborative space created: ${space.name} with ${space.participantSchools.size} schools`);
        
        // Emit event
        this.emit('collaborative-space-created', space);
        
        return space;
    }
    
    discoverResources(schoolId, interests, subjects) {
        const recommendations = [];
        
        // Get popular resources in similar categories
        const popularInCategory = this.getPopularResourcesByCategory(interests);
        recommendations.push(...popularInCategory.slice(0, 5));
        
        // Get resources from similar schools
        const similarSchools = this.findSimilarSchools(schoolId);
        const resourcesFromSimilar = this.getResourcesFromSchools(similarSchools);
        recommendations.push(...resourcesFromSimilar.slice(0, 5));
        
        // Get trending resources in specified subjects
        if (subjects) {
            const trendingInSubjects = this.getTrendingResourcesBySubjects(subjects);
            recommendations.push(...trendingInSubjects.slice(0, 5));
        }
        
        // Remove duplicates and sort by relevance
        const unique = recommendations.filter((resource, index, self) =>
            index === self.findIndex(r => r.id === resource.id)
        );
        
        return unique.sort((a, b) => this.calculateRecommendationScore(a, schoolId) - this.calculateRecommendationScore(b, schoolId));
    }
    
    getSharingAnalytics(schoolId, timeRange) {
        const resources = Array.from(this.resources.values())
            .filter(r => r.createdBySchool === schoolId);
        
        const shares = Array.from(this.sharedResources.values())
            .filter(s => s.sharedBySchool === schoolId);
        
        return {
            schoolId,
            timeRange,
            summary: {
                totalResourcesCreated: resources.length,
                totalResourcesShared: shares.length,
                totalRecipientsReached: shares.reduce((sum, s) => sum + s.targetSchools.length, 0),
                averageSharesPerResource: resources.length > 0 ? shares.length / resources.length : 0
            },
            resourceBreakdown: {
                byType: this.getResourceBreakdownByType(resources),
                byCategory: this.getResourceBreakdownByCategory(resources),
                byPopularity: resources.sort((a, b) => b.metrics.shares - a.metrics.shares).slice(0, 10)
            },
            collaborationNetwork: {
                partnerSchools: Array.from(new Set(shares.flatMap(s => s.targetSchools))),
                mostActivePartners: this.getMostActivePartners(shares),
                collaborationFrequency: this.getCollaborationFrequency(shares)
            },
            impact: {
                totalViews: resources.reduce((sum, r) => sum + r.metrics.views, 0),
                totalDownloads: resources.reduce((sum, r) => sum + r.metrics.downloads, 0),
                totalLikes: resources.reduce((sum, r) => sum + r.metrics.likes, 0),
                resourcesWithHighImpact: resources.filter(r => r.metrics.views > 100 || r.metrics.downloads > 50)
            }
        };
    }
    
    getCollaborationAnalytics(districtId, timeRange) {
        // Get all schools in district
        const districtSchools = this.getSchoolsInDistrict(districtId);
        
        // Get all collaborative activities
        const collaborativeSpaces = Array.from(this.collaborativeSpaces.values())
            .filter(space => Array.from(space.participantSchools).some(schoolId => districtSchools.includes(schoolId)));
        
        const crossSchoolShares = Array.from(this.sharedResources.values())
            .filter(share => districtSchools.includes(share.sharedBySchool));
        
        return {
            districtId,
            timeRange,
            overview: {
                totalCollaborativeSpaces: collaborativeSpaces.length,
                totalCrossSchoolShares: crossSchoolShares.length,
                participatingSchools: Array.from(new Set([
                    ...collaborativeSpaces.flatMap(space => Array.from(space.participantSchools)),
                    ...crossSchoolShares.flatMap(share => share.targetSchools)
                ])).length,
                activeCollaborations: collaborativeSpaces.filter(space => space.status === 'active').length
            },
            networkAnalysis: {
                collaborationMatrix: this.buildCollaborationMatrix(districtSchools),
                centralSchools: this.identifyCentralSchools(districtSchools),
                collaborationClusters: this.identifyCollaborationClusters(districtSchools),
                networkDensity: this.calculateNetworkDensity(districtSchools)
            },
            resourceFlow: {
                topResourceShares: this.getTopResourceShares(crossSchoolShares),
                resourceCategories: this.getSharedResourceCategories(crossSchoolShares),
                sharingTrends: this.getSharingTrends(crossSchoolShares, timeRange)
            },
            recommendations: [
                {
                    type: 'increase-collaboration',
                    title: 'Increase Cross-School Collaboration',
                    schools: this.identifyLowCollaborationSchools(districtSchools),
                    potential: 'High'
                },
                {
                    type: 'resource-gaps',
                    title: 'Address Resource Gaps',
                    categories: this.identifyResourceGaps(districtSchools),
                    potential: 'Medium'
                }
            ]
        };
    }
    
    initializeCategories() {
        const defaultCategories = [
            {
                id: 'academic',
                name: 'Academic Resources',
                description: 'Curriculum, lesson plans, and educational materials',
                icon: '📚',
                color: '#4CAF50'
            },
            {
                id: 'teaching-materials',
                name: 'Teaching Materials',
                description: 'Presentations, worksheets, and teaching aids',
                icon: '📊',
                color: '#2196F3'
            },
            {
                id: 'multimedia',
                name: 'Multimedia',
                description: 'Videos, audio files, and interactive content',
                icon: '🎥',
                color: '#FF9800'
            },
            {
                id: 'administrative',
                name: 'Administrative',
                description: 'Policies, procedures, and administrative templates',
                icon: '📜',
                color: '#9C27B0'
            },
            {
                id: 'communication',
                name: 'Communication',
                description: 'Announcement templates and communication tools',
                icon: '📢',
                color: '#F44336'
            },
            {
                id: 'events',
                name: 'Events',
                description: 'Event planning resources and templates',
                icon: '🎉',
                color: '#E91E63'
            }
        ];
        
        defaultCategories.forEach(category => {
            this.resourceCategories.set(category.id, category);
        });
        
        console.log(`📁 Initialized ${defaultCategories.length} resource categories`);
    }
    
    // Helper methods
    
    calculateResourceScore(resource) {
        const ageScore = Math.max(0, 30 - Math.floor((Date.now() - new Date(resource.createdAt).getTime()) / (1000 * 60 * 60 * 24)));
        const popularityScore = resource.metrics.views + (resource.metrics.downloads * 2) + (resource.metrics.shares * 5) + (resource.metrics.likes * 3);
        return ageScore + popularityScore;
    }
    
    calculateRecommendationScore(resource, schoolId) {
        // Implement recommendation algorithm based on school similarity, resource popularity, etc.
        return Math.random(); // Simplified for demo
    }
    
    hasAccessPermission(schoolId, resourceId) {
        // Check if school has been granted access to resource through sharing
        return Array.from(this.sharedResources.values()).some(share =>
            share.resourceId === resourceId && 
            share.targetSchools.includes(schoolId) && 
            share.status === 'accepted'
        );
    }
    
    async sendSharingNotifications(share) {
        // Send notifications to target schools about incoming resource share
        console.log(`📧 Sending sharing notifications to ${share.targetSchools.length} schools`);
        // Implementation would integrate with notification service
    }
    
    start(port = 3003) {
        return new Promise((resolve) => {
            this.app.listen(port, () => {
                console.log(`🔗 ResourceSharingService running on port ${port}`);
                console.log('🎯 Inter-school resource sharing features:');
                console.log('   📚 Resource upload and management');
                console.log('   🔗 Cross-school resource sharing');
                console.log('   🤝 Collaborative workspaces');
                console.log('   🔍 Resource discovery and recommendations');
                console.log('   📊 Sharing analytics and insights');
                console.log('   📁 Resource categorization and organization');
                console.log('   🎯 Intelligent content recommendations');
                console.log('   📈 Collaboration network analysis');
                resolve();
            });
        });
    }
}

// Start the service
if (require.main === module) {
    const resourceSharingService = new ResourceSharingService();
    const port = process.env.PORT || 3003;
    
    resourceSharingService.start(port).then(() => {
        console.log('🎉 Inter-school resource sharing system ready!');
    }).catch(error => {
        console.error('❌ Failed to start resource sharing service:', error);
        process.exit(1);
    });
}

module.exports = ResourceSharingService;