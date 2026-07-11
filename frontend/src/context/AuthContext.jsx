import { createContext, useContext, useEffect, useState } from "react"
import { api, setAccessToken, setOnUnauthorized } from "../api/client"

const AuthContext = createContext(null)

function decodeJwt(token) {
  try {
    const part = token.split(".")[1]
    return JSON.parse(atob(part))
  } catch {
    return null
  }
}

function applyToken(token) {
  setAccessToken(token)
  const claims = decodeJwt(token)
  return claims
    ? { id: claims.sub, username: claims.username, email: claims.email }
    : null
}

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null)

  useEffect(() => {
    // Clear auth state when a refresh fails (single source of truth).
    setOnUnauthorized(() => {
      setUser(null)
      setAccessToken(null)
    })
    // Silently restore the session from the httpOnly refresh cookie on load.
    api
      .refresh()
      .then((data) => setUser(applyToken(data.access_token)))
      .catch(() => {})
  }, [])

  const login = async (email, password) => {
    const data = await api.login({ email, password })
    setUser(applyToken(data.access_token))
  }

  const register = async (email, username, password) => {
    const data = await api.register({ email, username, password })
    setUser(applyToken(data.access_token))
  }

  const logout = async () => {
    try {
      await api.logout()
    } catch {
      /* ignore */
    }
    setUser(null)
    setAccessToken(null)
  }

  return (
    <AuthContext.Provider value={{ user, login, register, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}
