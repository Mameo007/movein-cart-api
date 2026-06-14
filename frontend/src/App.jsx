import CartList from './components/CartList'
import CheckoutForm from './components/CheckoutForm'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {

  return (
    <div>
      
      <BrowserRouter>
        <h1>Cart Tracker</h1>
        <Routes>
          <Route path="/" element={<CartList />} />
          <Route path="/checkout/:cartId" element={<CheckoutForm />} />
        </Routes>
      </BrowserRouter>
    </div>
  )

}

export default App
