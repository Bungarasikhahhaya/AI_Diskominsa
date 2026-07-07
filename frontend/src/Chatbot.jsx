const historyItems = [
  { title: 'Inflasi Nasional Januari 2024', subtitle: '2 jam yang lalu' },
  { title: 'Tren Ekspor Batubara Q4', subtitle: 'Kemarin' },
  { title: 'Sensus Penduduk Digital', subtitle: '3 hari yang lalu' },
  { title: 'Produksi Beras vs Konsumsi', subtitle: '1 minggu yang lalu' },
]

const features = [
  { label: 'Statistical Q&A', active: true },
  { label: 'Report Summarizer' },
  { label: 'Trend Prediction' },
  { label: 'Anomaly Analysis' },
]

export default function ChatbotPage() {
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
            <p className="mt-3 text-sm text-slate-500 leading-relaxed">Gunakan pertanyaan natural untuk mendapatkan insight data dari BPS dengan cepat.</p>
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
                <p className="text-sm uppercase tracking-[0.24em] text-slate-500">Riwayat Analisis</p>
                <h1 className="mt-3 text-3xl font-semibold text-slate-900">Analisis Statistik Terkini</h1>
                <p className="mt-3 max-w-2xl text-sm text-slate-500">Gunakan chatbot untuk mencari insight, menganalisis tren, dan ringkas laporan data instan.</p>
              </div>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                <div className="rounded-3xl bg-slate-50 p-5">
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Pertanyaan populer</p>
                  <p className="mt-3 font-semibold text-slate-900">Berapa angka inflasi bulan lalu?</p>
                </div>
                <div className="rounded-3xl bg-red-700 p-5 text-white">
                  <p className="text-xs uppercase tracking-[0.24em] text-red-200">Jawaban singkat</p>
                  <p className="mt-3 text-lg font-semibold">Inflasi YoY tercatat 2,57%.</p>
                </div>
              </div>
            </div>
          </section>

          <section className="grid gap-6 xl:grid-cols-[1.2fr_0.8fr]">
            <div className="rounded-[32px] bg-white border border-slate-200 p-6 shadow-sm">
              <div className="flex items-center justify-between gap-4 pb-4 border-b border-slate-200">
                <div>
                  <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Chatbot</p>
                  <h2 className="mt-2 text-xl font-semibold text-slate-900">Tanyakan data statistik apapun</h2>
                </div>
                <div className="inline-flex items-center gap-2 rounded-full bg-slate-100 px-3 py-2 text-sm text-slate-700">
                  <span className="material-symbols-outlined">shield</span>
                  Terverifikasi BPS
                </div>
              </div>

              <div className="mt-6 space-y-4">
                <div className="rounded-[28px] bg-slate-50 p-5">
                  <p className="text-sm text-slate-700">Selamat datang kembali, <strong>Budi</strong>. Saya siap membantu Anda menganalisis data statistik nasional terbaru.</p>
                </div>
                <div className="rounded-[28px] bg-red-700 p-5 text-white">
                  <p className="text-sm">Berdasarkan rilis BPS terbaru, inflasi YoY pada bulan lalu tercatat sebesar <strong>2,57%</strong>. Ini masih berada dalam rentang target pemerintah.</p>
                </div>
              </div>

              <div className="mt-8 rounded-[32px] border border-slate-200 bg-slate-50 p-5">
                <div className="grid gap-4 sm:grid-cols-3">
                  {['Berapa angka inflasi bulan lalu?', 'Tampilkan tren kemiskinan 2023', 'Analisis Gini Ratio per provinsi'].map((item) => (
                    <button key={item} className="rounded-3xl border border-slate-200 bg-white px-4 py-3 text-left text-sm font-semibold text-slate-900 hover:border-red-700 hover:text-red-700 transition">
                      {item}
                    </button>
                  ))}
                </div>
              </div>
            </div>

            <aside className="space-y-6">
              <div className="rounded-[32px] bg-white border border-slate-200 p-6 shadow-sm">
                <div className="flex items-center justify-between gap-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Ringkasan</p>
                    <h3 className="mt-2 text-lg font-semibold text-slate-900">Ringkasan Jawaban</h3>
                  </div>
                  <span className="material-symbols-outlined text-red-700">query_stats</span>
                </div>
                <p className="mt-4 text-sm text-slate-600">Teknologi AI memberikan jawaban cepat dengan sumber data BPS, sehingga Anda bisa langsung melanjutkan analisis kebijakan.</p>
              </div>

              <div className="rounded-[32px] bg-white border border-slate-200 p-6 shadow-sm">
                <div className="flex items-center justify-between gap-3 pb-4 border-b border-slate-200">
                  <div>
                    <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Grafik ringkas</p>
                    <h3 className="mt-2 text-lg font-semibold text-slate-900">Inflasi YoY</h3>
                  </div>
                  <span className="text-sm text-slate-500">Des</span>
                </div>
                <div className="mt-5 grid grid-cols-5 gap-2 h-32 items-end">
                  {[
                    { label: 'Agt', height: 'h-16' },
                    { label: 'Sep', height: 'h-12' },
                    { label: 'Okt', height: 'h-20' },
                    { label: 'Nov', height: 'h-24' },
                    { label: 'Des', height: 'h-28', primary: true },
                  ].map((item) => (
                    <div key={item.label} className="flex flex-col items-center gap-2">
                      <div className={`w-full rounded-t-3xl ${item.primary ? 'bg-red-700' : 'bg-slate-300'} ${item.height}`} />
                      <span className="text-[11px] text-slate-500">{item.label}</span>
                    </div>
                  ))}
                </div>
              </div>
            </aside>
          </section>

          <section className="rounded-[32px] bg-white border border-slate-200 p-6 shadow-sm">
            <div className="max-w-4xl mx-auto">
              <div className="relative flex items-center gap-3 rounded-[28px] border border-slate-200 bg-slate-50 p-4 shadow-sm">
                <button className="rounded-3xl bg-white px-4 py-3 text-sm font-semibold text-slate-700 hover:bg-slate-100 transition">Upload File</button>
                <input className="flex-1 rounded-3xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-700 focus:border-red-700 focus:outline-none" placeholder="Ketik pertanyaan statistik Anda di sini..." />
                <button className="inline-flex items-center gap-2 rounded-3xl bg-red-700 px-4 py-3 text-sm font-semibold text-white hover:bg-red-800 transition">
                  <span className="material-symbols-outlined">send</span>
                  Send
                </button>
              </div>
              <p className="mt-3 text-center text-xs uppercase tracking-[0.24em] text-slate-500">SADA-AI mungkin membuat kesalahan. Verifikasi hasil melalui Dashboard Resmi BPS.</p>
            </div>
          </section>
        </main>
      </div>
    </div>
  )
}
