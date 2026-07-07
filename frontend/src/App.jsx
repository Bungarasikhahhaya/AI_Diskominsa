import { useState } from 'react'

const features = [
  {
    title: 'AI Chatbot Tanya-Jawab',
    description: 'Konsultasi data statistik instan dengan pemrosesan bahasa alami untuk query data kompleks secara akurat.',
  },
  {
    title: 'AI Peringkas Laporan',
    description: 'Ubah dokumen laporan pemerintah yang panjang menjadi ringkasan poin-poin eksekutif yang mudah dipahami.',
  },
  {
    title: 'AI Prediksi Tren Data',
    description: 'Analisis prediktif menggunakan regresi linear baseline untuk memproyeksikan indikator ekonomi dan sosial.',
  },
  {
    title: 'AI Analisis Anomali',
    description: 'Deteksi otomatis penyimpangan data dan insight mendalam untuk memitigasi kesalahan pelaporan statistik.',
  },
]

const trendWorkflow = [
  {
    title: 'Baca dataset bersih',
    description: 'Script memproses seluruh CSV dari folder dataset_bersih sebagai sumber proyeksi.',
  },
  {
    title: 'Agregasi tahunan',
    description: 'Data sub-tahunan seperti bulan atau kuartal digabung dulu ke level tahun sebelum model dijalankan.',
  },
  {
    title: 'Fit regresi linear',
    description: 'Setiap indikator difit dengan polyfit derajat 1 untuk mendapatkan slope, arah tren, dan R^2.',
  },
  {
    title: 'Simpan hasil proyeksi',
    description: 'Output disusun ke CSV ringkas agar bisa dipakai ulang di dashboard atau pelaporan.',
  },
]

const trendOutputs = [
  'file_sumber',
  'indikator',
  'level_wilayah',
  'satuan',
  'jumlah_titik_tahun',
  'tahun_terakhir',
  'nilai_terakhir',
  'slope_per_tahun',
  'r_squared',
  'arah_tren',
]

function HeaderButton({ active, children, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`rounded-full px-4 py-2 text-sm font-semibold transition-all ${
        active ? 'bg-red-700 text-white shadow-sm' : 'text-slate-600 hover:bg-slate-100 hover:text-slate-900'
      }`}
    >
      {children}
    </button>
  )
}

function FeatureCard({ feature, onOpenTrend }) {
  const isTrendFeature = feature.title === 'AI Prediksi Tren Data'

  return (
    <div className="group flex h-full flex-col rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm transition-transform duration-200 hover:-translate-y-1 hover:shadow-lg">
      <div className="mb-4 flex h-12 w-12 items-center justify-center rounded-2xl bg-red-50 text-red-700">
        <svg className="h-6 w-6" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
          <path d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />
        </svg>
      </div>
      <h3 className="mb-2 text-lg font-bold text-slate-900">{feature.title}</h3>
      <p className="mb-6 flex-grow text-sm leading-relaxed text-slate-500">{feature.description}</p>
      <button
        type="button"
        onClick={isTrendFeature ? onOpenTrend : undefined}
        className={`inline-flex items-center justify-center rounded-full border px-4 py-2 text-sm font-semibold transition-colors ${
          isTrendFeature
            ? 'border-red-700 bg-red-700 text-white hover:bg-red-800'
            : 'border-slate-200 text-slate-700 hover:border-slate-300 hover:bg-slate-50'
        }`}
      >
        {isTrendFeature ? 'Buka Trend Prediction' : 'Buka Fitur'}
      </button>
    </div>
  )
}

function HomeView({ onOpenTrend }) {
  return (
    <div className="space-y-10">
      <section className="overflow-hidden rounded-[32px] border border-slate-200 bg-white p-8 shadow-sm md:p-14">
        <div className="max-w-3xl">
          <span className="mb-5 inline-flex rounded-full bg-red-50 px-4 py-2 text-[11px] font-bold uppercase tracking-wider text-red-700">
            Portal Resmi Statistika Indonesia
          </span>
          <h1 className="mb-5 text-4xl font-bold leading-tight text-slate-900 md:text-5xl">
            Selamat Datang di Portal SADA-AI
          </h1>
          <p className="mb-8 text-sm leading-relaxed text-slate-600 md:text-base">
            Integrasi kecerdasan buatan untuk tata kelola data nasional yang lebih transparan, cepat, dan akurat. Akses insight statistik secara real-time melalui platform analisis tercanggih untuk mendukung pengambilan kebijakan publik.
          </p>
          <div className="flex flex-wrap gap-3">
            <button type="button" className="inline-flex items-center gap-3 rounded-full bg-red-700 px-6 py-4 text-base font-semibold text-white transition-colors hover:bg-red-800">
              <svg className="h-5 w-5" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path d="M5 13l4 4L19 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" />
              </svg>
              Jelajahi Data Nasional
            </button>
            <button
              type="button"
              onClick={onOpenTrend}
              className="inline-flex items-center gap-3 rounded-full border border-slate-200 px-6 py-4 text-base font-semibold text-slate-700 transition-colors hover:border-red-200 hover:bg-red-50 hover:text-red-700"
            >
              Trend Prediction
            </button>
          </div>
        </div>
      </section>

      <section className="grid grid-cols-1 gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {features.map((feature) => (
          <FeatureCard key={feature.title} feature={feature} onOpenTrend={onOpenTrend} />
        ))}
      </section>
    </div>
  )
}

function TrendPredictionView({ onBack }) {
  return (
    <div className="space-y-8">
      <section className="grid gap-6 lg:grid-cols-[1.2fr_0.8fr]">
        <div className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-sm md:p-10">
          <span className="mb-5 inline-flex rounded-full bg-amber-50 px-4 py-2 text-[11px] font-bold uppercase tracking-wider text-amber-700">
            Trend Prediction
          </span>
          <h2 className="mb-4 text-3xl font-bold leading-tight text-slate-900 md:text-4xl">
            Prediksi Tren untuk indikator statistik Aceh
          </h2>
          <p className="max-w-2xl text-sm leading-relaxed text-slate-600 md:text-base">
            Halaman ini menautkan fitur AI prediksi tren yang sebelumnya berada di folder terpisah ke dalam SADA-AI. Pipeline Python yang sudah ada membaca dataset bersih, mengagregasi data tahunan, lalu menghasilkan proyeksi 1 sampai 3 tahun ke depan sebagai baseline yang mudah dijelaskan.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <button type="button" onClick={onBack} className="rounded-full bg-red-700 px-5 py-3 text-sm font-semibold text-white transition-colors hover:bg-red-800">
              Kembali ke Beranda
            </button>
            <div className="rounded-full border border-slate-200 bg-slate-50 px-5 py-3 text-sm font-semibold text-slate-700">
              Proyeksi 3 tahun ke depan
            </div>
          </div>
        </div>

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-1">
          {[
            ['Input utama', 'CSV tidy dengan kolom tahun dan nilai'],
            ['Model baseline', 'Regresi linear sederhana'],
            ['Validasi tren', 'R^2 untuk menilai kestabilan pola'],
            ['Output', 'CSV proyeksi per indikator dan wilayah'],
          ].map(([label, value]) => (
            <div key={label} className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
              <p className="text-xs font-bold uppercase tracking-wider text-slate-400">{label}</p>
              <p className="mt-2 text-lg font-semibold text-slate-900">{value}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-sm">
          <h3 className="text-xl font-bold text-slate-900">Alur pemrosesan</h3>
          <div className="mt-6 space-y-4">
            {trendWorkflow.map((step, index) => (
              <div key={step.title} className="flex gap-4 rounded-3xl border border-slate-100 bg-slate-50 p-4">
                <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-red-700 text-sm font-bold text-white">
                  {index + 1}
                </div>
                <div>
                  <h4 className="font-semibold text-slate-900">{step.title}</h4>
                  <p className="mt-1 text-sm leading-relaxed text-slate-600">{step.description}</p>
                </div>
              </div>
            ))}
          </div>
        </div>

        <div className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-sm">
          <h3 className="text-xl font-bold text-slate-900">Struktur output</h3>
          <p className="mt-3 text-sm leading-relaxed text-slate-600">
            Script Python menyimpan hasil ke hasil_proyeksi/proyeksi_semua_indikator.csv, dengan catatan tambahan jika tren historis terlalu fluktuatif.
          </p>
          <div className="mt-6 flex flex-wrap gap-2">
            {trendOutputs.map((field) => (
              <span key={field} className="rounded-full border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-semibold text-slate-600">
                {field}
              </span>
            ))}
          </div>

          <div className="mt-8 rounded-[28px] border border-dashed border-red-200 bg-red-50/60 p-5">
            <p className="text-sm font-semibold text-red-800">Catatan implementasi</p>
            <p className="mt-2 text-sm leading-relaxed text-red-900/80">
              UI ini sekarang sudah terhubung ke navigasi Trend Prediction di SADA-AI. Jika nanti endpoint Python atau Streamlit dihubungkan, panel ini bisa langsung dijadikan pintu masuk ke model yang sama tanpa mengubah struktur halaman utama.
            </p>
          </div>
        </div>
      </section>
    </div>
  )
}

export default function App() {
  const [activeView, setActiveView] = useState('home')

  return (
    <div className="min-h-screen text-slate-900">
      <header className="sticky top-0 z-20 border-b border-white/60 bg-white/85 backdrop-blur">
        <div className="mx-auto flex max-w-6xl flex-wrap items-center justify-between gap-4 px-4 py-4">
          <div>
            <span className="text-sm font-semibold uppercase tracking-[0.24em] text-red-700">SADA-AI</span>
          </div>
          <nav className="flex flex-wrap gap-2">
            <HeaderButton active={activeView === 'home'} onClick={() => setActiveView('home')}>
              Home
            </HeaderButton>
            <HeaderButton active={activeView === 'trend'} onClick={() => setActiveView('trend')}>
              Trend Prediction
            </HeaderButton>
          </nav>
        </div>
      </header>

      <main className="mx-auto max-w-6xl px-4 py-12">
        {activeView === 'trend' ? <TrendPredictionView onBack={() => setActiveView('home')} /> : <HomeView onOpenTrend={() => setActiveView('trend')} />}
      </main>

      <footer className="border-t border-slate-200 py-6">
        <div className="mx-auto flex max-w-6xl flex-col items-center justify-between gap-2 px-4 text-[11px] text-slate-500 md:flex-row">
          <div>
            <span className="font-bold text-slate-700">SADA-AI</span>
            <span className="mx-2">© 2024 Badan Pusat Statistik. Seluruh Hak Cipta Dilindungi.</span>
          </div>
        </div>
      </footer>
    </div>
  )
}
