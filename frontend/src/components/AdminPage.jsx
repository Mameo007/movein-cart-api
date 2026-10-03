import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { authHeaders, clearToken } from '../auth'
import AdminCarts from './AdminCarts'
import AdminSessions from './AdminSessions'
import AdminSettings from './AdminSettings'
import { isOverdue } from '../sessions'

// How often the overdue highlighting re-checks the clock
const CLOCK_TICK_MS = 30 * 1000

function AdminPage() {
    const [carts, setCarts] = useState([])
    const [sessions, setSessions] = useState([])
    // The site's IANA timezone; null until loaded so nothing renders in the browser's zone first
    const [timezone, setTimezone] = useState(null)
    const [now, setNow] = useState(new Date())
    const navigate = useNavigate()

    useEffect(() => {
        refresh()
        // Re-render every so often so a cart flips to overdue without a reload
        const timer = setInterval(() => setNow(new Date()), CLOCK_TICK_MS)
        return () => clearInterval(timer)
    }, [])

    function handleLogout() {
        clearToken()
        navigate('/admin/login')
    }

    // Every admin request goes through here so a 401 (expired or missing token)
    // always sends them back to login. Resolves to null in that case.
    function adminFetch(path, options = {}) {
        return fetch(`${import.meta.env.VITE_API_URL}${path}`, {
            ...options,
            headers: {
                'Content-Type': 'application/json',
                ...authHeaders(),
                ...options.headers
            }
        }).then(response => {
            if (response.status === 401) {
                handleLogout()
                return null
            }
            return response
        })
    }

    // Carts, active sessions and settings feed every section and the counts, so reload together
    function refresh() {
        adminFetch('/api/carts')
            .then(response => response && response.json())
            .then(data => data && setCarts(data))
            .catch(error => console.error(error))

        adminFetch('/api/admin/sessions')
            .then(response => response && response.json())
            .then(data => data && setSessions(data))
            .catch(error => console.error(error))

        adminFetch('/api/settings')
            .then(response => response && response.json())
            .then(data => data && setTimezone(data.timezone))
            .catch(error => console.error(error))
    }

    const counts = {
        available: carts.filter(c => c.status === 'AVAILABLE').length,
        inUse: carts.filter(c => c.status === 'IN_USE').length,
        overdue: sessions.filter(s => isOverdue(s, now)).length,
        maintenance: carts.filter(c => c.status === 'MAINTENANCE').length
    }

    return (
        <div>
            <h2>Admin</h2>
            <button onClick={handleLogout}>Log Out</button>

            <p>
                Available: {counts.available} | In Use: {counts.inUse} |{' '}
                <span style={counts.overdue > 0 ? { color: 'red', fontWeight: 'bold' } : undefined}>
                    Overdue: {counts.overdue}
                </span>{' '}
                | Out of Service: {counts.maintenance}
            </p>

            {timezone && (
                <AdminSessions sessions={sessions} now={now} timezone={timezone} adminFetch={adminFetch} onChange={refresh} />
            )}
            <AdminCarts carts={carts} adminFetch={adminFetch} onChange={refresh} />
            {/* Keyed so the dropdown resets to the saved zone after a save */}
            {timezone && (
                <AdminSettings key={timezone} timezone={timezone} adminFetch={adminFetch} onChange={refresh} />
            )}
        </div>
    )
}

export default AdminPage
