import { useCallback, useMemo, useState } from 'react'
import { api, isLoggedIn, login, logout } from './api'
import { LogGridCanvas } from './LogGridCanvas'
import { TripMap } from './TripMap'

type DutyRow = {
  id: number
  status: string
  start_time: string
  end_time: string
  duration_hours: string | null
  location: string
}

type DailyLog = {
  id: number
  log_date: string
  day_number: number
  total_miles_driven: number
  driving_hours: string
  on_duty_hours: string
  remarks: string
  log_grid_data: { intervals?: Record<string, { start_h: number; end_h: number }[]> }
  duty_changes: DutyRow[]
}

type TripDetail = {
  id: number
  current_location: string
  pickup_location: string
  dropoff_location: string
  total_distance_miles: number | null
  total_days: number | null
  trip_start_date: string | null
  route_geometry_json: { coordinates?: [number, number][] } | null
  daily_logs: DailyLog[]
}

export default function App() {
  const [logged, setLogged] = useState(isLoggedIn())
  const [username, setUsername] = useState('demodriver')
  const [password, setPassword] = useState('demo12345')
  const [busy, setBusy] = useState(false)
  const [err, setErr] = useState<string | null>(null)
  const [trip, setTrip] = useState<TripDetail | null>(null)

  const [current, setCurrent] = useState('Chicago, IL')
  const [pickup, setPickup] = useState('Indianapolis, IN')
  const [dropoff, setDropoff] = useState('Atlanta, GA')
  const [cycleUsed, setCycleUsed] = useState('35')
  const [startDate, setStartDate] = useState(() => new Date().toISOString().slice(0, 10))

  const coords = useMemo(
    () => trip?.route_geometry_json?.coordinates ?? null,
    [trip],
  )

  const doLogin = useCallback(async () => {
    setErr(null)
    setBusy(true)
    try {
      await login(username, password)
      setLogged(true)
    } catch {
      setErr('Login failed. Run backend seed: python manage.py seed_demo')
    } finally {
      setBusy(false)
    }
  }, [username, password])

  const doPlan = useCallback(async () => {
    setErr(null)
    setBusy(true)
    setTrip(null)
    try {
      const { data } = await api.post<TripDetail>('/api/trips/plan/', {
        current_location: current,
        pickup_location: pickup,
        dropoff_location: dropoff,
        cycle_used_hours: cycleUsed,
        trip_start_date: startDate,
        shipping_doc_number: 'BOL-PLAN',
        shipper_name: '',
        commodity: 'General freight',
      })
      setTrip(data)
    } catch (e: unknown) {
      const ax = e as { response?: { data?: { detail?: string } } }
      setErr(ax.response?.data?.detail || 'Planning failed (geocode/OSRM may be rate-limited).')
    } finally {
      setBusy(false)
    }
  }, [current, pickup, dropoff, cycleUsed, startDate])

  if (!logged) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-sky-950 flex items-center justify-center p-6">
        <div className="w-full max-w-md rounded-2xl bg-white/95 shadow-2xl p-8 border border-white/20">
          <h1 className="text-2xl font-semibold text-slate-900 tracking-tight">Driver ELD Assistant</h1>
          <p className="text-slate-600 text-sm mt-2">Sign in to plan trips, view routes, and ELD logs.</p>
          <label className="block mt-6 text-sm font-medium text-slate-700">Username</label>
          <input
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <label className="block mt-4 text-sm font-medium text-slate-700">Password</label>
          <input
            type="password"
            className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2 text-slate-900"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          {err && <p className="mt-4 text-sm text-red-600">{err}</p>}
          <button
            type="button"
            disabled={busy}
            onClick={doLogin}
            className="mt-6 w-full rounded-xl bg-sky-600 hover:bg-sky-500 text-white font-medium py-3 disabled:opacity-50"
          >
            {busy ? 'Signing in…' : 'Sign in'}
          </button>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <header className="border-b border-slate-200 bg-white/80 backdrop-blur sticky top-0 z-20">
        <div className="max-w-6xl mx-auto px-4 py-4 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold tracking-tight">Driver ELD Assistant</h1>
            <p className="text-xs text-slate-500">Property 70/8 · OSM map · Planned logs</p>
          </div>
          <button
            type="button"
            onClick={() => {
              logout()
              setLogged(false)
              setTrip(null)
            }}
            className="text-sm text-slate-600 hover:text-slate-900 underline"
          >
            Sign out
          </button>
        </div>
      </header>

      <main className="max-w-6xl mx-auto px-4 py-8 space-y-10">
        <section className="rounded-2xl bg-white border border-slate-200 shadow-sm p-6 md:p-8">
          <h2 className="text-base font-semibold text-slate-800">Trip inputs</h2>
          <p className="text-sm text-slate-500 mt-1">
            Current location, pickup, dropoff, and hours already used in your 70-hour / 8-day window.
          </p>
          <div className="mt-6 grid gap-4 md:grid-cols-2">
            <div>
              <label className="text-xs font-medium uppercase tracking-wide text-slate-500">Current location</label>
              <input className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" value={current} onChange={(e) => setCurrent(e.target.value)} />
            </div>
            <div>
              <label className="text-xs font-medium uppercase tracking-wide text-slate-500">Pickup location</label>
              <input className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" value={pickup} onChange={(e) => setPickup(e.target.value)} />
            </div>
            <div>
              <label className="text-xs font-medium uppercase tracking-wide text-slate-500">Dropoff location</label>
              <input className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" value={dropoff} onChange={(e) => setDropoff(e.target.value)} />
            </div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-slate-500">Cycle used (hrs)</label>
                <input className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" value={cycleUsed} onChange={(e) => setCycleUsed(e.target.value)} />
              </div>
              <div>
                <label className="text-xs font-medium uppercase tracking-wide text-slate-500">Start date</label>
                <input type="date" className="mt-1 w-full rounded-lg border border-slate-300 px-3 py-2" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
              </div>
            </div>
          </div>
          {err && <p className="mt-4 text-sm text-red-600">{err}</p>}
          <button
            type="button"
            disabled={busy}
            onClick={doPlan}
            className="mt-6 rounded-xl bg-gradient-to-r from-sky-600 to-indigo-600 text-white font-medium px-8 py-3 shadow-md hover:opacity-95 disabled:opacity-50"
          >
            {busy ? 'Geocoding & planning…' : 'Plan trip & build logs'}
          </button>
          <p className="mt-3 text-xs text-slate-400">
            Uses Nominatim + OSRM (public). Respect rate limits; first plan may take ~10s.
          </p>
        </section>

        {trip && (
          <>
            <section className="rounded-2xl bg-white border border-slate-200 shadow-sm p-6 md:p-8">
              <h2 className="text-base font-semibold text-slate-800">Route map</h2>
              <p className="text-sm text-slate-500 mt-1">
                ~{trip.total_distance_miles ?? '—'} mi · {trip.total_days ?? '—'} day(s) · Trip #{trip.id}
              </p>
              <div className="mt-4 overflow-hidden rounded-xl border border-slate-200">
                <TripMap
                  coordinates={coords || undefined}
                  labels={{ start: trip.current_location, pickup: trip.pickup_location, end: trip.dropoff_location }}
                />
              </div>
            </section>

            <section className="space-y-6">
              <h2 className="text-base font-semibold text-slate-800 px-1">Daily log sheets</h2>
              {trip.daily_logs.map((log) => (
                <article
                  key={log.id}
                  className="rounded-2xl bg-white border border-slate-200 shadow-sm overflow-hidden"
                >
                  <div className="bg-slate-900 text-white px-4 py-3 flex flex-wrap gap-4 justify-between items-center">
                    <span className="font-medium">Day {log.day_number}</span>
                    <span className="text-sky-200">{log.log_date}</span>
                    <span className="text-slate-300 text-sm">
                      Drive {log.driving_hours}h · {log.total_miles_driven} mi
                    </span>
                  </div>
                  <div className="p-4 md:p-6 space-y-4">
                    <LogGridCanvas logDate={log.log_date} gridData={log.log_grid_data} />
                    <div className="overflow-x-auto text-sm">
                      <table className="min-w-full border-collapse">
                        <thead>
                          <tr className="bg-slate-100 text-left text-xs uppercase text-slate-600">
                            <th className="p-2 border border-slate-200">Status</th>
                            <th className="p-2 border border-slate-200">Start</th>
                            <th className="p-2 border border-slate-200">End</th>
                            <th className="p-2 border border-slate-200">Hrs</th>
                            <th className="p-2 border border-slate-200">Location</th>
                          </tr>
                        </thead>
                        <tbody>
                          {log.duty_changes.map((d) => (
                            <tr key={d.id} className="hover:bg-slate-50">
                              <td className="p-2 border border-slate-200 font-mono text-xs">{d.status}</td>
                              <td className="p-2 border border-slate-200 font-mono text-xs">{d.start_time}</td>
                              <td className="p-2 border border-slate-200 font-mono text-xs">{d.end_time}</td>
                              <td className="p-2 border border-slate-200">{d.duration_hours}</td>
                              <td className="p-2 border border-slate-200 text-slate-700">{d.location}</td>
                            </tr>
                          ))}
                        </tbody>
                      </table>
                    </div>
                    {log.remarks && (
                      <p className="text-xs text-slate-500 border-t border-slate-100 pt-3">
                        <span className="font-semibold text-slate-600">Remarks: </span>
                        {log.remarks}
                      </p>
                    )}
                  </div>
                </article>
              ))}
            </section>
          </>
        )}
      </main>
    </div>
  )
}
