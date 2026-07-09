import { useMemo, useState } from 'react'

const suggestionPrompts = [
  'Berapa angka inflasi bulan lalu?',
  'Tampilkan tren kemiskinan 2023',
  'Analisis Gini Ratio per provinsi',
]

const features = [
  { label: 'Statistical Q&A', active: true },
  { label: 'Report Summarizer' },
  { label: 'Trend Prediction' },
  { label: 'Anomaly Analysis' },
]

export default function ChatbotPage() {
  const [input, setInput] = useState('')
  const [messages, setMessages] = useState([
    {
      sender: 'assistant',
      text: 'Halo! Saya SADA-AI. Tanyakan data statistik Aceh, dan saya akan mengambil jawaban berdasarkan sumber yang tersedia.',
    },
  ])
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')

  const latestAssistantReply = useMemo(() => {
    const assistantMessages = messages.filter((m) => m.sender === 'assistant')
    return assistantMessages[assistantMessages.length - 1]?.text || ''
  }, [messages])

  const historyItems = useMemo(() => {
    return messages
      .filter((message) => message.sender === 'user')
      .slice(-4)
      .reverse()
      .map((message) => ({
        title: message.text,
        subtitle: 'Baru saja',
      }))
  }, [messages])

  const renderMessageText = (text) => {
    const urlRegex = /(https?:\/\/[\w\-\.\?\,\'\/\+&%\$#_=~:;@!*]+)(?![^<]*>)/g
    const parts = text.split(urlRegex)

    return parts.map((part, index) => {
      if (urlRegex.test(part)) {
        return (
          <a
            key={index}
            href={part}
            target="_blank"
            rel="noopener noreferrer"
            className="text-red-700 hover:underline break-words"
          >
            {part}
          </a>
        )
      }

      return <span key={index}>{part}</span>
    })
  }

  const appendMessage = (message) => {
    setMessages((prev) => [...prev, message])
  }

  const handleSend = async (question) => {
    const prompt = question || input.trim()
    if (!prompt) {
      return
    }

    setError('')
    setInput('')
    appendMessage({ sender: 'user', text: prompt })
    setLoading(true)

    try {
      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: prompt }),
      })

      if (!response.ok) {
        throw new Error(`Backend error ${response.status}`)
      }

      const data = await response.json()
      const answer = data.answer || 'Maaf, saya tidak mendapatkan jawaban yang valid dari server.'
      appendMessage({ sender: 'assistant', text: answer })
    } catch (err) {
      setError('Gagal mengambil jawaban. Pastikan backend FastAPI berjalan pada http://localhost:8000.')
      appendMessage({ sender: 'assistant', text: 'Terjadi kesalahan saat memproses permintaan Anda. Silakan coba lagi.' })
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <div className="grid lg:grid-cols-[280px_minmax(0,1fr)] gap-6 p-6">
        <aside className="hidden lg:flex flex-col rounded-[32px] bg-white border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 pt-6 pb-4">
            <div className="inline-flex items-center gap-3 px-3 py-2 rounded-full bg-red-50 text-red-700 font-semibold text-sm">
              <span className="material-symbols-outlined">insights</span>
              STAT-AI
            </div>
            <p className="mt-5 text-xs uppercase tracking-[0.24em] text-slate-500">Data Intelligence</p>
            <h2 className="mt-4 text-2xl font-semibold text-slate-900">Chatbot Statistik</h2>
            <p className="mt-3 text-sm text-slate-500 leading-relaxed">Tanyakan data statistik Aceh secara natural, dan saya akan menjawab berdasarkan database yang tersedia.</p>
          </div>
          <div className="px-6 pb-6">
            <div className="grid gap-3">
              {features.map((feature) => (
                <button
                  key={feature.label}
                  className={`text-left rounded-3xl px-4 py-3 text-sm font-semibold transition ${feature.active ? 'bg-red-700 text-white shadow-sm' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'}`}
                >
                  {feature.label}
                </button>
              ))}
            </div>
          </div>

          <div className="border-t border-slate-200 px-6 py-6 mt-auto">
            <h3 className="text-xs uppercase tracking-[0.24em] text-slate-500 mb-4">Riwayat Analisis</h3>
            <div className="space-y-3">
              {historyItems.map((item) => (
                <div key={item.title} className="rounded-3xl border border-slate-200 bg-slate-50 px-4 py-3">
                  <p className="text-sm font-semibold text-slate-900 truncate">{item.title}</p>
                  <p className="text-[11px] text-slate-500 mt-1">{item.subtitle}</p>
                </div>
              ))}
            </div>
          </div>
        </aside>

        <main className="space-y-6">
          <section className="rounded-[32px] bg-white border border-slate-200 p-6 shadow-sm">
            <div className="flex flex-col xl:flex-row xl:items-center xl:justify-between gap-6">
              <div>
                <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Statistical Q&A</p>
                <h1 className="mt-3 text-3xl font-semibold text-slate-900">Ajukan pertanyaan data statistik Aceh</h1>
                <p className="mt-3 max-w-2xl text-sm text-slate-500">Gunakan chat untuk mendapatkan ringkasan, insight, dan jawaban dari data yang tersedia.</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="rounded-3xl bg-slate-50 p-5">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Pertanyaan populer</p>
                  <p className="mt-3 font-semibold text-slate-900">{suggestionPrompts[0]}</p>
                </div>
                <div className="rounded-3xl bg-red-700 p-5 text-white">
                  <p className="text-xs uppercase tracking-[0.24em] text-red-200">Jawaban terakhir</p>
                  <p className="mt-3 text-lg font-semibold">{latestAssistantReply || 'Ajukan pertanyaan untuk melihat jawaban.'}</p>
                </div>
              </div>
            </div>
          </section>

          <section className="grid gap-6">
            <div className="rounded-[32px] bg-white border border-slate-200 p-6 shadow-sm">
              <div className="flex flex-col md:flex-row md:items-center md:justify-between gap-4 pb-4 border-b border-slate-200">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Chatbot</p>
                  <h2 className="mt-2 text-xl font-semibold text-slate-900">Tanyakan data statistik secara natural</h2>
                </div>
                <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-2 text-sm text-slate-700">
                  <span className="material-symbols-outlined">shield</span>
                  Terverifikasi BPS
                </div>
              </div>

              <div className="mt-6 space-y-4">
                {messages.map((message, index) => (
                  <div
                    key={`${message.sender}-${index}`}
                    className={`rounded-[28px] p-5 shadow-sm ${message.sender === 'assistant' ? 'bg-slate-50 text-slate-900' : 'bg-red-700 text-white self-end'}`}
                  >
                    <p className="text-sm leading-relaxed">{renderMessageText(message.text)}</p>
                  </div>
                ))}
                {loading && (
                  <div className="rounded-[28px] p-5 shadow-sm bg-slate-50 text-slate-900">
                    <p className="text-sm leading-relaxed">SADA-AI sedang mengetik<span className="animate-pulse">...</span></p>
                  </div>
                )}
              </div>

              <div className="mt-8 rounded-[32px] border border-slate-200 bg-slate-50 p-5">
                <div className="grid gap-4 sm:grid-cols-3">
                  {suggestionPrompts.map((item) => (
                    <button
                      key={item}
                      type="button"
                      onClick={() => handleSend(item)}
                      className="rounded-3xl border border-slate-200 bg-white px-4 py-3 text-left text-sm font-semibold text-slate-900 hover:border-red-700 hover:text-red-700 transition"
                    >
                      {item}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </section>

          <section className="rounded-[32px] bg-white border border-slate-200 p-6 shadow-sm">
            <div className="max-w-4xl mx-auto">
              <div className="relative flex items-center gap-3 rounded-[28px] border border-slate-200 bg-slate-50 p-4 shadow-sm">
                <button className="rounded-3xl bg-white px-4 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-100 transition">Upload File</button>
                <input
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter') {
                      event.preventDefault()
                      handleSend('')
                    }
                  }}
                  className="flex-1 rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 focus:border-red-700 focus:outline-none"
                  placeholder="Ketik pertanyaan statistik Anda di sini..."
                />
                <button
                  type="button"
                  disabled={loading}
                  onClick={() => handleSend('')}
                  className="inline-flex items-center gap-2 rounded-3xl bg-red-700 px-4 py-3 text-sm font-semibold text-white hover:bg-red-800 transition disabled:cursor-not-allowed disabled:opacity-50"
                >
                  <span className="material-symbols-outlined">send</span>
                  Kirim
                </button>
              </div>
              {error && <p className="mt-3 text-center text-sm text-red-600">{error}</p>}
              <p className="mt-3 text-center text-xs uppercase tracking-[0.24em] text-slate-500">SADA-AI mungkin membuat kesalahan. Verifikasi hasil melalui Dashboard Resmi BPS.</p>
            </div>
          </section>
        </main>
      </div>
    </div>
  )
}
