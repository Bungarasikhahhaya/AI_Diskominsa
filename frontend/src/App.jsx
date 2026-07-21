import { useState } from 'react'
import ChatbotPage from './Chatbot'
import { TrendPredictionDashboard } from './TrendPrediction'

const features = [
  {
    title: 'Statistical Q&A',
    description: 'Konsultasi data statistik instan dengan pemrosesan bahasa alami untuk query data kompleks secara akurat.',
    icon: 'chat',
  },
  {
    title: 'AI Narasi Laporan Otomatis',
    description: 'Ubah dokumen laporan pemerintah yang panjang menjadi ringkasan poin-poin eksekutif yang mudah dipahami.',
    icon: 'document',
  },
  {
    title: 'AI Prediksi Tren Data',
    description: 'Analisis prediktif menggunakan algoritma Machine Learning untuk memproyeksikan indikator ekonomi dan sosial.',
    icon: 'trend',
  },
  {
    title: 'AI Analisis Anomali',
    description: 'Deteksi otomatis penyimpangan data dan insight mendalam untuk memitigasi kesalahan pelaporan statistik.',
    icon: 'spark',
  },
]

function FeatureIcon({ type }) {
  const paths = {
    chat: <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />,
    document: <path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8l-6-6zM14 2v6h6M8 13h8M8 17h5" />,
    trend: <path d="M3 17l6-6 4 4 8-9M15 6h6v6M3 21h18" />,
    spark: <path d="M12 3l1.8 5.2L19 10l-5.2 1.8L12 17l-1.8-5.2L5 10l5.2-1.8L12 3zM19 16l.8 2.2L22 19l-2.2.8L19 22l-.8-2.2L16 19l2.2-.8L19 16z" />,
  }
  return <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2">{paths[type]}</svg>
}

export default function App() {
  const [page, setPage] = useState('home')

  const openFeature = (title) => {
    if (title === 'Statistical Q&A') setPage('chat')
    if (title === 'AI Prediksi Tren Data') setPage('trend')
  }

  return (
    <div className="min-h-screen bg-gray-50 text-slate-900 flex flex-col">
      {page === 'home' ? (
        <main className="max-w-6xl mx-auto px-4 py-8 md:py-12 space-y-10 flex-grow">
          <section className="hero-panel relative overflow-hidden bg-white border border-white/80 rounded-[32px] p-8 md:p-14 shadow-xl shadow-slate-200/50">
            <div className="hero-orb hero-orb-one" aria-hidden="true" />
            <div className="hero-orb hero-orb-two" aria-hidden="true" />
            <div className="relative grid lg:grid-cols-[1.25fr_.75fr] gap-10 items-center">
              <div className="max-w-3xl animate-enter">
              <span className="inline-flex px-4 py-2 bg-red-50 text-red-700 text-[11px] font-bold tracking-wider uppercase rounded-full mb-5 ring-1 ring-red-100">
                Platform Analitik Satu Data Aceh
              </span>
              <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-5 leading-[1.12] tracking-tight">
                Selamat Datang di Portal SADA-AI
              </h1>
              <p className="text-gray-600 text-sm md:text-base leading-relaxed mb-8">
                Integrasi kecerdasan buatan untuk tata kelola data nasional yang lebih transparan, cepat, dan akurat. Akses insight statistik secara real-time melalui platform analisis tercanggih untuk mendukung pengambilan kebijakan publik.
              </p>
              <a
                className="hero-cta bg-red-700 text-white px-6 py-4 rounded-full inline-flex items-center gap-3 text-base font-semibold"
                href="https://satudata.acehprov.go.id"
                target="_blank"
                rel="noopener noreferrer"
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
                  <path d="M14 3h7v7M10 14L21 3M21 14v5a2 2 0 01-2 2H5a2 2 0 01-2-2V5a2 2 0 012-2h5" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.5" />
                </svg>
                Kunjungi Portal Satu Data Aceh
              </a>
              </div>
              <div className="relative hidden lg:block animate-enter-delayed" aria-hidden="true">
                <div className="data-card p-6 rounded-[26px] bg-white/90 border border-white shadow-2xl shadow-red-950/10">
                  <div className="flex items-center justify-between mb-7"><div><p className="text-xs text-slate-500 font-medium">Indeks Kepercayaan Data</p><p className="text-3xl font-bold text-slate-900 mt-1">98.4<span className="text-base text-red-700">%</span></p></div><div className="pulse-dot"><span /></div></div>
                  <div className="flex items-end gap-2 h-24">{[36, 51, 44, 68, 57, 83, 75, 96].map((height, index) => <span key={index} className="data-bar" style={{ height: `${height}%`, animationDelay: `${index * 85}ms` }} />)}</div>
                  <div className="flex justify-between mt-3 text-[10px] text-slate-400"><span>Januari</span><span>Desember</span></div>
                </div>
                <div className="absolute -bottom-6 -left-7 bg-red-700 text-white rounded-2xl px-5 py-4 shadow-xl shadow-red-900/20 float-slow"><p className="text-[10px] uppercase tracking-widest opacity-75">Insight tersedia</p><p className="font-bold text-xl">24/7</p></div>
              </div>
            </div>
          </section>

          <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            {features.map((feature, index) => (
              <div key={feature.title} className="feature-card bg-white border border-gray-200 rounded-[28px] p-6 flex flex-col h-full shadow-sm animate-card" style={{ animationDelay: `${index * 90}ms` }}>
                <div className="feature-icon w-12 h-12 bg-red-50 text-red-700 rounded-2xl flex items-center justify-center mb-4">
                  <FeatureIcon type={feature.icon} />
                </div>
                <h3 className="font-bold text-gray-900 mb-2 text-lg">{feature.title}</h3>
                <p className="text-sm text-gray-500 mb-6 leading-relaxed flex-grow">{feature.description}</p>
                <button
                  className="feature-link inline-flex items-center justify-center gap-2 text-sm font-semibold border border-gray-200 rounded-full px-4 py-2 text-slate-700"
                  onClick={() => openFeature(feature.title)}
                >
                  Buka Fitur <span aria-hidden="true">→</span>
                </button>
              </div>
            ))}
          </section>
        </main>
      ) : page === 'chat' ? (
        <div className="flex-grow">
          <header className="p-4 mb-4 max-w-6xl mx-auto">
            <button onClick={() => setPage('home')} className="text-slate-600 hover:text-slate-900 font-semibold text-sm">
              &larr; Kembali ke Beranda
            </button>
          </header>
          <ChatbotPage onNavigate={openFeature} />
        </div>
      ) : (
        <div className="flex-grow">
          <header className="p-4 mb-4 max-w-6xl mx-auto">
            <button onClick={() => setPage('home')} className="text-slate-600 hover:text-slate-900 font-semibold text-sm">
              &larr; Kembali ke Beranda
            </button>
          </header>
          <main className="max-w-6xl mx-auto px-4 pb-12">
            <TrendPredictionDashboard />
          </main>
        </div>
      )}

      <footer className="py-6 border-t border-gray-200 mt-auto">
        <div className="max-w-6xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center text-[11px] text-gray-500 gap-2">
          <div><span className="font-bold text-gray-700">SADA-AI</span><span className="mx-2">© 2024 Badan Pusat Statistik. Seluruh Hak Cipta Dilindungi.</span></div>
        </div>
      </footer>
    </div>
  )
}
