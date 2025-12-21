import { useState } from 'react'
import ChatInterface from './ChatInterface'
import Dashboard from './Dashboard'
import { LayoutDashboard } from 'lucide-react'
import './App.css'
import './Dashboard.css'

function App() {
  const [sessionId] = useState(() => Math.random().toString(36).substring(7))
  const [showDashboard, setShowDashboard] = useState(false)

  return (
    <div className="app-container">
      <header>
        <div className="header-content">
          <h1>ElectroShop AI Agent</h1>
          <p>Order electronics via Chat (Voice Mode Coming Soon)</p>
        </div>
        <button
          className="dashboard-btn"
          onClick={() => setShowDashboard(true)}
          title="Business Owner Dashboard"
        >
          <LayoutDashboard size={24} />
        </button>
      </header>

      <main>
        {/* Chat Interface by default for now */}
        <ChatInterface sessionId={sessionId} />
      </main>

      {showDashboard && <Dashboard onClose={() => setShowDashboard(false)} />}

      <footer>
        <p>Session ID: {sessionId}</p>
      </footer>
    </div>
  )
}

export default App
