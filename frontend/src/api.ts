import axios from 'axios'

const base = import.meta.env.VITE_API_BASE_URL || ''

export const api = axios.create({
  baseURL: base || undefined,
  headers: { 'Content-Type': 'application/json' },
})

api.interceptors.request.use((config) => {
  const t = localStorage.getItem('access_token')
  if (t) {
    config.headers.Authorization = `Bearer ${t}`
  }
  return config
})

export type TokenPair = { access: string; refresh: string }

export async function login(username: string, password: string): Promise<TokenPair> {
  const { data } = await api.post<TokenPair>('/api/auth/token/', { username, password })
  localStorage.setItem('access_token', data.access)
  localStorage.setItem('refresh_token', data.refresh)
  return data
}

export function logout() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
}

export function isLoggedIn() {
  return !!localStorage.getItem('access_token')
}
