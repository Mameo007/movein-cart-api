import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'

function CartList() {
    const [items, setItems] = useState([])
    const navigate = useNavigate()

    useEffect(() => {
        fetchCarts()
    }, [])

    function handleCheckout(cartId) {
        navigate('/checkout/' + cartId)
    }

    function handleReturn(cartId) {
        fetch(`${import.meta.env.VITE_API_URL}/api/carts/${cartId}/return`, {
            method: 'POST'
        }).then(response => {
            if (response.ok) {
                fetchCarts()
            } else {
                console.error('Return failed')
            }
        }).catch(error => console.error(error))
    }

    function fetchCarts() {
        fetch(`${import.meta.env.VITE_API_URL}/api/carts`)
            .then(response => response.json())
            .then(data => setItems(data))
            .catch(error => console.error(error))
    }

    return (
        <div>
            {items.map(cart => (
                <div key={cart.id}>
                    {cart.id} - {cart.status}
                    {cart.status === 'AVAILABLE' && <button onClick={() => handleCheckout(cart.id)}>Checkout</button>}
                    {cart.status === 'IN_USE' && <button onClick={() => handleReturn(cart.id)}>Return</button>}
                    {/* MAINTENANCE carts get no button -- the admin puts them back in service */}
                </div>
            ))}
        </div>
        
    )
}



export default CartList