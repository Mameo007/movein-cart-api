// The admin token lives in localStorage so a refresh doesn't log you out.
// This is only for convenience -- the API is what actually enforces access.
const TOKEN_KEY = 'admin_token'

export function getToken() {
    return localStorage.getItem(TOKEN_KEY)
}

export function setToken(token) {
    localStorage.setItem(TOKEN_KEY, token)
}

export function clearToken() {
    localStorage.removeItem(TOKEN_KEY)
}

export function authHeaders() {
    return { Authorization: `Bearer ${getToken()}` }
}
