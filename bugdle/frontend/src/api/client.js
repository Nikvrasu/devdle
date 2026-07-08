const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

// In-memory access token (never localStorage, per Phase 3). The AuthContext
// sets this after login / refresh.
let accessToken = null
let onUnauthorized = null

export function setAccessToken(token) {
  accessToken = token
}

export function setOnUnauthorized(cb) {
  onUnauthorized = cb
}

function buildHeaders() {
  const headers = { "Content-Type": "application/json" }
  if (accessToken) headers["Authorization"] = `Bearer ${accessToken}`
  return headers
}

async function request(path, options = {}) {
  const retry = options.retry !== false

  const res = await fetch(`${BASE_URL}${path}`, {
    ...options,
    // Include cookies (refresh token) on every request.
    credentials: "include",
    headers: buildHeaders(),
  })

  if (res.status === 401 && retry) {
    // Exactly one silent refresh attempt, then retry the original request once.
    try {
      const r = await fetch(`${BASE_URL}/api/auth/refresh`, {
        method: "POST",
        credentials: "include",
      })
      if (r.ok) {
        const d = await r.json()
        setAccessToken(d.access_token)
        return request(path, { ...options, retry: false })
      }
    } catch {
      /* fall through to unauthorized handling */
    }
    if (onUnauthorized) onUnauthorized()
  }

  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try {
      const data = await res.json()
      if (data && data.detail) {
        message = Array.isArray(data.detail)
          ? data.detail.map((d) => d.msg || d.message || String(d)).join("; ")
          : String(data.detail)
      }
    } catch {
      /* ignore non-JSON error bodies */
    }
    throw new Error(message)
  }

  if (res.status === 204) return null
  return res.json()
}

export const api = {
  getToday: () => request("/api/game/today"),
  submitGuess: (payload) =>
    request("/api/game/guess", { method: "POST", body: JSON.stringify(payload) }),

  login: (payload) =>
    request("/api/auth/login", { method: "POST", body: JSON.stringify(payload) }),
  register: (payload) =>
    request("/api/auth/register", { method: "POST", body: JSON.stringify(payload) }),
  // refresh must not trigger the auto-refresh retry loop
  refresh: () =>
    request("/api/auth/refresh", { method: "POST", retry: false }),
  logout: () => request("/api/auth/logout", { method: "POST", retry: false }),
}
