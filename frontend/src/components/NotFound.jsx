import { Link } from 'react-router-dom'

// Shown for any URL that doesn't match a route, e.g. a typo like /admn
function NotFound() {

    return (
        <div>
            <h2>Page not found</h2>
            <Link to="/">Back to carts</Link>
        </div>
    )
}

export default NotFound
