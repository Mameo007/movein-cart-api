import { Navigate } from 'react-router-dom'
import { getToken } from '../auth'

// Wraps admin-only routes. This just hides the page from someone without a
// token -- the API still checks the token on every request, which is the part
// that actually keeps non-admins out.
function RequireAdmin({ children }) {
    if (!getToken()) {
        return <Navigate to="/admin/login" replace />
    }

    return children
}

export default RequireAdmin
