import { useParams, useNavigate } from 'react-router-dom'
import {useState, useEffect} from 'react'
import { timezoneLabel } from '../time'

function CheckoutForm() {

    const { cartId } = useParams()
    const navigate = useNavigate()
    const [formData, setFormData] = useState({
        first_name: '',
        last_name: '',
        phone_number: '',
        room_number: '',
        due_at: ''
    })
    const [timezone, setTimezone] = useState(null)

    // The API reads the typed due time in the site's timezone, so say which one that is
    useEffect(() => {
        fetch(`${import.meta.env.VITE_API_URL}/api/settings`)
            .then(response => response.json())
            .then(data => setTimezone(data.timezone))
            .catch(error => console.error(error))
    }, [])

    const handleSubmit = (e) => {
        e.preventDefault()
        fetch(`${import.meta.env.VITE_API_URL}/api/carts/${cartId}/checkout`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(formData)
        }).then(response => {
            if (response.ok) {
                navigate('/')
            } else {
                console.error('Checkout failed')
            }
        }).catch(error => console.error(error))
    }

    return (
        <form onSubmit={handleSubmit}>
            <input type="text" placeholder="First Name" value={formData.first_name} onChange={e => setFormData({...formData, first_name: e.target.value})} required />
            <input type="text" placeholder="Last Name" value={formData.last_name} onChange={e => setFormData({...formData, last_name: e.target.value})} required />
            <input type="text" placeholder="Phone Number" value={formData.phone_number} onChange={e => setFormData({...formData, phone_number: e.target.value})} required />
            <input type="text" placeholder="Room Number" value={formData.room_number} onChange={e => setFormData({...formData, room_number: e.target.value})} required />
            {timezone && <span>Due time ({timezoneLabel(timezone)}):</span>}
            <input type="datetime-local" placeholder="Due At" value={formData.due_at} onChange={e => setFormData({...formData, due_at: e.target.value})} required />
            <button type="submit">Checkout</button>
        </form>
    )
}

export default CheckoutForm