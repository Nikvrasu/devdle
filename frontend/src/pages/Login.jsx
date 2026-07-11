import { useState } from "react"
import { useAuth } from "../context/AuthContext"

export default function Login({ onDone }) {
  const { login, register } = useAuth()
  const [mode, setMode] = useState("login") // "login" | "register"
  const [email, setEmail] = useState("")
  const [username, setUsername] = useState("")
  const [password, setPassword] = useState("")
  const [error, setError] = useState("")

  const submit = async (e) => {
    e.preventDefault()
    setError("")
    try {
      if (mode === "login") {
        await login(email, password)
      } else {
        await register(email, username, password)
      }
      onDone && onDone()
    } catch (err) {
      setError(err.message)
    }
  }

  return (
    <div className="mx-auto mt-10 max-w-sm rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
      <div className="mb-4 flex justify-center gap-2 text-sm font-semibold">
        <button
          type="button"
          onClick={() => setMode("login")}
          className={mode === "login" ? "text-indigo-600" : "text-slate-400"}
        >
          Log in
        </button>
        <span className="text-slate-300">|</span>
        <button
          type="button"
          onClick={() => setMode("register")}
          className={mode === "register" ? "text-indigo-600" : "text-slate-400"}
        >
          Register
        </button>
      </div>

      <form onSubmit={submit} className="space-y-3">
        <input
          type="email"
          required
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-indigo-500 focus:outline-none"
        />
        {mode === "register" && (
          <input
            type="text"
            required
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-indigo-500 focus:outline-none"
          />
        )}
        <input
          type="password"
          required
          placeholder="Password (min 8 chars)"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full rounded-md border border-slate-300 px-3 py-2 focus:border-indigo-500 focus:outline-none"
        />
        {error && <p className="text-sm text-red-600">{error}</p>}
        <button
          type="submit"
          className="w-full rounded-md bg-indigo-600 py-2 font-semibold text-white hover:bg-indigo-700"
        >
          {mode === "login" ? "Log in" : "Register"}
        </button>
      </form>
    </div>
  )
}
