import { useState } from 'react'

const STATUS_LABELS = {
    AVAILABLE: 'Available',
    IN_USE: 'In Use',
    MAINTENANCE: 'Out of Service'
}

function AdminCarts({ carts, adminFetch, onChange }) {
    const [newCartNumber, setNewCartNumber] = useState('')
    const [error, setError] = useState('')

    // The API sends back { detail: "..." } on a 400 -- show that to the admin
    function handleResponse(response) {
        if (!response) return
        if (response.ok) {
            setError('')
            onChange()
            return
        }
        return response.json().then(data => setError(data.detail ?? 'Something went wrong'))
    }

    function handleAddCart(e) {
        e.preventDefault()
        adminFetch('/api/admin/carts', {
            method: 'POST',
            body: JSON.stringify({ cart_number: newCartNumber.trim() })
        }).then(response => {
            if (response?.ok) setNewCartNumber('')
            return handleResponse(response)
        }).catch(error => console.error(error))
    }

    function handleSetStatus(cart, status) {
        adminFetch(`/api/admin/carts/${cart.id}`, {
            method: 'PATCH',
            body: JSON.stringify({ status })
        }).then(handleResponse).catch(error => console.error(error))
    }

    function handleDelete(cart) {
        if (!window.confirm(`Delete cart ${cart.cart_number}? Its session history will be deleted too.`)) return

        adminFetch(`/api/admin/carts/${cart.id}`, { method: 'DELETE' })
            .then(handleResponse)
            .catch(error => console.error(error))
    }

    return (
        <section>
            <h3>Carts</h3>
            <form onSubmit={handleAddCart}>
                <input
                    placeholder="New cart number"
                    value={newCartNumber}
                    onChange={e => setNewCartNumber(e.target.value)}
                    required
                />
                <button type="submit">Add Cart</button>
            </form>
            {error && <p style={{ color: 'red' }}>{error}</p>}

            {carts.map(cart => (
                <div key={cart.id}>
                    Cart {cart.cart_number} - {STATUS_LABELS[cart.status] ?? cart.status}
                    {cart.status === 'AVAILABLE' && (
                        <button onClick={() => handleSetStatus(cart, 'MAINTENANCE')}>Take Out of Service</button>
                    )}
                    {cart.status === 'MAINTENANCE' && (
                        <button onClick={() => handleSetStatus(cart, 'AVAILABLE')}>Return to Service</button>
                    )}
                    {/* A checked-out cart has to be returned before it can be changed or deleted */}
                    <button onClick={() => handleDelete(cart)} disabled={cart.status === 'IN_USE'}>Delete</button>
                </div>
            ))}
        </section>
    )
}

export default AdminCarts
