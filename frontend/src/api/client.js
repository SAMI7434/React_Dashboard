const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api'

export const apiFetch = async (path, options = {}) => {
  const { auth = true, headers = {}, body, ...rest } = options
  const token = window.localStorage.getItem('auth_token')

  const finalHeaders = { ...headers }
  let finalBody = body

  if (body && !(body instanceof FormData)) {
    finalHeaders['Content-Type'] = 'application/json'
    finalBody = JSON.stringify(body)
  }

  if (auth && token) {
    finalHeaders.Authorization = `Token ${token}`
  }

  const response = await fetch(`${API_BASE}${path}`, {
    ...rest,
    headers: finalHeaders,
    body: finalBody
  })

  if (!response.ok) {
    const errorText = await response.text()
    throw new Error(errorText || 'Request failed')
  }

  if (response.status === 204) {
    return null
  }
  return response.json()
}
