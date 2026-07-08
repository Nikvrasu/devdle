export default function StatsChart({ distribution, highlightGuess }) {
  // distribution: { 1: n, 2: n, 3: n, 4: n, 5: n }
  const max = Math.max(1, ...Object.values(distribution))

  return (
    <div className="space-y-2">
      {[1, 2, 3, 4, 5].map((g) => {
        const count = distribution[g] || 0
        const pct = (count / max) * 100
        const highlight = highlightGuess === g
        return (
          <div key={g} className="flex items-center gap-3">
            <span className="w-4 text-right text-sm font-medium text-slate-500">{g}</span>
            <div className="h-6 flex-1 overflow-hidden rounded bg-slate-100">
              <div
                className={`flex h-full items-center justify-end rounded px-2 text-xs font-semibold text-white transition-all duration-500 ${
                  highlight ? "bg-emerald-500" : "bg-indigo-500"
                }`}
                style={{ width: `${pct}%`, minWidth: count ? "2rem" : "0" }}
              >
                {count > 0 ? count : ""}
              </div>
            </div>
          </div>
        )
      })}
    </div>
  )
}
