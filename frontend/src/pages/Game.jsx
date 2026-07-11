import { useEffect, useState } from "react"
import { api } from "../api/client"
import ClueCard from "../components/ClueCard"
import GuessInput from "../components/GuessInput"
import ResultModal from "../components/ResultModal"

function storageKey() {
  const d = new Date()
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, "0")
  const day = String(d.getDate()).padStart(2, "0")
  return `bugdle-${y}-${m}-${day}`
}

export default function Game() {
  const [state, setState] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(false)
  const [dismissed, setDismissed] = useState(false)

  // On mount: prefer the saved game (so a refresh resumes) over a fresh fetch.
  useEffect(() => {
    const saved = localStorage.getItem(storageKey())
    if (saved) {
      try {
        setState(JSON.parse(saved))
        setLoading(false)
        return
      } catch {
        localStorage.removeItem(storageKey())
      }
    }
    api
      .getToday()
      .then((data) => setState(data))
      .catch(() => setError(true))
      .finally(() => setLoading(false))
  }, [])

  // Persist the current game so a refresh resumes rather than restarting.
  useEffect(() => {
    if (state) localStorage.setItem(storageKey(), JSON.stringify(state))
  }, [state])

  // Show the result modal again for a fresh (non-finished) game.
  useEffect(() => {
    if (state && !state.game_over) setDismissed(false)
  }, [state])

  const handleGuess = (answer) => {
    if (!state || state.game_over) return
    api
      .submitGuess({ attempt_token: state.attempt_token, answer })
      .then((res) => {
        setState((prev) => ({
          ...prev,
          attempt_token: res.attempt_token,
          clues: res.next_clue ? [...prev.clues, res.next_clue] : prev.clues,
          guesses_remaining: res.guesses_remaining,
          game_over: res.game_over,
          correct: res.correct,
          correct_answer: res.correct_answer ?? prev.correct_answer,
        }))
      })
      .catch((err) => alert(err.message))
  }

  if (loading) {
    return <div className="mt-20 text-center text-slate-500">Loading…</div>
  }
  if (error || !state) {
    return (
      <div className="mt-20 text-center text-red-600">
        Could not load today's puzzle. Is the backend running?
      </div>
    )
  }

  return (
    <div className="mx-auto max-w-xl p-4">
      <header className="mb-4 text-center">
        <h1 className="text-3xl font-bold text-indigo-600">Bugdle</h1>
        <p className="text-sm text-slate-500">
          Category: {state.scenario_category} · Guesses left: {state.guesses_remaining}
        </p>
      </header>

      <div className="space-y-3">
        {state.clues.map((c) => (
          <ClueCard key={c.order} order={c.order} text={c.text} />
        ))}
      </div>

      {state.game_over && (
        <div
          className={`mt-3 rounded-lg border p-4 ${
            state.correct
              ? "border-green-300 bg-green-50 text-green-800"
              : "border-slate-300 bg-slate-50 text-slate-700"
          }`}
        >
          <div className="text-xs font-semibold uppercase tracking-wide opacity-70">
            Solution
          </div>
          <div className="mt-1 text-lg font-semibold">{state.correct_answer}</div>
        </div>
      )}

      {!state.game_over && (
        <div className="mt-4">
          <GuessInput
            options={state.answer_options}
            disabled={state.game_over}
            onGuess={handleGuess}
          />
        </div>
      )}

      {state.game_over && !dismissed && (
        <ResultModal
          correct={state.correct}
          correctAnswer={state.correct_answer}
          guessesRemaining={state.guesses_remaining}
          onClose={() => setDismissed(true)}
        />
      )}
    </div>
  )
}
