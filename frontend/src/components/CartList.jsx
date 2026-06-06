import { useState, useEffect } from 'react'

function CartList() {
    const [items, setItems] = useState([])

    useEffect(() => {
        fetch('http://localhost:8000/api/carts')
            .then(response => response.json())
            .then(data => setItems(data))
            .catch(error => console.error('Error fetching cart items:', error))
    }, [])

    return (
        <div>
            {items.map(cart => (
                <div key={cart.id}>
                    {cart.id} - {cart.status}
                </div>
            ))}
        </div>
        
    )
} 

export default CartList