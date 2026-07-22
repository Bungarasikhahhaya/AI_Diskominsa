import { useEffect, useMemo, useRef, useState } from 'react'
import { TrendPointChart } from './TrendPrediction'

const suggestionPrompts = [
  'Berapa angka inflasi bulan lalu?',
  'Tampilkan tren kemiskinan 2023',
  'Analisis Gini Ratio per provinsi',
]

const features = [
  { label: 'Statistical Q&A', icon: '◌', destination: 'Statistical Q&A' },
  { label: 'AI Narasi Laporan', icon: '▤', destination: 'AI Narasi Laporan Otomatis' },
  { label: 'Trend Prediction', icon: '↗', destination: 'AI Prediksi Tren Data' },
  { label: 'Anomaly Analysis', icon: '✦' },
]

const welcomeMessage = {
  sender: 'assistant',
  text: 'Halo! Saya SADA-AI. Tanyakan data statistik Aceh, dan saya akan mengambil jawaban berdasarkan sumber yang tersedia.',
}

const createRoom = (id) => ({
  id,
  title: 'Analisis baru',
  messages: [welcomeMessage],
})

export default function ChatbotPage({ onNavigate }) {
  const [input, setInput] = useState('')
  const [rooms, setRooms] = useState(() => [createRoom('room-1')])
  const [activeRoomId, setActiveRoomId] = useState('room-1')
  const [loadingRoomId, setLoadingRoomId] = useState(null)
  const [error, setError] = useState('')
  const [featureNotice, setFeatureNotice] = useState('')
  const abortControllerRef = useRef(null)
  const roomSequenceRef = useRef(1)

  useEffect(() => () => abortControllerRef.current?.controller.abort(), [])

  const activeRoom = rooms.find((room) => room.id === activeRoomId) || rooms[0]
  const messages = activeRoom?.messages || []
  const loading = loadingRoomId === activeRoomId

  const historyItems = useMemo(() => {
    return [...rooms]
      .reverse()
      .map((room) => ({
        id: room.id,
        title: room.title,
        subtitle: `${room.messages.filter((message) => message.sender === 'user').length} pertanyaan`,
      }))
  }, [rooms])

  const renderInlineText = (text) => {
    const tokenRegex = /(https?:\/\/[^\s]+|\*\*[^*]+\*\*)/g
    return text.split(tokenRegex).filter(Boolean).map((part, index) => {
      if (part.startsWith('http://') || part.startsWith('https://')) {
        return (
          <a key={index} href={part} target="_blank" rel="noopener noreferrer" className="text-red-700 hover:underline break-words">
            Buka sumber Satu Data Aceh
          </a>
        )
      }
      if (part.startsWith('**') && part.endsWith('**')) {
        return <strong key={index} className="font-semibold text-slate-900">{part.slice(2, -2)}</strong>
      }
      return <span key={index}>{part}</span>
    })
  }

  const renderMessageText = (text) => text.split('\n').map((line, index) => (
    <div key={index} className={line ? 'min-h-[1.25rem]' : 'h-3'}>
      {renderInlineText(line)}
    </div>
  ))

  const appendMessage = (roomId, message) => {
    setRooms((previousRooms) => previousRooms.map((room) => (
      room.id === roomId ? { ...room, messages: [...room.messages, message] } : room
    )))
  }

  const handleSend = async (question) => {
    const prompt = question || input.trim()
    if (!prompt || loadingRoomId) {
      return
    }

    const roomId = activeRoomId
    setError('')
    setInput('')
    setRooms((previousRooms) => previousRooms.map((room) => {
      if (room.id !== roomId) return room
      const isFirstQuestion = !room.messages.some((message) => message.sender === 'user')
      return {
        ...room,
        title: isFirstQuestion ? prompt.slice(0, 52) : room.title,
        messages: [...room.messages, { sender: 'user', text: prompt }],
      }
    }))
    setLoadingRoomId(roomId)
    const controller = new AbortController()
    abortControllerRef.current = { controller, roomId }

    try {
      if (/\btren(?:d)?\b/i.test(prompt)) {
        const trendResponse = await fetch(`/api/trend-chat?question=${encodeURIComponent(prompt)}`, { signal: controller.signal })
        if (trendResponse.ok) {
          const trend = await trendResponse.json()
          if (trend.matched && (trend.historis?.length || trend.proyeksi?.length)) {
            const targetText = trend.target
              ? `Untuk ${trend.target.tahun}, model memproyeksikan nilai **${trend.target.nilai}**.`
              : 'Grafik berikut menampilkan titik historis dan proyeksi yang tersedia dari model.'
            appendMessage(roomId, {
              sender: 'assistant',
              text: `**Prediksi tren ${trend.indikator?.nama || ''}**\n${targetText}\n\nSaya tampilkan seri datanya langsung dari modul AI Trend Prediction.`,
            })
            appendMessage(roomId, { sender: 'assistant', type: 'trend-chart', trend })
            return
          }
        }
      }

      const response = await fetch('/chat', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ question: prompt }),
        signal: controller.signal,
      })

      if (!response.ok) {
        throw new Error(`Backend error ${response.status}`)
      }

      const data = await response.json()
      const answer = data.answer || 'Maaf, saya tidak mendapatkan jawaban yang valid dari server.'
      appendMessage(roomId, { sender: 'assistant', text: answer })
    } catch (err) {
      if (err.name === 'AbortError') {
        return
      }
      setError('Gagal mengambil jawaban. Pastikan backend FastAPI berjalan pada http://localhost:8000.')
      appendMessage(roomId, { sender: 'assistant', text: 'Terjadi kesalahan saat memproses permintaan Anda. Silakan coba lagi.' })
    } finally {
      if (abortControllerRef.current?.controller === controller) {
        abortControllerRef.current = null
        setLoadingRoomId(null)
      }
    }
  }

  const handleCancel = () => {
    if (abortControllerRef.current?.roomId !== activeRoomId) return
    abortControllerRef.current.controller.abort()
    abortControllerRef.current = null
    setLoadingRoomId(null)
    setError('Permintaan dibatalkan.')
  }

  const handleNewAnalysis = () => {
    if (loadingRoomId) {
      abortControllerRef.current?.controller.abort()
      abortControllerRef.current = null
      setLoadingRoomId(null)
    }
    roomSequenceRef.current += 1
    const nextRoom = createRoom(`room-${Date.now()}-${roomSequenceRef.current}`)
    setRooms((previousRooms) => [...previousRooms, nextRoom])
    setActiveRoomId(nextRoom.id)
    setInput('')
    setError('')
  }

  const handleFeatureClick = (feature) => {
    if (feature.destination) {
      onNavigate?.(feature.destination)
      return
    }
    setFeatureNotice(`${feature.label} sedang dalam tahap pengembangan.`)
  }

  return (
    <div className="min-h-screen bg-slate-100 text-slate-900">
      <div className="grid lg:grid-cols-[280px_minmax(0,1fr)] gap-6 p-6 items-start">
        <aside className="hidden lg:flex flex-col rounded-[32px] bg-white border border-slate-200 shadow-sm overflow-hidden">
          <div className="px-6 pt-6 pb-4">
            <div className="inline-flex items-center gap-3 px-3 py-2 rounded-full bg-red-50 text-red-700 font-semibold text-sm">
              <span className="material-symbols-outlined">insights</span>
              SADA-AI
            </div>
            <p className="mt-5 text-xs uppercase tracking-[0.24em] text-slate-500">Data Intelligence</p>
            <h2 className="mt-4 text-2xl font-semibold text-slate-900">Chatbot Statistik</h2>
            <p className="mt-3 text-sm text-slate-500 leading-relaxed">Tanyakan data statistik Aceh secara natural, dan saya akan menjawab berdasarkan database yang tersedia.</p>
            <button type="button" onClick={handleNewAnalysis} className="new-analysis-button mt-5 flex w-full items-center justify-center gap-2 rounded-2xl bg-red-700 px-4 py-3 text-sm font-semibold text-white">
              <span aria-hidden="true">＋</span> Analisis Baru
            </button>
          </div>
          <div className="px-6 pb-6">
            <div className="grid gap-3">
              {features.map((feature) => (
                <button
                  key={feature.label}
                  type="button"
                  onClick={() => handleFeatureClick(feature)}
                  className={`sidebar-feature group flex items-center gap-3 text-left rounded-3xl px-4 py-3 text-sm font-semibold transition ${feature.destination === 'Statistical Q&A' ? 'bg-red-700 text-white shadow-sm' : 'bg-slate-50 text-slate-700 hover:bg-slate-100'}`}
                >
                  <span className="flex h-7 w-7 items-center justify-center rounded-xl bg-white/15 text-base transition group-hover:scale-110">{feature.icon}</span>
                  <span className="flex-1">{feature.label}</span>
                  <span className="opacity-0 transition group-hover:translate-x-0.5 group-hover:opacity-100" aria-hidden="true">→</span>
                </button>
              ))}
            </div>
            {featureNotice && <p className="mt-4 rounded-2xl bg-amber-50 px-3 py-2 text-xs leading-relaxed text-amber-800">{featureNotice}</p>}
          </div>

          <div className="border-t border-slate-200 px-6 py-6">
            <h3 className="text-xs uppercase tracking-[0.24em] text-slate-500 mb-4">Riwayat Analisis</h3>
            <div className="space-y-3">
              {historyItems.map((item) => (
                <button key={item.id} type="button" disabled={Boolean(loadingRoomId)} onClick={() => { setActiveRoomId(item.id); setInput(''); setError('') }} className={`room-history w-full rounded-3xl border px-4 py-3 text-left ${item.id === activeRoomId ? 'border-red-200 bg-red-50' : 'border-slate-200 bg-slate-50'} disabled:cursor-not-allowed`}>
                  <p className="text-sm font-semibold text-slate-900 truncate">{item.title}</p>
                  <p className="text-[11px] text-slate-500 mt-1">{item.subtitle}</p>
                </button>
              ))}
            </div>
          </div>
        </aside>

        <main className="space-y-6">
          <section className="chat-command-center relative overflow-hidden rounded-[32px] p-7 shadow-xl shadow-red-950/15 md:p-9">
            <div className="command-glow" aria-hidden="true" />
            <div className="relative grid items-center gap-8 lg:grid-cols-[minmax(0,1fr)_auto]">
              <div className="max-w-2xl">
                <div className="inline-flex items-center gap-2 rounded-full border border-white/20 bg-white/10 px-3 py-2 text-[11px] font-bold uppercase tracking-[.18em] text-white/90"><span className="command-status" />SADA-AI online</div>
                <h1 className="mt-5 text-3xl font-bold leading-tight tracking-tight text-white md:text-4xl">Ruang tanya jawab data Aceh</h1>
                <p className="mt-3 text-sm leading-relaxed text-red-100 md:text-base">Ajukan pertanyaan dengan bahasa natural. SADA-AI membantu menemukan jawaban dan sumber data yang relevan dalam satu percakapan.</p>
              </div>
              <div className="command-summary">
                <div className="command-summary-icon" aria-hidden="true">
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.7"><path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3z" /><path d="M19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16z" /></svg>
                </div>
                <div><p>Mode aktif</p><strong>Statistical Q&A</strong><span>{messages.filter((message) => message.sender === 'user').length} pertanyaan dalam room ini</span></div>
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
                  Terverifikasi Satu Data Aceh
                </div>
              </div>

              <div className="mt-6 space-y-4" aria-live="polite">
                {messages.map((message, index) => (
                  <div
                    key={`${message.sender}-${index}`}
                    className={`flex ${message.sender === 'assistant' ? 'justify-start' : 'justify-end'}`}
                  >
                    {message.type === 'trend-chart' ? (
                      <div className="chat-trend-card chat-bubble rounded-[28px] p-5 shadow-sm bg-slate-50 text-slate-900">
                        <div className="mb-4 flex flex-wrap items-start justify-between gap-3">
                          <div><p className="text-xs font-bold uppercase tracking-[.16em] text-red-700">AI Trend Prediction</p><h3 className="mt-1 text-base font-bold">{message.trend.indikator?.nama}</h3><p className="mt-1 text-xs text-slate-500">Wilayah: {message.trend.wilayah}</p></div>
                          {message.trend.target && <div className="rounded-2xl bg-red-50 px-3 py-2 text-right"><p className="text-[10px] font-bold uppercase tracking-wider text-red-500">{message.trend.target.tahun}</p><p className="text-sm font-bold text-red-800">{message.trend.target.nilai}</p></div>}
                        </div>
                        <TrendPointChart historical={message.trend.historis || []} projection={message.trend.proyeksi || []} unit={message.trend.indikator?.satuan} />
                        {message.trend.ringkasan?.insight_text && (
                          <div className="chat-ai-insight mt-4 rounded-2xl p-4">
                            <div className="flex items-center gap-2 text-emerald-800"><span aria-hidden="true">✦</span><p className="text-xs font-bold uppercase tracking-[.14em]">AI Insight</p></div>
                            <p className="mt-2 text-sm leading-relaxed text-emerald-950/80">{message.trend.ringkasan.insight_text}</p>
                          </div>
                        )}
                        {message.trend.indikator?.file_sumber && (
                          <div className="mt-4 border-t border-slate-200 pt-3 text-xs text-slate-500">
                            <span className="font-semibold text-slate-700">Sumber data:</span>{' '}
                            {message.trend.indikator.file_sumber}
                          </div>
                        )}
                        <p className="mt-3 text-xs leading-relaxed text-slate-500">Garis hitam menunjukkan data historis, sedangkan garis merah putus-putus adalah proyeksi model. Hasil proyeksi merupakan estimasi, bukan data realisasi.</p>
                      </div>
                    ) : (
                      <div className={`chat-bubble rounded-[28px] p-5 shadow-sm text-sm leading-relaxed ${message.sender === 'assistant' ? 'bg-slate-50 text-slate-900' : 'bg-red-700 text-white'}`}>{renderMessageText(message.text)}</div>
                    )}
                  </div>
                ))}
                {loading && (
                  <div className="flex justify-start">
                    <div className="ai-processing rounded-[28px] p-5 shadow-sm bg-slate-50 text-slate-900" role="status" aria-label="SADA-AI sedang memproses pertanyaan">
                      <div className="processing-orbit" aria-hidden="true"><span /><span /><span /></div>
                      <div><p className="text-sm font-semibold">SADA-AI sedang memproses data</p><div className="processing-wave mt-2" aria-hidden="true"><i /><i /><i /><i /><i /></div></div>
                    </div>
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
                      disabled={Boolean(loadingRoomId)}
                      className="rounded-3xl border border-slate-200 bg-white px-4 py-3 text-left text-sm font-semibold text-slate-900 hover:border-red-700 hover:text-red-700 transition disabled:cursor-not-allowed disabled:opacity-50"
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
                <input
                  value={input}
                  onChange={(event) => setInput(event.target.value)}
                  onKeyDown={(event) => {
                    if (event.key === 'Enter' && !loadingRoomId) {
                      event.preventDefault()
                      handleSend('')
                    }
                  }}
                  disabled={Boolean(loadingRoomId)}
                  className="flex-1 rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 focus:border-red-700 focus:outline-none disabled:cursor-not-allowed disabled:opacity-60"
                  placeholder="Ketik pertanyaan statistik Anda di sini..."
                />
                <button
                  type="button"
                  onClick={loading ? handleCancel : () => handleSend('')}
                  className={`inline-flex items-center gap-2 rounded-3xl px-4 py-3 text-sm font-semibold text-white transition ${loading ? 'cancel-button bg-slate-700 hover:bg-slate-900' : 'bg-red-700 hover:bg-red-800'}`}
                >
                  <span className="material-symbols-outlined">{loading ? 'close' : 'send'}</span>
                  {loading ? 'Batalkan' : 'Kirim'}
                </button>
              </div>
              {error && <p className="mt-3 text-center text-sm text-red-600">{error}</p>}
              <p className="mt-3 text-center text-xs uppercase tracking-[0.24em] text-slate-500">SADA-AI mungkin membuat kesalahan. Verifikasi hasil melalui Dashboard Resmi Satu Data Aceh.</p>
            </div>
          </section>
        </main>
      </div>
    </div>
  )
}
