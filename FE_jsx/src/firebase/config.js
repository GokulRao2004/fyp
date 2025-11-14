// Firebase Configuration
// Get your config from Firebase Console > Project Settings > Your apps > SDK setup and configuration
import { initializeApp } from "firebase/app";
import { getAuth } from "firebase/auth";

const firebaseConfig = {
  apiKey: "AIzaSyAEZdWwWcOiXFTNF7OQW7JfMSIhQ2J_aXU",
  authDomain: "finalyearpptgenerator.firebaseapp.com",
  projectId: "finalyearpptgenerator",
  storageBucket: "finalyearpptgenerator.firebasestorage.app",
  messagingSenderId: "437834823934",
  appId: "1:437834823934:web:2c270bbe011552af4e0daf",
  measurementId: "G-D5EFXHPFC5"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);

// Initialize Firebase Authentication
export const auth = getAuth(app);

export default app;
