import { useState } from 'react'
import { timezoneLabel } from '../time'

// US zones cover the states this runs in; the API accepts any IANA name
const TIMEZONES = [
    ['America/New_York', 'Eastern (New York)'],
    ['America/Chicago', 'Central (Chicago)'],
    ['America/Denver', 'Mountain (Denver)'],
    ['America/Phoenix', 'Arizona (no daylight saving)'],
    ['America/Los_Angeles', 'Pacific (Los Angeles)'],
    ['America/Anchorage', 'Alaska (Anchorage)'],
    ['Pacific/Honolulu', 'Hawaii (Honolulu)']
]

function AdminSettings({ timezone, adminFetch, onChange }) {
    const [selected, setSelected] = useState(timezone)
    const [error, setError] = useState('')

    // Keep a zone set outside this list selectable instead of silently showing the first option
    const options = TIMEZONES.some(([value]) => value === timezone)
        ? TIMEZONES
        : [[timezone, timezone], ...TIMEZONES]

    function handleSave(e) {
        e.preventDefault()
        adminFetch('/api/admin/settings/timezone', {
            method: 'PUT',
            body: JSON.stringify({ timezone: selected })
        }).then(response => {
            if (!response) return
            if (response.ok) {
                setError('')
                onChange()
            } else {
                setError('Could not save the timezone')
            }
        }).catch(error => console.error(error))
    }

    return (
        <section>
            <h3>Settings</h3>
            <form onSubmit={handleSave}>
                <label>
                    Timezone{' '}
                    <select value={selected} onChange={e => setSelected(e.target.value)}>
                        {options.map(([value, name]) => (
                            <option key={value} value={value}>{name}</option>
                        ))}
                    </select>
                </label>
                <button type="submit" disabled={selected === timezone}>Save</button>
            </form>
            <p>Due times are entered and shown in {timezoneLabel(timezone)}.</p>
            {error && <p style={{ color: 'red' }}>{error}</p>}
        </section>
    )
}

export default AdminSettings
