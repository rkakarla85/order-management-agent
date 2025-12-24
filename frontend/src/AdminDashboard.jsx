import { useState, useEffect } from 'react';
import { X, Plus, Store, Play } from 'lucide-react';
import axios from 'axios';
import './Dashboard.css'; // Reuse existing styles for consistency

const API_URL = import.meta.env.PROD ? '' : 'http://localhost:8000';

export default function AdminDashboard({ onClose, onSwitchBusiness, businesses, onBusinessAdded }) {
    // const [businesses, setBusinesses] = useState([]); // Removed local state
    const [isCreating, setIsCreating] = useState(false);
    const [newBiz, setNewBiz] = useState({ name: '', type: 'retail', sheet_id: '' });

    // Removed useEffect and fetchBusinesses

    // ... create handler needs update ...

    const handleCreate = async (e) => {
        e.preventDefault();
        // Basic ID generation logic based on name
        const id = newBiz.name.toLowerCase().replace(/\s+/g, '_') + '_' + Math.floor(Math.random() * 1000);

        try {
            await axios.post(`${API_URL}/admin/businesses`, {
                ...newBiz,
                id: id,
                config: {}
            });
            setIsCreating(false);
            setNewBiz({ name: '', type: 'retail', sheet_id: '' });
            if (onBusinessAdded) onBusinessAdded(); // Refresh parent state
        } catch (error) {
            alert("Failed to create business");
            console.error(error);
        }
    };

    const handleTest = (bizId) => {
        if (onSwitchBusiness) {
            onSwitchBusiness(bizId);
            onClose(); // Close admin panel so they can test immediately
        }
    };

    return (
        <div className="dashboard-overlay">
            <div className="dashboard-content">
                <div className="dashboard-header">
                    <div className="header-left">
                        <Store size={24} />
                        <h2>Platform Admin</h2>
                    </div>
                    <button className="close-btn" onClick={onClose}><X size={24} /></button>
                </div>

                <div className="dashboard-body">
                    <div className="stats-grid">
                        <div className="stat-card">
                            <h3>Total Businesses</h3>
                            <p className="stat-value">{businesses.length}</p>
                        </div>
                    </div>

                    <div className="orders-section">
                        <div className="section-header">
                            <h3>Registered Businesses</h3>
                            <button className="refresh-btn" onClick={() => setIsCreating(true)}>
                                <Plus size={16} /> Add New
                            </button>
                        </div>

                        {isCreating && (
                            <div className="login-card" style={{ margin: '20px auto', maxWidth: '100%', padding: '20px' }}>
                                <form onSubmit={handleCreate} style={{ display: 'flex', flexDirection: 'column', gap: '10px', textAlign: 'left' }}>
                                    <h3>New Business</h3>
                                    <input
                                        placeholder="Business Name"
                                        value={newBiz.name}
                                        onChange={e => setNewBiz({ ...newBiz, name: e.target.value })}
                                        required
                                        className="p-2 rounded bg-white/10 border border-white/20 text-white"
                                    />
                                    <select
                                        value={newBiz.type}
                                        onChange={e => setNewBiz({ ...newBiz, type: e.target.value })}
                                        className="p-2 rounded bg-white/10 border border-white/20 text-white"
                                    >
                                        <option value="retail">Retail (Electronics)</option>
                                        <option value="restaurant">Restaurant</option>
                                    </select>
                                    <input
                                        placeholder="Google Sheet ID"
                                        value={newBiz.sheet_id}
                                        onChange={e => setNewBiz({ ...newBiz, sheet_id: e.target.value })}
                                        required
                                        className="p-2 rounded bg-white/10 border border-white/20 text-white"
                                    />
                                    <div style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
                                        <button type="submit" className="dashboard-btn" style={{ flex: 1 }}>Create</button>
                                        <button type="button" className="logout-btn" onClick={() => setIsCreating(false)}>Cancel</button>
                                    </div>
                                </form>
                            </div>
                        )}

                        <div className="orders-table-container">
                            <table className="orders-table">
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Name</th>
                                        <th>Type</th>
                                        <th>Sheet ID</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {businesses.map((biz) => (
                                        <tr key={biz.id}>
                                            <td>{biz.id}</td>
                                            <td>{biz.name}</td>
                                            <td>
                                                <span className={`status-badge ${biz.type === 'restaurant' ? 'pending' : 'confirmed'}`}>
                                                    {biz.type.toUpperCase()}
                                                </span>
                                            </td>
                                            <td style={{ fontSize: '0.8em', maxWidth: '150px', overflow: 'hidden', textOverflow: 'ellipsis' }}>{biz.sheet_id}</td>
                                            <td>
                                                <button
                                                    onClick={() => handleTest(biz.id)}
                                                    className="test-btn"
                                                    title="Test this business"
                                                    style={{
                                                        background: 'rgba(46, 213, 115, 0.2)',
                                                        color: '#2ed573',
                                                        border: '1px solid rgba(46, 213, 115, 0.4)',
                                                        padding: '4px 8px',
                                                        borderRadius: '6px',
                                                        cursor: 'pointer',
                                                        display: 'flex',
                                                        alignItems: 'center',
                                                        gap: '4px'
                                                    }}
                                                >
                                                    <Play size={14} /> Test
                                                </button>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
