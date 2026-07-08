import { useMemo, useState } from "react"

export default function GuessInput({ options, disabled, onGuess }) {
  const [query, setQuery] = useState("")
  const [open, setOpen] = useState(false)

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return options
    return options.filter((o) => o.toLowerCase().includes(q))
  }, [query, options])

  const choose = (opt) => {
    setQuery("")
    setOpen(false)
    onGuess(opt)
  }

  return (
    <div className="relative">
      <input
        type="text"
        value={query}
        disabled={disabled}
        placeholder={disabled ? "Game over" : "Search for the root cause…"}
        onChange={(e) => {
          setQuery(e.target.value)
          setOpen(true)
        }}
        onFocus={() => setOpen(true)}
        onBlur={() => setTimeout(() => setOpen(false), 150)}
        className="w-full rounded-md border border-slate-300 px-3 py-2 text-slate-800 shadow-sm focus:border-indigo-500 focus:outline-none focus:ring-1 focus:ring-indigo-500 disabled:cursor-not-allowed disabled:bg-slate-100"
      />
      {open && !disabled && filtered.length > 0 && (
        <ul className="absolute z-10 mt-1 max-h-64 w-full overflow-auto rounded-md border border-slate-200 bg-white py-1 shadow-lg">
          {filtered.map((o) => (
            <li
              key={o}
              onMouseDown={() => choose(o)}
              className="cursor-pointer px-3 py-2 text-slate-700 hover:bg-indigo-50"
            >
              {o}
            </li>
          ))}
        </ul>
      )}
    </div>
  )
}
