import React, { useState } from 'react';
import { Server, Database, Users, MessageSquare, Smartphone, Cloud, Shield, Activity, Globe, Zap } from 'lucide-react';

const SchoolBridgeArchitecture = () => {
  const [activeTab, setActiveTab] = useState('architecture');
  const [selectedComponent, setSelectedComponent] = useState(null);

  const architectureLayers = [
    {
      name: 'Client Layer',
      icon: Users,
      color: 'bg-blue-500',
      components: [
        { name: 'Web App (React)', desc: 'Desktop/tablet access for teachers & admins' },
        { name: 'Mobile App (Flutter)', desc: 'Cross-platform mobile application' },
        { name: 'SMS/USSD Gateway', desc: 'Offline access for low-income parents' }
      ]
    },
    {
      name: 'Load Balancer Layer',
      icon: Zap,
      color: 'bg-purple-500',
      components: [
        { name: 'AWS ELB / NGINX', desc: 'Routes traffic to nearest healthy region' },
        { name: 'Geographic Routing', desc: 'Latency-based routing for optimal performance' }
      ]
    },
    {
      name: 'Application Layer',
      icon: Server,
      color: 'bg-green-500',
      components: [
        { name: 'Communication Service Nodes', desc: 'Distributed across multiple regions' },
        { name: 'Auth Service', desc: 'JWT-based authentication & authorization' },
        { name: 'Notification Service', desc: 'Push, SMS, and email notifications' },
        { name: 'Analytics Service', desc: 'Performance tracking and reporting' }
      ]
    },
    {
      name: 'Communication Layer',
      icon: MessageSquare,
      color: 'bg-orange-500',
      components: [
        { name: 'WebSocket Server', desc: 'Real-time P2P messaging' },
        { name: 'Message Queue (RabbitMQ)', desc: 'Async message processing' },
        { name: 'Twilio Integration', desc: 'SMS/USSD gateway for offline access' }
      ]
    },
    {
      name: 'Data Layer',
      icon: Database,
      color: 'bg-red-500',
      components: [
        { name: 'PostgreSQL Cluster', desc: 'Primary database with replication' },
        { name: 'MongoDB Replica Set', desc: 'Document store for messages & logs' },
        { name: 'Redis Cache', desc: 'Session storage & real-time data caching' },
        { name: 'S3/Cloud Storage', desc: 'File storage for documents & media' }
      ]
    }
  ];

  const distributedFeatures = [
    {
      title: 'Fault Tolerance',
      icon: Shield,
      description: 'Automatic failover to healthy nodes',
      details: [
        'Health checks every 30 seconds',
        'Automatic node replacement on failure',
        'Data replication across 3+ regions',
        'Zero-downtime deployments'
      ]
    },
    {
      title: 'Scalability',
      icon: Activity,
      description: 'Horizontal scaling across regions',
      details: [
        'Auto-scaling based on load',
        'Microservices architecture',
        'Database sharding by school district',
        'CDN for static assets'
      ]
    },
    {
      title: 'Global Distribution',
      icon: Globe,
      description: 'Multi-region cloud deployment',
      details: [
        'Regional nodes in 3+ continents',
        'Edge caching for faster access',
        'Geo-redundant data storage',
        'Local data compliance (GDPR, etc.)'
      ]
    }
  ];

  const techStack = {
    frontend: [
      { name: 'React', purpose: 'Web application framework' },
      { name: 'Flutter', purpose: 'Cross-platform mobile app' },
      { name: 'Tailwind CSS', purpose: 'Responsive UI styling' }
    ],
    backend: [
      { name: 'Node.js + Express', purpose: 'API server (recommended for WebSocket)' },
      { name: 'Flask (Python)', purpose: 'Alternative for ML/Analytics features' },
      { name: 'JWT', purpose: 'Stateless authentication' }
    ],
    database: [
      { name: 'PostgreSQL', purpose: 'Relational data (students, attendance)' },
      { name: 'MongoDB', purpose: 'Messages, logs, unstructured data' },
      { name: 'Redis', purpose: 'Caching & session management' }
    ],
    infrastructure: [
      { name: 'AWS/GCP/Azure', purpose: 'Multi-region cloud hosting' },
      { name: 'Docker + Kubernetes', purpose: 'Container orchestration' },
      { name: 'Terraform', purpose: 'Infrastructure as code' }
    ],
    communication: [
      { name: 'WebSocket (Socket.io)', purpose: 'Real-time P2P messaging' },
      { name: 'Twilio', purpose: 'SMS/USSD gateway' },
      { name: 'RabbitMQ/Kafka', purpose: 'Message queuing' }
    ]
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-white mb-3">
            SchoolBridge System Architecture
          </h1>
          <p className="text-blue-200 text-lg">
            Distributed Communication Platform for Schools
          </p>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 mb-6 bg-slate-800 p-2 rounded-lg">
          {['architecture', 'features', 'techstack'].map((tab) => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`flex-1 py-3 px-4 rounded-lg font-semibold transition-all ${
                activeTab === tab
                  ? 'bg-blue-600 text-white'
                  : 'text-gray-300 hover:bg-slate-700'
              }`}
            >
              {tab === 'architecture' && 'System Architecture'}
              {tab === 'features' && 'Distributed Features'}
              {tab === 'techstack' && 'Technology Stack'}
            </button>
          ))}
        </div>

        {/* Architecture View */}
        {activeTab === 'architecture' && (
          <div className="space-y-4">
            {architectureLayers.map((layer, idx) => {
              const Icon = layer.icon;
              return (
                <div
                  key={idx}
                  className="bg-slate-800 rounded-xl p-6 border border-slate-700 hover:border-blue-500 transition-all"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className={`${layer.color} p-3 rounded-lg`}>
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-xl font-bold text-white">{layer.name}</h3>
                  </div>
                  <div className="grid md:grid-cols-2 gap-3">
                    {layer.components.map((comp, compIdx) => (
                      <div
                        key={compIdx}
                        className="bg-slate-700 p-4 rounded-lg border border-slate-600 hover:border-blue-400 transition-all cursor-pointer"
                        onClick={() => setSelectedComponent(comp)}
                      >
                        <h4 className="font-semibold text-blue-300 mb-1">{comp.name}</h4>
                        <p className="text-sm text-gray-300">{comp.desc}</p>
                      </div>
                    ))}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Features View */}
        {activeTab === 'features' && (
          <div className="grid md:grid-cols-3 gap-6">
            {distributedFeatures.map((feature, idx) => {
              const Icon = feature.icon;
              return (
                <div
                  key={idx}
                  className="bg-slate-800 rounded-xl p-6 border border-slate-700 hover:border-blue-500 transition-all"
                >
                  <div className="flex items-center gap-3 mb-4">
                    <div className="bg-blue-600 p-3 rounded-lg">
                      <Icon className="w-6 h-6 text-white" />
                    </div>
                    <h3 className="text-lg font-bold text-white">{feature.title}</h3>
                  </div>
                  <p className="text-gray-300 mb-4">{feature.description}</p>
                  <ul className="space-y-2">
                    {feature.details.map((detail, detailIdx) => (
                      <li key={detailIdx} className="flex items-start gap-2 text-sm">
                        <span className="text-blue-400 mt-1">•</span>
                        <span className="text-gray-300">{detail}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              );
            })}
          </div>
        )}

        {/* Tech Stack View */}
        {activeTab === 'techstack' && (
          <div className="space-y-6">
            {Object.entries(techStack).map(([category, technologies]) => (
              <div
                key={category}
                className="bg-slate-800 rounded-xl p-6 border border-slate-700"
              >
                <h3 className="text-xl font-bold text-white mb-4 capitalize">
                  {category}
                </h3>
                <div className="grid md:grid-cols-2 gap-4">
                  {technologies.map((tech, idx) => (
                    <div
                      key={idx}
                      className="bg-slate-700 p-4 rounded-lg border border-slate-600"
                    >
                      <h4 className="font-semibold text-blue-300 mb-2">{tech.name}</h4>
                      <p className="text-sm text-gray-300">{tech.purpose}</p>
                    </div>
                  ))}
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Info Card */}
        <div className="mt-8 bg-gradient-to-r from-blue-600 to-purple-600 rounded-xl p-6 text-white">
          <h3 className="text-xl font-bold mb-2">Key Architecture Highlights</h3>
          <ul className="space-y-2 text-blue-50">
            <li>• <strong>Multi-region deployment</strong> ensures low latency and high availability</li>
            <li>• <strong>Database replication</strong> across 3+ nodes prevents data loss</li>
            <li>• <strong>WebSocket P2P layer</strong> enables real-time communication without central bottleneck</li>
            <li>• <strong>SMS/USSD integration</strong> ensures accessibility for users without internet</li>
            <li>• <strong>Microservices design</strong> allows independent scaling of each service</li>
          </ul>
        </div>
      </div>
    </div>
  );
};

export default SchoolBridgeArchitecture;