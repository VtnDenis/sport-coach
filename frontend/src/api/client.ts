const API_BASE = '/api'

export async function createSession(): Promise<string> {
  const res = await fetch(`${API_BASE}/sessions`, { method: 'POST' })
  const data = await res.json()
  return data.session_id
}

export async function listSessions() {
  const res = await fetch(`${API_BASE}/sessions`)
  return res.json()
}

export function chatSSE(sessionId: string, message: string, onChunk: (text: string) => void, onDone: (full: string) => void, onError: (err: string) => void): AbortController {
  const controller = new AbortController()

  fetch(`${API_BASE}/chat/${sessionId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message }),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        onError(`HTTP ${response.status}`)
        return
      }
      const reader = response.body?.getReader()
      if (!reader) return
      const decoder = new TextDecoder()
      let full = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        const text = decoder.decode(value, { stream: true })
        const lines = text.split('\n')
        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const event = JSON.parse(line.slice(6))
              if (event.type === 'text') {
                full += event.content
                onChunk(event.content)
              } else if (event.type === 'done') {
                onDone(event.content || full)
              } else if (event.type === 'error') {
                onError(event.content)
              }
            } catch {
              // skip malformed chunks
            }
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        onError(err.message)
      }
    })

  return controller
}

export async function getDashboardSummary() {
  const res = await fetch(`${API_BASE}/dashboard/summary`)
  return res.json()
}

export async function getDashboardActivities(limit = 10, source = 'strava') {
  const res = await fetch(`${API_BASE}/dashboard/activities?limit=${limit}&source=${source}`)
  return res.json()
}

export async function getDashboardHealth() {
  const res = await fetch(`${API_BASE}/dashboard/health`)
  return res.json()
}

export async function getHealth() {
  const res = await fetch(`${API_BASE}/health`)
  return res.json()
}
