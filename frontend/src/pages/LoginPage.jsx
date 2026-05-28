import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useAuth } from '../hooks/useAuth.js'

const LoginPage = () => {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [formData, setFormData] = useState({ username: '', password: '' })
  const [error, setError] = useState(null)
  const [isSubmitting, setIsSubmitting] = useState(false)

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError(null)
    setIsSubmitting(true)
    try {
      await login(formData)
      navigate('/')
    } catch (err) {
      setError('Login failed. Check your credentials.')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center px-6">
      <div className="glass-panel rounded-3xl p-10 max-w-md w-full">
        <p className="text-xs uppercase tracking-[0.3em] text-cyan-300">Analyst Access</p>
        <h1 className="text-3xl font-semibold mt-2">Utility Billing Console</h1>
        <p className="text-slate-400 text-sm mt-2">
          Sign in to review and approve utility billing records.
        </p>
        <form onSubmit={handleSubmit} className="mt-6 space-y-4">
          <div>
            <label className="text-xs text-slate-400">Username</label>
            <input
              type="text"
              value={formData.username}
              onChange={(event) => setFormData({ ...formData, username: event.target.value })}
              className="w-full mt-1 px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-sm"
              required
            />
          </div>
          <div>
            <label className="text-xs text-slate-400">Password</label>
            <input
              type="password"
              value={formData.password}
              onChange={(event) => setFormData({ ...formData, password: event.target.value })}
              className="w-full mt-1 px-3 py-2 rounded-lg bg-slate-900/70 border border-slate-700 text-sm"
              required
            />
          </div>
          {error ? <p className="text-sm text-rose-300">{error}</p> : null}
          <button
            type="submit"
            disabled={isSubmitting}
            className="w-full mt-2 px-4 py-2 rounded-full bg-cyan-500/30 text-cyan-100 hover:bg-cyan-500/40"
          >
            {isSubmitting ? 'Signing in...' : 'Sign in'}
          </button>
        </form>
      </div>
    </div>
  )
}

export default LoginPage
