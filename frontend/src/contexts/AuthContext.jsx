import { createContext, useEffect, useMemo, useState } from 'react'
import { getMe, login as loginRequest } from '../api/ingest.js'

export const AuthContext = createContext(null)

export const AuthProvider = ({ children }) => {
  const [token, setToken] = useState(() => window.localStorage.getItem('auth_token'))
  const [user, setUser] = useState(() => {
    const stored = window.localStorage.getItem('auth_user')
    return stored ? JSON.parse(stored) : null
  })
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    if (!token) {
      setUser(null)
      return
    }

    setIsLoading(true)
    getMe()
      .then((data) => {
        setUser(data)
        window.localStorage.setItem('auth_user', JSON.stringify(data))
      })
      .catch(() => {
        setToken(null)
        setUser(null)
        window.localStorage.removeItem('auth_token')
        window.localStorage.removeItem('auth_user')
      })
      .finally(() => setIsLoading(false))
  }, [token])

  const login = async (credentials) => {
    const data = await loginRequest(credentials)
    setToken(data.token)
    setUser(data.user)
    window.localStorage.setItem('auth_token', data.token)
    window.localStorage.setItem('auth_user', JSON.stringify(data.user))
  }

  const logout = () => {
    setToken(null)
    setUser(null)
    window.localStorage.removeItem('auth_token')
    window.localStorage.removeItem('auth_user')
  }

  const value = useMemo(
    () => ({ token, user, login, logout, isLoading }),
    [token, user, isLoading]
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
