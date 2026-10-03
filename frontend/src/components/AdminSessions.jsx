import { useState } from 'react'
import { isOverdue } from '../sessions'
import { formatTime, toInputValue } from '../time'

const QUICK_EXTENDS = [15, 30, 60]

function minutesOverdue(session, now) {
    return Math.floor((now - new Date(session.due_at)) / 60000)
}

function matchesSearch(session, search) {
    const needle = search.trim().toLowerCase()
    if (!needle) return true
    return [session.first_name, session.last_name, session.room_number, session.cart_number]
        .some(field => field.toLowerCase().includes(needle))
}

function AdminSessions({ sessions, now, timezone, adminFetch, onChange }) {
    const [view, setView] = useState('active')
    const [history, setHistory] = useState([])
    // Only what the admin has typed but not saved; untouched rows show the session's due time
    const [dueEdits, setDueEdits] = useState({})
    const [search, setSearch] = useState('')

    function showHistory() {
        setView('history')
        adminFetch('/api/admin/sessions?status=returned')
            .then(response => response && response.json())
            .then(data => data && setHistory(data))
            .catch(error => console.error(error))
    }

    function updateDue(sessionId, dueAt) {
        adminFetch(`/api/admin/sessions/${sessionId}`, {
            method: 'PATCH',
            body: JSON.stringify({ due_at: dueAt })
        }).then(response => {
            if (response?.ok) {
                // Drop the draft so the input falls back to the saved due time
                setDueEdits(edits => {
                    const rest = { ...edits }
                    delete rest[sessionId]
                    return rest
                })
                onChange()
            } else if (response) {
                console.error('Due time update failed')
            }
        }).catch(error => console.error(error))
    }

    // Extend from whichever is later, the due time or now -- adding 15 minutes
    // to a cart that's an hour overdue would still leave it overdue.
    // Sent as an exact UTC instant, so the API doesn't reinterpret it in the site zone.
    function handleQuickExtend(session, minutes) {
        const base = Math.max(new Date(session.due_at), now)
        updateDue(session.id, new Date(base + minutes * 60000).toISOString())
    }

    function handleForceReturn(session) {
        if (!window.confirm(`Mark cart ${session.cart_number} as returned?`)) return

        adminFetch(`/api/admin/sessions/${session.id}/return`, { method: 'POST' })
            .then(response => {
                if (response?.ok) onChange()
                else if (response) console.error('Force return failed')
            }).catch(error => console.error(error))
    }

    const activeRows = sessions.filter(s => matchesSearch(s, search))
    const historyRows = history.filter(s => matchesSearch(s, search))

    return (
        <section>
            <h3>Sessions</h3>
            <button onClick={() => setView('active')} disabled={view === 'active'}>Active</button>
            <button onClick={showHistory} disabled={view === 'history'}>History</button>
            <input
                type="search"
                placeholder="Search name, room, or cart"
                value={search}
                onChange={e => setSearch(e.target.value)}
            />

            {view === 'active' && (
                <>
                    {activeRows.length === 0 && <p>No carts are currently checked out.</p>}

                    {activeRows.map(session => {
                        const overdue = isOverdue(session, now)
                        return (
                            <div key={session.id} style={overdue ? { color: 'red' } : undefined}>
                                Cart {session.cart_number} - {session.first_name} {session.last_name} - Room {session.room_number} -{' '}
                                <a href={`tel:${session.phone_number}`}>{session.phone_number}</a>{' '}
                                (<a href={`sms:${session.phone_number}`}>text</a>)
                                {' '}- Due {formatTime(session.due_at, timezone)}
                                {overdue && <strong> ({minutesOverdue(session, now)} min overdue)</strong>}

                                <input
                                    type="datetime-local"
                                    value={dueEdits[session.id] ?? toInputValue(new Date(session.due_at), timezone)}
                                    onChange={e => setDueEdits({ ...dueEdits, [session.id]: e.target.value })}
                                />
                                <button
                                    onClick={() => updateDue(session.id, dueEdits[session.id])}
                                    disabled={!(session.id in dueEdits)}
                                >
                                    Update Due Time
                                </button>
                                {QUICK_EXTENDS.map(minutes => (
                                    <button key={minutes} onClick={() => handleQuickExtend(session, minutes)}>
                                        +{minutes >= 60 ? `${minutes / 60} hr` : `${minutes} min`}
                                    </button>
                                ))}
                                <button onClick={() => handleForceReturn(session)}>Mark Returned</button>
                            </div>
                        )
                    })}
                </>
            )}

            {view === 'history' && (
                <>
                    {historyRows.length === 0 && <p>No returned sessions yet.</p>}

                    {historyRows.map(session => (
                        <div key={session.id}>
                            Cart {session.cart_number} - {session.first_name} {session.last_name} - Room {session.room_number} -{' '}
                            {session.phone_number} - Out {formatTime(session.checked_out_at, timezone)} - Returned {formatTime(session.returned_at, timezone)}
                        </div>
                    ))}
                </>
            )}
        </section>
    )
}

export default AdminSessions
