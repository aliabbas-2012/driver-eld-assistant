import { useEffect, useState } from 'react'
import './App.css'

type HealthResponse = { status: string; service: string }

function App() {
  const [health, setHealth] = useState<HealthResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    fetch('/api/health/')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json() as Promise<HealthResponse>
      })
      .then(setHealth)
      .catch(() => setError('Could not reach Django API (is it running on port 8000?)'))
  }, [])

  return (
    <main className="shell">
      <h1>Driver ELD Assistant</h1>
      <p className="lede">Django + React scaffold. Add product requirements next.</p>
      <section className="panel" aria-live="polite">
        <h2>API health</h2>
        {health && (
          <pre className="json">{JSON.stringify(health, null, 2)}</pre>
        )}
        {error && <p className="error">{error}</p>}
      </section>
    </main>
  )
}

export default App
