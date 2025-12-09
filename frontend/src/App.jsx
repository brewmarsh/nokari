import React, { useState, useEffect, useCallback, memo, useRef, Suspense, lazy } from 'react';
import { Routes, Route, Navigate, Link, useNavigate } from 'react-router-dom';
import './App.css';
import { auth, db } from './firebaseConfig';
import { onAuthStateChanged, signOut } from 'firebase/auth';
import { doc, getDoc } from 'firebase/firestore';
import UserProfileIcon from './components/UserProfileIcon.jsx';

// Lazy load components
const Login = lazy(() => import('./components/Login.jsx'));
const Register = lazy(() => import('./components/Register.jsx'));
const Dashboard = lazy(() => import('./components/Dashboard.jsx'));
const Onboarding = lazy(() => import('./components/Onboarding.jsx'));
const Documents = lazy(() => import('./components/Documents.jsx'));
const Profile = lazy(() => import('./components/Profile.jsx'));
const Settings = lazy(() => import('./components/Settings.jsx'));
const Admin = lazy(() => import('./components/Admin.jsx'));
const AdminJobs = lazy(() => import('./components/AdminJobs.jsx'));

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
            {user.role === 'admin' && <Link to="/admin">Admin</Link>}
            <div style={{ position: 'relative', marginLeft: 'auto' }} ref={dropdownRef}>
              <button onClick={() => setDropdownOpen(!isDropdownOpen)} style={{ background: 'none', border: 'none', cursor: 'pointer' }} aria-label="User Menu">
                <UserProfileIcon />
              </button>
              {isDropdownOpen && (
                <div style={{ position: 'absolute', right: 0, backgroundColor: 'white', border: '1px solid var(--neutral-gray)', borderRadius: '5px', zIndex: 10 }}>
                  <Link to="/profile" style={{ display: 'block', padding: '10px', textDecoration: 'none', color: 'var(--neutral-gray)' }}>Profile</Link>
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
                <Route path="/profile" element={<Profile />} />
                <Route path="/settings" element={<Settings />} />
                <Route path="/*" element={<Navigate to="/dashboard" />} />
              </>
            ) : (
              <>
                <Route path="/onboarding" element={<Onboarding onOnboardingSuccess={onOnboardingSuccess} onLoginSuccess={onLoginSuccess} />} />
                <Route path="/login" element={<Login onLoginSuccess={onLoginSuccess} />} />
                <Route path="/register" element={<Register />} />
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
  const navigate = useNavigate();

  useEffect(() => {
    const unsubscribe = onAuthStateChanged(auth, async (firebaseUser) => {
      if (firebaseUser) {
        // User is signed in, see if we have additional data in Firestore
        const userDocRef = doc(db, "users", firebaseUser.uid);
        const userDoc = await getDoc(userDocRef);
        if (userDoc.exists()) {
          setUser({ ...firebaseUser, ...userDoc.data() });
        } else {
          setUser(firebaseUser);
        }
      } else {
        // User is signed out
        setUser(null);
      }
    });

    return () => unsubscribe();
  }, []);

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
