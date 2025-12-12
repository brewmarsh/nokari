import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";
import { getFirestore } from "firebase/firestore";
import { getStorage } from "firebase/storage";

// Your web app's Firebase configuration
// For Firebase JS SDK v7.20.0 and later, measurementId is optional
const firebaseConfig = {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID,
  storageBucket: import.meta.env.VITE_FIREBASE_STORAGE_BUCKET,
  messagingSenderId: import.meta.env.VITE_FIREBASE_MESSAGING_SENDER_ID,
  appId: import.meta.env.VITE_FIREBASE_APP_ID,
  measurementId: import.meta.env.VITE_FIREBASE_MEASUREMENT_ID
};

let app;
let auth;
let db;
let storage;
let initializationError = null;

try {
  // Check for required configuration
  if (!firebaseConfig.apiKey) {
    throw new Error("VITE_FIREBASE_API_KEY is missing. Check your build environment variables.");
  }

  // Check if running with default test credentials
  if (firebaseConfig.apiKey === 'test-api-key') {
    throw new Error("Application is running with default test credentials. Please configure your .env file with valid Firebase credentials.");
  }

  // Verify other configuration values if apiKey is valid
  // We skip measurementId as it is optional
  const requiredKeys = ['authDomain', 'projectId', 'storageBucket', 'messagingSenderId', 'appId'];
  const missingKeys = requiredKeys.filter(key => {
    const value = firebaseConfig[key];
    return !value || value.startsWith('test-');
  });

  if (missingKeys.length > 0) {
    throw new Error(`Invalid Firebase configuration. The following keys are missing or using default test values: ${missingKeys.join(', ')}. Please update your .env file.`);
  }

  // Initialize Firebase
  app = initializeApp(firebaseConfig);

  // Export Firebase services
  auth = getAuth(app);
  db = getFirestore(app);
  storage = getStorage(app);
} catch (error) {
  console.error("Firebase initialization failed:", error);
  initializationError = error;
}

export { auth, db, storage, initializationError };
