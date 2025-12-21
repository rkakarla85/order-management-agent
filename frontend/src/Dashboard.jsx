import { useState, useEffect } from 'react'
import axios from 'axios'
import { Package, Clock, X } from 'lucide-react'

function Dashboard({ onClose }) {
    const [orders, setOrders] = useState([])
    const [isLoading, setIsLoading] = useState(true)

    useEffect(() => {
        fetchOrders()
    }, [])

    const fetchOrders = async () => {
        try {
            const response = await axios.get('http://localhost:8000/orders')
            setOrders(response.data)
        } catch (error) {
            console.error("Error fetching orders:", error)
        } finally {
            setIsLoading(false)
        }
    }

    return (
        <div className="dashboard-overlay">
            <div className="dashboard-container">
                <div className="dashboard-header">
                    <h2><Package className="icon" /> Order Dashboard</h2>
                    <button onClick={onClose} className="close-btn"><X /></button>
                </div>

                <div className="dashboard-content">
                    {isLoading ? (
                        <p>Loading orders...</p>
                    ) : orders.length === 0 ? (
                        <p className="no-orders">No orders found.</p>
                    ) : (
                        <div className="orders-table-wrapper">
                            <table className="orders-table">
                                <thead>
                                    <tr>
                                        <th>Timestamp</th>
                                        <th>Items</th>
                                        <th>Status</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {orders.map((order, index) => (
                                        <tr key={index}>
                                            <td><div className="td-content"><Clock size={14} /> {order.Timestamp || order.timestamp}</div></td>
                                            <td>{order['Order Items'] || order.items || 'N/A'}</td>
                                            <td><span className="status-badge">{order.Status || order.status || 'Confirmed'}</span></td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </div>
            </div>
        </div>
    )
}

export default Dashboard
