import { useState, useEffect } from 'react'
import axios from 'axios'
import { GoogleLogin, googleLogout } from '@react-oauth/google'
import { jwtDecode } from 'jwt-decode'
import ChatInterface from './ChatInterface'
import Dashboard from './Dashboard'
import AdminDashboard from './AdminDashboard'
import { LayoutDashboard, LogOut, Store, Settings } from 'lucide-react'
import './App.css'
import './Dashboard.css'

function App() {
  const [sessionId] = useState(() => Math.random().toString(36).substring(7))
  const [showDashboard, setShowDashboard] = useState(false)
  const [showAdmin, setShowAdmin] = useState(false)
  const [user, setUser] = useState(null)

  // Multi-tenancy State
  const [businesses, setBusinesses] = useState([])
  const [currentBusinessId, setCurrentBusinessId] = useState('electronics_default')

  // Check for existing session
  useEffect(() => {
    const storedUser = localStorage.getItem('user_token');
    if (storedUser) {
      try {
        const decoded = jwtDecode(storedUser);
        if (decoded.exp * 1000 > Date.now()) {
          setUser(decoded);
        } else {
          localStorage.removeItem('user_token');
        }
      } catch (e) {
        localStorage.removeItem('user_token');
      }
    }
  }, []);

  // Load Businesses
  const loadBusinesses = () => {
    const API_URL = import.meta.env.PROD ? '' : 'http://localhost:8000';
    axios.get(`${API_URL}/admin/businesses`)
      .then(res => {
        setBusinesses(res.data)
        // Restore last selected business if available, but only if we don't have a valid one selected
        // Actually, logic: if saved exists, use it.
        const savedBiz = localStorage.getItem('selected_business_id')
        if (savedBiz && res.data.find(b => b.id === savedBiz)) {
          // Maybe don't auto-set if we already have one?
          // The previous logic was fine for initial load.
          // For explicit reloads, we just want to update the list, not change selection unless invalid.
          if (!currentBusinessId || currentBusinessId === 'electronics_default') {
            setCurrentBusinessId(savedBiz)
          }
        }
      })
      .catch(err => console.error("Failed to load businesses", err))
  }

  useEffect(() => {
    loadBusinesses()
  }, [])

  // Switch business handler (available to AdminDashboard)
  const switchBusiness = (businessId) => {
    setCurrentBusinessId(businessId)
    localStorage.setItem('selected_business_id', businessId)
  }

  const handleBusinessChange = (e) => {
    switchBusiness(e.target.value)
  }

  const handleLoginSuccess = (credentialResponse) => {
    const decoded = jwtDecode(credentialResponse.credential);
    console.log("Logged in user:", decoded);
    setUser(decoded);
    localStorage.setItem('user_token', credentialResponse.credential);
  };

  const handleLogout = () => {
    googleLogout();
    setUser(null);
    localStorage.removeItem('user_token');
    setShowDashboard(false);
    setShowAdmin(false);
  };

  if (!user) {
    return (
      <div className="login-container">
        <div className="login-card">
          <h1>Platform Login</h1>
          <p>Welcome back! Please sign in to continue.</p>
          <div className="google-login-wrapper">
            <GoogleLogin
              onSuccess={handleLoginSuccess}
              onError={() => {
                console.log('Login Failed');
              }}
              useOneTap
            />
          </div>
        </div>
      </div>
    )
  }

  // Find current business object for display
  const currentBiz = businesses.find(b => b.id === currentBusinessId) || {}

  const ADMIN_EMAILS = ["rakeshkakarla85@gmail.com"];
  // Robust check with lowercasing and optional chaining
  const userEmail = user?.email?.toLowerCase();
  const isAdmin = userEmail && ADMIN_EMAILS.includes(userEmail);

  return (
    <div className="app-container">
      <header>
        <div className="header-content">
          <h1>{currentBiz.name || 'AI Platform'}</h1>
          <div className="business-selector">
            <Store size={16} />
            <select value={currentBusinessId} onChange={handleBusinessChange}>
              {businesses.map(biz => (
                <option key={biz.id} value={biz.id}>
                  {biz.name} ({biz.type})
                </option>
              ))}
            </select>
          </div>
        </div>
        <div className="header-actions">
          {user && <span className="user-greeting">Hi, {user.given_name}</span>}

          {isAdmin && (
            <button
              className="admin-btn"
              onClick={() => setShowAdmin(true)}
              title="Platform Admin"
            >
              <Settings size={20} />
            </button>
          )}

          <button
            className="dashboard-btn"
            onClick={() => setShowDashboard(true)}
            title="Business Owner Dashboard"
          >
            <LayoutDashboard size={20} />
          </button>

          <button
            className="logout-btn"
            onClick={handleLogout}
            title="Sign Out"
          >
            <LogOut size={20} />
          </button>
        </div>
      </header>

      <main>
        <ChatInterface
          sessionId={sessionId}
          businessId={currentBusinessId}
          businessName={currentBiz.name || 'Electronics Shop'}
        />
      </main>

      {showDashboard && (
        <Dashboard
          onClose={() => setShowDashboard(false)}
          businessId={currentBusinessId}
        />
      )}

      {showAdmin && (
        <AdminDashboard
          onClose={() => setShowAdmin(false)}
          onSwitchBusiness={switchBusiness}
          businesses={businesses}
          onBusinessAdded={loadBusinesses}
        />
      )}

      <footer>
        <p>Session ID: {sessionId} | Business: {currentBusinessId}</p>
      </footer>
    </div>
  )
}

export default App
