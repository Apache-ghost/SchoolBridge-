// Firebase configuration
import { initializeApp } from "firebase/app";
import { getAnalytics } from "firebase/analytics";
import { getFirestore } from "firebase/firestore";
import { getAuth } from "firebase/auth";

// Your web app's Firebase configuration
const firebaseConfig = {
  apiKey: "AIzaSyA3JFdDRQDRN6SOViENr617uswS97qK2Jo",
  authDomain: "cloudstorage-fcbef.firebaseapp.com",
  projectId: "cloudstorage-fcbef",
  storageBucket: "cloudstorage-fcbef.firebasestorage.app",
  messagingSenderId: "802240843944",
  appId: "1:802240843944:web:05201cd426013256b3f29d",
  measurementId: "G-4070N1JY8P"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const analytics = getAnalytics(app);
const db = getFirestore(app);
const auth = getAuth(app);

export { db, auth, analytics };