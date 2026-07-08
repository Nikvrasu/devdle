const BASE_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"

function buildHeaders() {
  const headers = { "Content-Type": "application/json" }
  // Phase 3 will attach an Authorization header here from the in-memory token.
  return headers
}

async function request(path, options = {}) {
  let res
  try {
    res = await fetch(`${BASE_URL}${path}`, {
      ...options,
      headers: buildHeaders(),
    })
  } catch (e) {
    throw new Error("Network error — is the backend running?")
  }

  if (!res.ok) {
    let message = `Request failed (${res.status})`
    try {
      const data = await res.json()
      if (data && data.detail) {
        message = Array.isArray(data.detail)
          ? data.detail.map((d) => d.msg || d.message || String(d)).join("; ")
          : String(data.detail)
      }
    } catch {
      /* ignore non-JSON error bodies */
    }
    throw new Error(message)
  }

  if (res.status === 204) return null
  return res.json()
}

export const api = {
  getToday: () => request("/api/game/today"),
  submitGuess: (payload) =>
    request("/api/game/guess", {
      method: "POST",
      body: JSON.stringify(payload),
    }),
}
