import { useState } from "react"

function buildEmojiGrid(correct, guessesRemaining) {
  const used = 5 - guessesRemaining
  if (correct) {
    return "🟥".repeat(Math.max(0, used - 1)) + "🟩"
  }
  return "🟥".repeat(5)
}

export default function ResultModal({ correct, correctAnswer, guessesRemaining }) {
  const [copied, setCopied] = useState(false)
  const grid = buildEmojiGrid(correct, guessesRemaining)
  const today = new Date().toISOString().slice(0, 10)
  const shareText = `Bugdle ${today}\n${grid}\n${correct ? "Solved!" : "Out of guesses"} — ${correctAnswer}`

  const copy = async () => {
    try {
      await navigator.clipboard.writeText(shareText)
      setCopied(true)
      setTimeout(() => setCopied(false), 1500)
    } catch {
      /* clipboard may be unavailable; ignore */
    }
  }

  return (
    <div className="fixed inset-0 z-20 flex items-center justify-center bg-black/40 p-4">
      <div className="w-full max-w-sm rounded-xl bg-white p-6 shadow-xl">
        <h2
          className={`mb-2 text-center text-2xl font-bold ${
            correct ? "text-green-600" : "text-red-600"
          }`}
        >
          {correct ? "Solved!" : "Out of guesses"}
        </h2>
        <p className="mb-4 text-center text-slate-600">
          The answer was: <span className="font-semibold text-slate-900">{correctAnswer}</span>
        </p>
        <pre className="mb-4 text-center text-2xl tracking-widest">{grid}</pre>
        <button
          onClick={copy}
          className="w-full rounded-md bg-indigo-600 py-2 font-semibold text-white hover:bg-indigo-700"
        >
          {copied ? "Copied!" : "Copy share text"}
        </button>
      </div>
    </div>
  )
}
