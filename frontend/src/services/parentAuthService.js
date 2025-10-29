import { auth, db, PARENT_ACCESS_CODE } from '../firebase/config';
import { 
    createUserWithEmailAndPassword,
    signInWithEmailAndPassword,
    signInAnonymously, 
    signOut,
    onAuthStateChanged 
} from 'firebase/auth';
import { 
    doc, 
    setDoc, 
    getDoc, 
    collection,
    query,
    where,
    getDocs,
    updateDoc,
    serverTimestamp 
} from 'firebase/firestore';

class ParentAuthService {
    constructor() {
        this.currentParent = null;
        this.authStateListeners = [];
        
        // Listen for auth state changes
        onAuthStateChanged(auth, (user) => {
            if (user) {
                this.loadParentData(user.uid);
            } else {
                this.currentParent = null;
            }
            this.notifyAuthStateListeners(this.currentParent);
        });
    }

    // Register new parent with email and password
    async registerParent(email, password, parentName, phoneNumber, accessCode) {
        try {
            // Validate access code first
            if (accessCode !== PARENT_ACCESS_CODE) {
                throw new Error('Invalid access code. Please contact your school for the correct code.');
            }

            // Validate required fields
            if (!email || !password || !parentName || !phoneNumber) {
                throw new Error('All fields are required: email, password, name, and phone number.');
            }

            // Clean phone number
            const cleanPhone = this.cleanPhoneNumber(phoneNumber);
            
            if (!this.isValidPhoneNumber(cleanPhone)) {
                throw new Error('Please enter a valid phone number.');
            }

            // Check if parent already exists with this email or phone
            const existingParent = await this.findParentByEmailOrPhone(email, cleanPhone);
            if (existingParent) {
                throw new Error('An account already exists with this email or phone number.');
            }

            // Create Firebase auth user with email/password
            const userCredential = await createUserWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;

            // Create parent document
            const parentData = {
                uid: user.uid,
                email: email,
                phoneNumber: cleanPhone,
                name: parentName,
                authType: 'email',
                createdAt: new Date().toISOString(),
                lastLogin: new Date().toISOString(),
                children: [],
                notifications: [],
                preferences: {
                    smsEnabled: true,
                    emailEnabled: true,
                    language: 'en'
                }
            };

            // Save parent data in Firestore
            await setDoc(doc(db, 'parents', user.uid), {
                ...parentData,
                updatedAt: serverTimestamp()
            });

            // Maintain phone number index for SMS notifications
            await setDoc(doc(db, 'parentsByPhone', cleanPhone), {
                uid: user.uid,
                phoneNumber: cleanPhone,
                email: email,
                updatedAt: serverTimestamp()
            });

            this.currentParent = parentData;
            
            return {
                success: true,
                parent: this.currentParent,
                message: 'Account created successfully!'
            };

        } catch (error) {
            console.error('Registration error:', error);
            let errorMessage = error.message || 'Registration failed. Please try again.';
            
            if (error.code === 'auth/email-already-in-use') {
                errorMessage = 'An account with this email already exists.';
            } else if (error.code === 'auth/weak-password') {
                errorMessage = 'Password should be at least 6 characters.';
            } else if (error.code === 'auth/invalid-email') {
                errorMessage = 'Please enter a valid email address.';
            }

            return {
                success: false,
                error: errorMessage
            };
        }
    }

    // Login with email and password
    async loginWithEmail(email, password, accessCode) {
        try {
            // Validate access code first
            if (accessCode !== PARENT_ACCESS_CODE) {
                throw new Error('Invalid access code. Please contact your school for the correct code.');
            }

            // Sign in with Firebase Auth
            const userCredential = await signInWithEmailAndPassword(auth, email, password);
            const user = userCredential.user;

            // Load parent data
            const parentDoc = await getDoc(doc(db, 'parents', user.uid));
            
            if (!parentDoc.exists()) {
                throw new Error('Parent account not found. Please contact your school.');
            }

            const parentData = { ...parentDoc.data(), uid: user.uid };

            // Update last login
            await updateDoc(doc(db, 'parents', user.uid), {
                lastLogin: new Date().toISOString(),
                updatedAt: serverTimestamp()
            });

            this.currentParent = parentData;

            return {
                success: true,
                parent: this.currentParent,
                message: 'Successfully logged in!'
            };

        } catch (error) {
            console.error('Email login error:', error);
            let errorMessage = error.message || 'Login failed. Please try again.';
            
            if (error.code === 'auth/user-not-found' || error.code === 'auth/wrong-password') {
                errorMessage = 'Invalid email or password.';
            } else if (error.code === 'auth/invalid-email') {
                errorMessage = 'Please enter a valid email address.';
            } else if (error.code === 'auth/too-many-requests') {
                errorMessage = 'Too many failed attempts. Please try again later.';
            }

            return {
                success: false,
                error: errorMessage
            };
        }
    }

    // Authenticate parent with phone number and access code (alternative method)
    async authenticateParent(phoneNumber, accessCode, parentName = '') {
        try {
            // Validate access code
            if (accessCode !== PARENT_ACCESS_CODE) {
                throw new Error('Invalid access code. Please contact your school for the correct code.');
            }

            // Clean phone number (remove spaces, dashes, etc.)
            const cleanPhone = this.cleanPhoneNumber(phoneNumber);
            
            if (!this.isValidPhoneNumber(cleanPhone)) {
                throw new Error('Please enter a valid phone number.');
            }

            // Check if parent already exists
            let parentData = await this.findParentByPhone(cleanPhone);
            
            if (!parentData) {
                // Create new parent record if doesn't exist
                parentData = {
                    phoneNumber: cleanPhone,
                    name: parentName || `Parent (${cleanPhone})`,
                    authType: 'phone',
                    createdAt: new Date().toISOString(),
                    lastLogin: new Date().toISOString(),
                    children: [],
                    notifications: [],
                    preferences: {
                        smsEnabled: true,
                        emailEnabled: false,
                        language: 'en'
                    }
                };
            } else {
                // Update last login
                parentData.lastLogin = new Date().toISOString();
            }

            // Sign in anonymously (we'll link this to phone number)
            const userCredential = await signInAnonymously(auth);
            const user = userCredential.user;

            // Save/update parent data in Firestore
            await setDoc(doc(db, 'parents', user.uid), {
                ...parentData,
                uid: user.uid,
                updatedAt: serverTimestamp()
            });

            // Also maintain phone number index for quick lookup
            await setDoc(doc(db, 'parentsByPhone', cleanPhone), {
                uid: user.uid,
                phoneNumber: cleanPhone,
                updatedAt: serverTimestamp()
            });

            this.currentParent = { ...parentData, uid: user.uid };
            
            return {
                success: true,
                parent: this.currentParent,
                message: 'Successfully logged in!'
            };

        } catch (error) {
            console.error('Parent authentication error:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    // Find parent by phone number
    async findParentByPhone(phoneNumber) {
        try {
            const phoneDoc = await getDoc(doc(db, 'parentsByPhone', phoneNumber));
            if (phoneDoc.exists()) {
                const { uid } = phoneDoc.data();
                const parentDoc = await getDoc(doc(db, 'parents', uid));
                if (parentDoc.exists()) {
                    return { ...parentDoc.data(), uid };
                }
            }
            return null;
        } catch (error) {
            console.error('Error finding parent:', error);
            return null;
        }
    }

    // Find parent by email or phone number
    async findParentByEmailOrPhone(email, phoneNumber) {
        try {
            // First check by email in parents collection
            const parentsRef = collection(db, 'parents');
            const emailQuery = query(parentsRef, where('email', '==', email));
            const emailResults = await getDocs(emailQuery);
            
            if (!emailResults.empty) {
                const parentDoc = emailResults.docs[0];
                return { ...parentDoc.data(), uid: parentDoc.id };
            }

            // Then check by phone number
            return await this.findParentByPhone(phoneNumber);
            
        } catch (error) {
            console.error('Error finding parent by email or phone:', error);
            return null;
        }
    }

    // Load parent data by UID
    async loadParentData(uid) {
        try {
            const parentDoc = await getDoc(doc(db, 'parents', uid));
            if (parentDoc.exists()) {
                this.currentParent = { ...parentDoc.data(), uid };
            }
        } catch (error) {
            console.error('Error loading parent data:', error);
        }
    }

    // Get parent's children/students
    async getParentChildren(parentUid = null) {
        try {
            const uid = parentUid || this.currentParent?.uid;
            if (!uid) throw new Error('No parent authenticated');

            // Query students where parent field matches this parent's UID
            const studentsQuery = query(
                collection(db, 'students'),
                where('parentUid', '==', uid)
            );
            
            const querySnapshot = await getDocs(studentsQuery);
            const children = [];
            
            querySnapshot.forEach((doc) => {
                children.push({
                    id: doc.id,
                    ...doc.data()
                });
            });

            return children;
        } catch (error) {
            console.error('Error getting parent children:', error);
            return [];
        }
    }

    // Get communications/notifications for parent
    async getParentCommunications(parentUid = null, limit = 50) {
        try {
            const uid = parentUid || this.currentParent?.uid;
            if (!uid) throw new Error('No parent authenticated');

            const commQuery = query(
                collection(db, 'communications'),
                where('parentUid', '==', uid),
                // orderBy('createdAt', 'desc'),
                // limit(limit)
            );

            const querySnapshot = await getDocs(commQuery);
            const communications = [];

            querySnapshot.forEach((doc) => {
                communications.push({
                    id: doc.id,
                    ...doc.data()
                });
            });

            // Sort by createdAt (since orderBy might not work with compound queries)
            communications.sort((a, b) => {
                const dateA = new Date(a.createdAt || 0);
                const dateB = new Date(b.createdAt || 0);
                return dateB - dateA;
            });

            return communications.slice(0, limit);
        } catch (error) {
            console.error('Error getting communications:', error);
            return [];
        }
    }

    // Mark communication as read
    async markCommunicationAsRead(communicationId) {
        try {
            await updateDoc(doc(db, 'communications', communicationId), {
                readAt: serverTimestamp(),
                read: true
            });
            return true;
        } catch (error) {
            console.error('Error marking communication as read:', error);
            return false;
        }
    }

    // Update parent preferences
    async updateParentPreferences(preferences) {
        try {
            if (!this.currentParent?.uid) throw new Error('No parent authenticated');

            await updateDoc(doc(db, 'parents', this.currentParent.uid), {
                preferences: {
                    ...this.currentParent.preferences,
                    ...preferences
                },
                updatedAt: serverTimestamp()
            });

            this.currentParent.preferences = {
                ...this.currentParent.preferences,
                ...preferences
            };

            return true;
        } catch (error) {
            console.error('Error updating preferences:', error);
            return false;
        }
    }

    // Link child/student to parent
    async linkChildToParent(childId, childName) {
        try {
            if (!this.currentParent?.uid) throw new Error('No parent authenticated');

            // Update student record to include parent UID
            await updateDoc(doc(db, 'students', childId), {
                parentUid: this.currentParent.uid,
                parentPhone: this.currentParent.phoneNumber,
                updatedAt: serverTimestamp()
            });

            // Update parent's children list
            const currentChildren = this.currentParent.children || [];
            if (!currentChildren.find(child => child.id === childId)) {
                currentChildren.push({
                    id: childId,
                    name: childName,
                    linkedAt: new Date().toISOString()
                });

                await updateDoc(doc(db, 'parents', this.currentParent.uid), {
                    children: currentChildren,
                    updatedAt: serverTimestamp()
                });

                this.currentParent.children = currentChildren;
            }

            return true;
        } catch (error) {
            console.error('Error linking child to parent:', error);
            return false;
        }
    }

    // Sign out parent
    async signOutParent() {
        try {
            await signOut(auth);
            this.currentParent = null;
            return true;
        } catch (error) {
            console.error('Error signing out:', error);
            return false;
        }
    }

    // Check if user is authenticated
    isAuthenticated() {
        return !!this.currentParent;
    }

    // Get current parent
    getCurrentParent() {
        return this.currentParent;
    }

    // Auth state listener management
    addAuthStateListener(listener) {
        this.authStateListeners.push(listener);
    }

    removeAuthStateListener(listener) {
        this.authStateListeners = this.authStateListeners.filter(l => l !== listener);
    }

    notifyAuthStateListeners(parent) {
        this.authStateListeners.forEach(listener => listener(parent));
    }

    // Utility functions
    cleanPhoneNumber(phone) {
        return phone.replace(/\D/g, '');
    }

    isValidPhoneNumber(phone) {
        // Basic validation for international phone numbers (7-15 digits)
        return /^\d{7,15}$/.test(phone);
    }

    formatPhoneNumber(phone) {
        const cleaned = this.cleanPhoneNumber(phone);
        if (cleaned.length === 11 && cleaned.startsWith('234')) {
            // Nigerian number format
            return `+234 ${cleaned.slice(3, 6)} ${cleaned.slice(6, 9)} ${cleaned.slice(9)}`;
        } else if (cleaned.length === 10) {
            // Local format
            return `${cleaned.slice(0, 4)} ${cleaned.slice(4, 7)} ${cleaned.slice(7)}`;
        }
        return phone;
    }
}

// Create singleton instance
const parentAuthService = new ParentAuthService();

export default parentAuthService;