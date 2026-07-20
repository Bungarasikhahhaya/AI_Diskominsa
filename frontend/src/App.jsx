import { useState } from 'react'
import ChatbotPage from './Chatbot'
import { TrendPredictionDashboard } from './TrendPrediction'

const features = [
  {
    title: 'Statistical Q&A',
    description: 'Konsultasi data statistik instan dengan pemrosesan bahasa alami untuk query data kompleks secara akurat.',
  },
  {
    title: 'AI Narasi Laporan Otomatis',
    description: 'Ubah dokumen laporan pemerintah yang panjang menjadi ringkasan poin-poin eksekutif yang mudah dipahami.',
  },
  {
    title: 'AI Prediksi Tren Data',
    description: 'Analisis prediktif menggunakan algoritma Machine Learning untuk memproyeksikan indikator ekonomi dan sosial.',
  },
  {
    title: 'AI Analisis Anomali',
    description: 'Deteksi otomatis penyimpangan data dan insight mendalam untuk memitigasi kesalahan pelaporan statistik.',
  },
]

export default function App() {
  const [page, setPage] = useState('home')

  const openFeature = (title) => {
    if (title === 'Statistical Q&A') setPage('chat')
    if (title === 'AI Prediksi Tren Data') setPage('trend')
  }

  return (
    <div className="min-h-screen bg-gray-50 text-slate-900 flex flex-col">
      {page === 'home' ? (
        <main className="max-w-6xl mx-auto px-4 py-12 space-y-10 flex-grow">
          <section className="bg-white border border-gray-200 rounded-[32px] p-8 md:p-14 shadow-sm">
            <div className="max-w-3xl">
              <span className="inline-flex px-4 py-2 bg-red-50 text-red-700 text-[11px] font-bold tracking-wider uppercase rounded-full mb-5">
                Portal Resmi Statistika Indonesia
              </span>
              <h1 className="text-4xl md:text-5xl font-bold text-slate-900 mb-5 leading-tight">
                Selamat Datang di Portal SADA-AI
              </h1>
              <p className="text-gray-600 text-sm md:text-base leading-relaxed mb-8">
                Integrasi kecerdasan buatan untuk tata kelola data nasional yang lebih transparan, cepat, dan akurat. Akses insight statistik secara real-time melalui platform analisis tercanggih untuk mendukung pengambilan kebijakan publik.
              </p>
              <button
                className="bg-red-700 text-white px-6 py-4 rounded-full inline-flex items-center gap-3 hover:bg-red-800 transition-colors text-base font-semibold"
                onClick={() => setPage('chat')}
              >
                <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                  <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
                </svg>
                Statistical Q&A
              </button>
            </div>
          </section>

          <section className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
            {features.map((feature) => (
              <div key={feature.title} className="bg-white border border-gray-200 rounded-[28px] p-6 flex flex-col h-full shadow-sm">
                <div className="w-12 h-12 bg-red-50 text-red-700 rounded-2xl flex items-center justify-center mb-4">
                  <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                    <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
                  </svg>
                </div>
                <h3 className="font-bold text-gray-900 mb-2 text-lg">{feature.title}</h3>
                <p className="text-sm text-gray-500 mb-6 leading-relaxed flex-grow">{feature.description}</p>
                <button
                  className="inline-flex items-center justify-center text-sm font-semibold border border-gray-200 rounded-full px-4 py-2 text-slate-700 hover:bg-gray-100 transition-colors"
                  onClick={() => openFeature(feature.title)}
                >
                  Buka Fitur
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
          <ChatbotPage />
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
