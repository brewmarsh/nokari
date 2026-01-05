import React, { useState, useEffect, useCallback, memo, useRef, Suspense } from 'react';
import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import './App.css';
import { auth, initializationError, db } from './firebaseConfig';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { doc, getDoc, setDoc } from 'firebase/firestore';
import UserProfileIcon from './components/UserProfileIcon.jsx';
import api from './services/api';
import lazyWithRetry from './utils/lazyWithRetry';

// Lazy load components
const Login = lazyWithRetry(() => import('./components/Login.jsx'));
const Register = lazyWithRetry(() => import('./components/Register.jsx'));
const Dashboard = lazyWithRetry(() => import('./components/Dashboard.jsx'));
const Onboarding = lazyWithRetry(() => import('./components/Onboarding.jsx'));
const Documents = lazyWithRetry(() => import('./components/Documents.jsx'));
const Profile = lazyWithRetry(() => import('./components/Profile.jsx'));
const Settings = lazyWithRetry(() => import('./components/Settings.jsx'));
const Admin = lazyWithRetry(() => import('./components/Admin.jsx'));
const AdminJobs = lazyWithRetry(() => import('./components/AdminJobs.jsx'));
const Debug = lazyWithRetry(() => import('./components/Debug.jsx'));

const AppRoutes = memo(({ user, onOnboardingSuccess, onLoginSuccess, handleLogout }) => {
  const [isDropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => {
      document.removeEventListener('mousedown', handleClickOutside);
    };
  }, []);

  if (user === undefined) {
    return <div>Loading...</div>;
  }

  const registerButtonStyle = {
    backgroundColor: 'var(--accent-orange)',
    color: 'white',
    padding: '10px 15px',
    textDecoration: 'none',
    borderRadius: '5px',
  };

  return (
    <>
      <nav>
        {user ? (
          <>
            <Link to="/dashboard">Dashboard</Link>
            {user.role && user.role.toLowerCase() === 'admin' && <Link to="/admin">Admin</Link>}
            <div style={{ position: 'relative', marginLeft: 'auto' }} ref={dropdownRef}>
              <button onClick={() => setDropdownOpen(!isDropdownOpen)} style={{ background: 'none', border: 'none', cursor: 'pointer' }} aria-label="User Menu">
                <UserProfileIcon />
              </button>
              {isDropdownOpen && (
                <div style={{ position: 'absolute', right: 0, backgroundColor: 'white', border: '1px solid var(--neutral-gray)', borderRadius: '5px', zIndex: 10 }}>
                  <Link to="/profile" style={{ display: 'block', padding: '10px', textDecoration: 'none', color: 'var(--neutral-gray)' }}>Profile</Link>
                  {user.role && user.role.toLowerCase() === 'admin' && (
                    <Link to="/admin" style={{ display: 'block', padding: '10px', textDecoration: 'none', color: 'var(--neutral-gray)' }}>Admin</Link>
                  )}
                  <Link to="/settings" style={{ display: 'block', padding: '10px', textDecoration: 'none', color: 'var(--neutral-gray)' }}>Settings</Link>
                  <Link to="/documents" style={{ display: 'block', padding: '10px', textDecoration: 'none', color: 'var(--neutral-gray)' }}>Documents</Link>
                  <button onClick={() => { handleLogout(); setDropdownOpen(false); }} style={{ display: 'block', width: '100%', padding: '10px', background: 'none', border: 'none', textAlign: 'left', cursor: 'pointer', color: 'var(--neutral-gray)' }}>Logout</button>
                </div>
              )}
            </div>
          </>
        ) : (
          <>
            <Link to="/login">Login</Link>
            <Link to="/register" style={registerButtonStyle}>Register</Link>
          </>
        )}
      </nav>
      <div className="container">
        <Suspense fallback={<div>Loading page...</div>}>
          <Routes>
            {user ? (
              <>
                <Route path="/dashboard" element={<Dashboard user={user} />} />
                <Route path="/admin" element={<Admin />} />
                <Route path="/admin/jobs" element={<AdminJobs />} />
                <Route path="/documents" element={<Documents />} />
                <Route path="/profile" element={<Profile user={user} />} />
                <Route path="/settings" element={<Settings user={user} />} />
                <Route path="/debug" element={<Debug />} />
                <Route path="/*" element={<Navigate to="/dashboard" />} />
              </>
            ) : (
              <>
                <Route path="/onboarding" element={<Onboarding onOnboardingSuccess={onOnboardingSuccess} onLoginSuccess={onLoginSuccess} />} />
                <Route path="/login" element={<Login onLoginSuccess={onLoginSuccess} />} />
                <Route path="/register" element={<Register />} />
                <Route path="/debug" element={<Debug />} />
                <Route path="/*" element={<Navigate to="/login" />} />
              </>
            )}
          </Routes>
        </Suspense>
      </div>
    </>
  );
});

function App() {
  const [user, setUser] = useState(undefined);
  const [loadingError, setLoadingError] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    if (!auth) {
      console.error("Auth is not initialized");
      return;
    }

    console.log("Setting up auth listener");
    // Timeout to detect if Firebase is hanging
    const timeoutId = setTimeout(() => {
      if (user === undefined) {
        console.warn("Firebase auth listener timed out");
        setLoadingError(new Error("Firebase authentication timed out. Check network connection or API key configuration."));
      }
    }, 10000); // 10 seconds timeout

    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      clearTimeout(timeoutId);
      console.log("Auth state changed:", firebaseUser ? "User found" : "No user");
      try {
        if (firebaseUser) {
          try {
            // Fetch user profile from backend API to avoid Firestore permission issues
            const response = await api.get('/me');
            setUser({ ...firebaseUser, ...response.data });
          } catch (apiError) {
            console.warn("Failed to fetch user profile from API, proceeding with auth user only:", apiError);

            // Auto-heal: Ensure Firestore document exists
            try {
              const userRef = doc(db, "users", firebaseUser.uid);
              const userSnap = await getDoc(userRef);

              if (!userSnap.exists()) {
                console.log("Creating missing user profile in Firestore (auto-heal)...");
                const newUserData = {
                  email: firebaseUser.email,
                  role: 'user',
                  created_at: new Date().toISOString(),
                  preferred_work_arrangement: [],
                  id: firebaseUser.uid
                };
                await setDoc(userRef, newUserData);
                setUser({ ...firebaseUser, ...newUserData });
              } else {
                 setUser({ ...firebaseUser, ...userSnap.data() });
              }
            } catch (firestoreError) {
              console.error("Failed to auto-heal Firestore profile:", firestoreError);
              setUser(firebaseUser);
            }
          }
        } else {
          // User is signed out
          setUser(null);
        }
      } catch (err) {
        console.error("Error fetching user data:", err);
        setLoadingError(err);
      }
    }, (error) => {
      clearTimeout(timeoutId);
      console.error("Auth listener error:", error);
      setLoadingError(error);
    });

    return () => {
      clearTimeout(timeoutId);
      unsubscribe();
    };
  }, []);

  if (initializationError) {
    return (
      <div style={{ padding: '20px', color: 'red' }}>
        <h1>Application Initialization Error</h1>
        <p>{initializationError.message}</p>
        <p>Please check the browser console for more details.</p>
      </div>
    );
  }

  const handleLogout = useCallback(async () => {
    try {
      await signOut(auth);
      setUser(null);
      navigate('/login');
    } catch (error) {
      console.error("Error signing out:", error);
    }
  }, [navigate]);

  // Placeholder for onOnboardingSuccess and onLoginSuccess
  // These functions might need to be updated based on how they are used in Login/Onboarding components
  const onOnboardingSuccess = useCallback(() => {
    // After onboarding, the user should already be logged in via Firebase
    // The onAuthStateChanged listener will pick up the user
    navigate('/dashboard');
  }, [navigate]);

  const onLoginSuccess = useCallback(() => {
    // After login, the user should already be logged in via Firebase
    // The onAuthStateChanged listener will pick up the user
    navigate('/dashboard');
  }, [navigate]);


  if (loadingError) {
    return (
      <div style={{ padding: '20px', color: 'red' }}>
        <h1>Loading Error</h1>
        <p>{loadingError.message}</p>
        <button onClick={() => window.location.reload()} style={{ marginTop: '10px' }}>Retry</button>
      </div>
    );
  }

  return (
    <AppRoutes
      user={user}
      onOnboardingSuccess={onOnboardingSuccess}
      onLoginSuccess={onLoginSuccess}
      handleLogout={handleLogout}
    />
  );
}

export default App;
