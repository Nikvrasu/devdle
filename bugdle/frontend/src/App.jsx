import { useState } from "react"
import Game from "./pages/Game"
import Login from "./pages/Login"
import { useAuth } from "./context/AuthContext"

export default function App() {
  const { user, logout } = useAuth()
  const [view, setView] = useState("game") // "game" | "login"

  return (
    <div className="min-h-screen bg-slate-50">
      <header className="flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3">
        <button
          onClick={() => setView("game")}
          className="text-2xl font-bold text-indigo-600"
        >
          Bugdle
        </button>
        <nav>
          {user ? (
            <div className="flex items-center gap-3">
              <span className="text-sm text-slate-600">{user.username}</span>
              <button
                onClick={async () => {
                  await logout()
                  setView("game")
                }}
                className="rounded-md border border-slate-300 px-3 py-1 text-sm font-medium text-slate-700 hover:bg-slate-100"
              >
                Log out
              </button>
            </div>
          ) : (
            <button
              onClick={() => setView("login")}
              className="rounded-md bg-indigo-600 px-3 py-1 text-sm font-medium text-white hover:bg-indigo-700"
            >
              Log in
            </button>
          )}
        </nav>
      </header>
      <main>{view === "game" ? <Game /> : <Login onDone={() => setView("game")} />}</main>
    </div>
  )
}
