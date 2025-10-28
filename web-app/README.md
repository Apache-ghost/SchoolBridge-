# SchoolBridge Web Application

A modern React web application with Tailwind CSS for the SchoolBridge distributed communication platform.

## Features

### Authentication
- User registration and login
- JWT token management with automatic persistence
- Protected routes and session handling

### Real-time Communication
- **Room Chat**: Join multiple chat rooms, real-time messaging
- **P2P Direct Messages**: Direct user-to-user messaging without server storage
- **Online Presence**: See who's online, real-time user status updates
- **Connection Status**: Visual indicators for WebSocket connection health

### Modern UI/UX
- Responsive design with Tailwind CSS
- Dark theme optimized for extended use
- Real-time message bubbles with timestamps
- User avatars and presence indicators
- Tabbed interface for different chat modes

## Technology Stack

- **React 18**: Modern React with hooks and context
- **Tailwind CSS**: Utility-first CSS framework
- **Socket.IO Client**: Real-time WebSocket communication
- **Axios**: HTTP client for API calls
- **React Router**: Client-side routing
- **Heroicons**: Beautiful SVG icons

## Development Setup

### Prerequisites
- Node.js 18+ 
- npm or yarn

### Local Development
```bash
# Navigate to web-app directory
cd web-app

# Install dependencies
npm install

# Start development server
npm start

# Build for production
npm run build
```

The development server runs at `http://localhost:3000` and proxies API calls to the backend services.

### Environment Variables
Create a `.env.local` file in the web-app directory:
```
REACT_APP_API_BASE=http://localhost:3000
REACT_APP_AUTH_BASE=http://localhost:4000  
REACT_APP_WS_URL=http://localhost:5000
```

## Docker Deployment

The web app is containerized and included in the main docker-compose setup:

```bash
# From project root
docker-compose up --build web-app
```

Access at `http://localhost:8080`

## Architecture Notes

### State Management
- **AuthContext**: Manages authentication state, login/logout, token persistence
- **SocketContext**: Handles WebSocket connections, real-time messaging, user presence

### Real-time Features
- Automatic reconnection on connection loss
- Message delivery confirmations for P2P chat
- Live user presence updates
- Real-time typing indicators (ready for implementation)

### Security
- JWT tokens stored in localStorage with automatic cleanup
- Protected API calls with authorization headers
- Input validation and sanitization

## Key Components

- **App.js**: Main application router and provider setup
- **Login.js**: Authentication form with registration/login toggle
- **Dashboard.js**: Main dashboard with tabs and user management  
- **RoomChat.js**: Multi-room chat interface with room management
- **P2PChat.js**: Direct messaging with online user selection

## API Integration

The web app integrates with the backend services:
- **Auth Service** (port 4000): Registration, login, token validation
- **API Service** (port 3000): Protected endpoints, user profiles
- **WebSocket Service** (port 5000): Real-time messaging, P2P communication

## Production Considerations

- Build optimization with React scripts
- Nginx reverse proxy for API routing
- Static asset serving with proper caching headers
- Error boundaries for graceful error handling
- Accessibility improvements (ARIA labels, keyboard navigation)

## Future Enhancements

- PWA support (service worker, offline capabilities)
- Push notifications
- File sharing and media messages
- Message search and history
- User settings and preferences
- Mobile-responsive improvements