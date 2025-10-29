// Firebase Configuration for SchoolBridge Frontend
// Import the functions you need from the SDKs you need
import { initializeApp } from "firebase/app";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";
import { getAnalytics } from "firebase/analytics";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyAX8SMZyXOs8bj6oFUxtRGKLf3kUAAuPPg",
  authDomain: "schoolbridge-8746c.firebaseapp.com",
  projectId: "schoolbridge-8746c",
  storageBucket: "schoolbridge-8746c.firebasestorage.app",
  messagingSenderId: "415210830131",
  appId: "1:415210830131:web:36290febd880683e5e6646",
  measurementId: "G-1SW2CKQRBG"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase services
export const db = getFirestore(app);
export const auth = getAuth(app);
export const analytics = getAnalytics(app);

// Parent Access Configuration
export const PARENT_ACCESS_CODE = "ICTU2032!";

// Export the Firebase app instance
export default app;

// SchoolBridge Communication Service Configuration
export const COMMUNICATION_CONFIG = {
  // Communication Service URL (adjust based on environment)
  serviceUrl: process.env.REACT_APP_COMMUNICATION_SERVICE_URL || 'http://localhost:6000',
  
  // Real-time connection settings
  socketOptions: {
    transports: ['websocket', 'polling'],
    upgrade: true,
    reconnection: true,
    reconnectionAttempts: 5,
    reconnectionDelay: 1000,
    timeout: 20000
  },
  
  // School node configuration (can be set per school)
  defaultSchoolCode: process.env.REACT_APP_SCHOOL_CODE || 'MAIN001',
  defaultDistrict: process.env.REACT_APP_SCHOOL_DISTRICT || 'district-main'
};