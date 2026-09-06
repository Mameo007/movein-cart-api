import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { authHeaders, clearToken } from '../auth'

// <input type="datetime-local"> wants "YYYY-MM-DDTHH:MM", the API sends full ISO
function toInputValue(isoString) {
    return isoString.slice(0, 16)
}

function AdminPage() {
    const [sessions, setSessions] = useState([])
    const [dueEdits, setDueEdits] = useState({})
    const navigate = useNavigate()

    useEffect(() => {
        fetchSessions()
    }, [])

    // An expired or missing token means the API says 401 -- send them back to login
    function handleUnauthorized() {
        clearToken()
        navigate('/admin/login')
    }

    function handleLogout() {
        clearToken()
        navigate('/admin/login')
    }

    function fetchSessions() {
        fetch(`${import.meta.env.VITE_API_URL}/api/admin/sessions`, {
            headers: authHeaders()
        }).then(response => {
            if (response.status === 401) {
                handleUnauthorized()
                return
            }
            return response.json().then(data => {
                setSessions(data)
                // Seed each row's input with the due time already on the session
                setDueEdits(Object.fromEntries(data.map(s => [s.id, toInputValue(s.due_at)])))
            })
        }).catch(error => console.error(error))
    }

    function handleUpdateDue(sessionId) {
        fetch(`${import.meta.env.VITE_API_URL}/api/admin/sessions/${sessionId}`, {
            method: 'PATCH',
            headers: {
                'Content-Type': 'application/json',
                ...authHeaders()
            },
            body: JSON.stringify({ due_at: dueEdits[sessionId] })
        }).then(response => {
            if (response.status === 401) {
                handleUnauthorized()
            } else if (response.ok) {
                fetchSessions()
            } else {
                console.error('Due time update failed')
            }
        }).catch(error => console.error(error))
    }

    return (
        <div>
            <h2>Active Sessions</h2>
            <button onClick={handleLogout}>Log Out</button>

            {sessions.length === 0 && <p>No carts are currently checked out.</p>}

            {sessions.map(session => (
                <div key={session.id}>
                    Cart {session.cart_number} - {session.first_name} {session.last_name} - Room {session.room_number} - {session.phone_number}
                    <input
                        type="datetime-local"
                        value={dueEdits[session.id] ?? ''}
                        onChange={e => setDueEdits({ ...dueEdits, [session.id]: e.target.value })}
                    />
                    <button onClick={() => handleUpdateDue(session.id)}>Update Due Time</button>
                </div>
            ))}
        </div>
    )
}

export default AdminPage
