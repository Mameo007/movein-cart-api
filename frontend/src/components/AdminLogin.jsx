import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { setToken } from '../auth'

function AdminLogin() {

    const navigate = useNavigate()
    const [password, setPassword] = useState('')
    const [error, setError] = useState('')

    const handleSubmit = (e) => {
        e.preventDefault()
        setError('')

        fetch(`${import.meta.env.VITE_API_URL}/api/admin/login`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ password })
        }).then(response => {
            if (response.ok) {
                return response.json().then(data => {
                    setToken(data.access_token)
                    navigate('/admin')
                })
            }
            setError('Incorrect password')
        }).catch(error => console.error(error))
    }

    return (
        <form onSubmit={handleSubmit}>
            <h2>Admin Login</h2>
            <input type="password" placeholder="Admin Password" value={password} onChange={e => setPassword(e.target.value)} required />
            <button type="submit">Log In</button>
            {error && <p>{error}</p>}
        </form>
    )
}

export default AdminLogin
