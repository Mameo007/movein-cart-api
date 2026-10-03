import CartList from './components/CartList'
import CheckoutForm from './components/CheckoutForm'
import AdminLogin from './components/AdminLogin'
import AdminPage from './components/AdminPage'
import RequireAdmin from './components/RequireAdmin'
import { BrowserRouter, Routes, Route } from 'react-router-dom'

function App() {

  return (
    <div>
      
      <BrowserRouter>
        <h1>Cart Tracker</h1>
        <Routes>
          <Route path="/" element={<CartList />} />
          <Route path="/checkout/:cartId" element={<CheckoutForm />} />
          <Route path="/admin/login" element={<AdminLogin />} />
          <Route path="/admin" element={<RequireAdmin><AdminPage /></RequireAdmin>} />
        </Routes>
      </BrowserRouter>
    </div>
  )

}

export default App
