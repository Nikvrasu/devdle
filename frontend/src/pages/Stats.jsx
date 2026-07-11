import { useEffect, useState } from "react"
import { useAuth } from "../context/AuthContext"
import { api } from "../api/client"
import StatsChart from "../components/StatsChart"

export default function Stats() {
  const { user } = useAuth()
  const [stats, setStats] = useState(null)
  const [error, setError] = useState(false)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (!user) {
      setLoading(false)
      return
    }
    api
      .stats()
      .then(setStats)
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [user])

  if (!user) {
    return (
      <div className="mx-auto mt-20 max-w-sm text-center text-slate-500">
        Log in or register to see your stats.
      </div>
    )
  }

  if (loading) return <div className="mt-20 text-center text-slate-500">Loading…</div>
  if (error || !stats) {
    return <div className="mt-20 text-center text-red-600">Could not load stats.</div>
  }

  return (
    <div className="mx-auto max-w-md p-4">
      <h2 className="mb-4 text-xl font-bold text-slate-800">Your stats</h2>
      <div className="grid grid-cols-2 gap-3">
        <Stat label="Games played" value={stats.games_played} />
        <Stat label="Win rate" value={`${Math.round(stats.win_rate * 100)}%`} />
        <Stat label="Current streak" value={stats.current_streak} />
        <Stat label="Max streak" value={stats.max_streak} />
      </div>

      <h3 className="mb-2 mt-6 font-semibold text-slate-700">Guess distribution</h3>
      <StatsChart distribution={stats.guess_distribution} highlightGuess={stats.today_solved_guess} />
    </div>
  )
}

function Stat({ label, value }) {
  return (
    <div className="rounded-lg border border-slate-200 bg-white p-4 text-center shadow-sm">
      <div className="text-2xl font-bold text-indigo-600">{value}</div>
      <div className="text-xs uppercase tracking-wide text-slate-500">{label}</div>
    </div>
  )
}
