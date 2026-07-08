import { useEffect, useState } from "react"

export default function ClueCard({ order, text }) {
  const [shown, setShown] = useState(false)

  useEffect(() => {
    const t = setTimeout(() => setShown(true), 10)
    return () => clearTimeout(t)
  }, [])

  return (
    <div
      className={`rounded-lg border border-slate-200 bg-white p-4 shadow-sm transition-all duration-500 ease-out ${
        shown ? "translate-y-0 opacity-100" : "translate-y-2 opacity-0"
      }`}
    >
      <div className="mb-1 text-xs font-semibold uppercase tracking-wide text-indigo-600">
        Clue {order}
      </div>
      <p className="text-slate-700">{text}</p>
    </div>
  )
}
