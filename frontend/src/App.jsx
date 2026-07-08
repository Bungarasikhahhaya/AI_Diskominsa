import { useEffect, useMemo, useState } from 'react'

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

const API_BASE = '/api'

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

function TrendPointChart({ historical, projection, unit }) {
  const { points, viewBox, minY, maxY } = useMemo(() => {
    const combined = [...historical.map((item) => ({ ...item, group: 'historical' })), ...projection.map((item) => ({ ...item, group: 'projection' }))]

    if (!combined.length) {
      return { points: { historical: '', projection: '' }, viewBox: '0 0 800 360', minY: 0, maxY: 1 }
    }

    const sorted = combined.sort((a, b) => a.tahun - b.tahun)
    const minValue = Math.min(...sorted.map((item) => item.nilai))
    const maxValue = Math.max(...sorted.map((item) => item.nilai))
    const minYear = Math.min(...sorted.map((item) => item.tahun))
    const maxYear = Math.max(...sorted.map((item) => item.tahun))
    const width = 800
    const height = 360
    const paddingX = 54
    const paddingY = 42
    const rangeX = Math.max(maxYear - minYear, 1)
    const rangeY = Math.max(maxValue - minValue, 1)

    const scaleX = (year) => paddingX + ((year - minYear) / rangeX) * (width - paddingX * 2)
    const scaleY = (value) => height - paddingY - ((value - minValue) / rangeY) * (height - paddingY * 2)

    const makePath = (items) =>
      items
        .sort((a, b) => a.tahun - b.tahun)
        .map((point, index) => `${index === 0 ? 'M' : 'L'} ${scaleX(point.tahun).toFixed(2)} ${scaleY(point.nilai).toFixed(2)}`)
        .join(' ')

    return {
      points: {
        historical: makePath(historical),
        projection: makePath(projection),
        combined: makePath([...historical, ...projection]),
      },
      viewBox: `0 0 ${width} ${height}`,
      minY: minValue,
      maxY: maxValue,
    }
  }, [historical, projection])

  const allPoints = [...historical, ...projection]
  if (!allPoints.length) {
    return (
      <div className="flex h-[360px] items-center justify-center rounded-[28px] border border-dashed border-slate-200 bg-slate-50 text-sm text-slate-500">
        Belum ada data untuk ditampilkan.
      </div>
    )
  }

  const years = Array.from(new Set(allPoints.map((point) => point.tahun))).sort((a, b) => a - b)
  const historicalEndYear = historical.length ? Math.max(...historical.map((point) => point.tahun)) : null

  return (
    <div className="rounded-[28px] border border-slate-200 bg-white p-4 shadow-sm">
      <div className="mb-4 flex flex-wrap items-center justify-between gap-3 px-2">
        <div>
          <p className="text-sm font-semibold text-slate-900">Historis solid, proyeksi dashed</p>
          <p className="text-xs text-slate-500">Satuan: {unit || '-'}</p>
        </div>
        <div className="flex flex-wrap gap-3 text-xs font-semibold text-slate-600">
          <span className="inline-flex items-center gap-2 rounded-full bg-slate-50 px-3 py-2">
            <span className="h-2.5 w-2.5 rounded-full bg-slate-900" />
            Historis
          </span>
          <span className="inline-flex items-center gap-2 rounded-full bg-slate-50 px-3 py-2">
            <span className="h-2.5 w-2.5 rounded-full bg-red-700" />
            Proyeksi
          </span>
        </div>
      </div>

      <div className="overflow-x-auto">
        <svg viewBox={viewBox} className="min-w-[640px] w-full" role="img" aria-label="Grafik historis dan proyeksi">
          <defs>
            <linearGradient id="historicalFill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="rgba(15, 23, 42, 0.18)" />
              <stop offset="100%" stopColor="rgba(15, 23, 42, 0)" />
            </linearGradient>
            <linearGradient id="projectionFill" x1="0" x2="0" y1="0" y2="1">
              <stop offset="0%" stopColor="rgba(185, 28, 28, 0.18)" />
              <stop offset="100%" stopColor="rgba(185, 28, 28, 0)" />
            </linearGradient>
          </defs>

          <rect x="0" y="0" width="800" height="360" rx="20" fill="#fff" />

          {[0, 1, 2, 3, 4].map((step) => {
            const y = 42 + ((360 - 84) / 4) * step
            const labelValue = maxY - ((maxY - minY) / 4) * step
            return (
              <g key={step}>
                <line x1="54" x2="746" y1={y} y2={y} stroke="#e2e8f0" strokeDasharray="4 8" />
                <text x="14" y={y + 4} className="fill-slate-400" fontSize="12">
                  {labelValue.toFixed(1)}
                </text>
              </g>
            )
          })}

          {years.map((year) => {
            const x = 54 + ((year - years[0]) / Math.max(years[years.length - 1] - years[0], 1)) * (800 - 108)
            return (
              <g key={year}>
                <line x1={x} x2={x} y1="42" y2="318" stroke="#f1f5f9" />
                <text x={x} y="342" textAnchor="middle" className="fill-slate-500" fontSize="12">
                  {year}
                </text>
              </g>
            )
          })}

          {points.combined && <path d={points.combined} fill="none" stroke="#0f172a" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />}

          {historical.length > 0 && projection.length > 0 && historicalEndYear !== null ? (
            <path
              d={points.projection}
              fill="none"
              stroke="#b91c1c"
              strokeWidth="3.5"
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeDasharray="10 8"
            />
          ) : null}

          {historical.map((point) => {
            const x = 54 + ((point.tahun - years[0]) / Math.max(years[years.length - 1] - years[0], 1)) * (800 - 108)
            const y = 318 - ((point.nilai - minY) / Math.max(maxY - minY, 1)) * 276
            return <circle key={`h-${point.tahun}`} cx={x} cy={y} r="4.5" fill="#0f172a" />
          })}

          {projection.map((point) => {
            const x = 54 + ((point.tahun - years[0]) / Math.max(years[years.length - 1] - years[0], 1)) * (800 - 108)
            const y = 318 - ((point.nilai - minY) / Math.max(maxY - minY, 1)) * 276
            return <circle key={`p-${point.tahun}`} cx={x} cy={y} r="4.5" fill="#b91c1c" />
          })}
        </svg>
      </div>
    </div>
  )
}

function TrendPredictionDashboard() {
  const [indicators, setIndicators] = useState([])
  const [indicator, setIndicator] = useState('')
  const [regions, setRegions] = useState([])
  const [regionDetails, setRegionDetails] = useState([])
  const [region, setRegion] = useState('')
  const [payload, setPayload] = useState(null)
  const [loadingIndicators, setLoadingIndicators] = useState(false)
  const [loadingSeries, setLoadingSeries] = useState(false)
  const [error, setError] = useState('')

  useEffect(() => {
    let active = true
    async function loadIndicators() {
      setLoadingIndicators(true)
      setError('')
      try {
        const response = await fetch(`${API_BASE}/indikator`)
        if (!response.ok) {
          throw new Error('Gagal memuat daftar indikator')
        }
        const data = await response.json()
        if (!active) {
          return
        }
        setIndicators(data)
        if (data.length) {
          setIndicator((current) => current || data[0].indikator)
        }
      } catch (fetchError) {
        if (active) {
          setError(fetchError.message)
        }
      } finally {
        if (active) {
          setLoadingIndicators(false)
        }
      }
    }

    loadIndicators()
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    if (!indicator) {
      return
    }

    let active = true
    async function loadRegions() {
      setLoadingSeries(true)
      setError('')
      try {
        const response = await fetch(`${API_BASE}/wilayah?indikator=${encodeURIComponent(indicator)}`)
        if (!response.ok) {
          throw new Error('Gagal memuat wilayah')
        }
        const data = await response.json()
        if (!active) {
          return
        }
        const nextRegions = data.wilayah || []
        setRegionDetails(data.wilayah_detail || [])
        setRegions(nextRegions)
        const preferredRegion = (data.wilayah_detail || []).find((item) => item.historical_count > 0) || data.wilayah_detail?.[0]
        setRegion((current) => {
          if (current && nextRegions.includes(current)) {
            return current
          }
          return preferredRegion?.wilayah || nextRegions[0] || ''
        })
      } catch (fetchError) {
        if (active) {
          setError(fetchError.message)
          setRegions([])
          setRegion('')
          setPayload(null)
        }
      } finally {
        if (active) {
          setLoadingSeries(false)
        }
      }
    }

    loadRegions()
    return () => {
      active = false
    }
  }, [indicator])

  useEffect(() => {
    if (!indicator || !region) {
      return
    }

    let active = true
    async function loadSeries() {
      setLoadingSeries(true)
      setError('')
      try {
        const response = await fetch(
          `${API_BASE}/data?indikator=${encodeURIComponent(indicator)}&wilayah=${encodeURIComponent(region)}`,
        )
        if (!response.ok) {
          throw new Error('Gagal memuat data seri')
        }
        const data = await response.json()
        if (active) {
          setPayload(data)
        }
      } catch (fetchError) {
        if (active) {
          setPayload(null)
          setError(fetchError.message)
        }
      } finally {
        if (active) {
          setLoadingSeries(false)
        }
      }
    }

    loadSeries()
    return () => {
      active = false
    }
  }, [indicator, region])

  const indicatorMeta = indicators.find((item) => item.indikator === indicator)
  const selectedRegionDetail = regionDetails.find((item) => item.wilayah === region)
  const historical = payload?.historis || []
  const projection = payload?.proyeksi || []
  const summary = payload?.ringkasan

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] border border-slate-200 bg-white p-8 shadow-sm md:p-10">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-2xl">
            <span className="mb-4 inline-flex rounded-full bg-amber-50 px-4 py-2 text-[11px] font-bold uppercase tracking-wider text-amber-700">
              Trend Prediction
            </span>
            <h2 className="text-3xl font-bold leading-tight text-slate-900 md:text-4xl">
              Prediksi tren terhubung ke API backend
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-slate-600 md:text-base">
              Pilih indikator dan wilayah untuk melihat historis solid, proyeksi dashed, dan ringkasan keandalan model dari SQLite/FastAPI.
            </p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 px-5 py-4 text-sm text-slate-600">
            <p className="font-semibold text-slate-900">Data source</p>
            <p>{indicatorMeta?.file_sumber || 'Menunggu indikator'}</p>
            <p className="mt-1 text-xs text-slate-500">
              Historis: {selectedRegionDetail?.historical_count ?? 0} | Proyeksi: {selectedRegionDetail?.projection_count ?? 0}
            </p>
          </div>
        </div>

        <div className="mt-8 grid gap-4 lg:grid-cols-2">
          <label className="space-y-2">
            <span className="text-sm font-semibold text-slate-700">Indikator</span>
            <select
              value={indicator}
              onChange={(event) => setIndicator(event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-red-300 focus:ring-4 focus:ring-red-50"
              disabled={loadingIndicators}
            >
              <option value="">Pilih indikator</option>
              {indicators.map((item) => (
                <option key={item.indikator} value={item.indikator}>
                  {item.indikator}
                </option>
              ))}
            </select>
          </label>

          <label className="space-y-2">
            <span className="text-sm font-semibold text-slate-700">Wilayah / Breakdown</span>
            <select
              value={region}
              onChange={(event) => setRegion(event.target.value)}
              className="w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-red-300 focus:ring-4 focus:ring-red-50"
              disabled={!regions.length}
            >
              <option value="">Pilih wilayah</option>
              {regions.map((item) => (
                <option key={item} value={item}>
                  {item}
                </option>
              ))}
            </select>
          </label>
        </div>

        {error ? (
          <div className="mt-6 rounded-2xl border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-800">
            {error}
          </div>
        ) : null}
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <div className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">R^2</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{summary?.r_squared ?? '-'}</p>
          <p className="mt-1 text-sm text-slate-500">Keandalan tren</p>
        </div>
        <div className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Arah tren</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{summary?.arah_tren || '-'}</p>
          <p className="mt-1 text-sm text-slate-500">Output model</p>
        </div>
        <div className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Tahun terakhir</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{summary?.tahun_terakhir ?? '-'}</p>
          <p className="mt-1 text-sm text-slate-500">Titik historis terbaru</p>
        </div>
        <div className="rounded-[28px] border border-slate-200 bg-white p-5 shadow-sm">
          <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Seri data</p>
          <p className="mt-2 text-3xl font-bold text-slate-900">{historical.length + projection.length}</p>
          <p className="mt-1 text-sm text-slate-500">Historis + proyeksi</p>
        </div>
      </section>

      <section className="grid gap-6 xl:grid-cols-[1.4fr_0.6fr]">
        <TrendPointChart historical={historical} projection={projection} unit={indicatorMeta?.satuan || payload?.indikator?.satuan} />

        <div className="space-y-4">
          <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
            <p className="text-xs font-bold uppercase tracking-wider text-slate-400">Ringkasan angka</p>
            <div className="mt-4 space-y-3 text-sm text-slate-700">
              <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-3">
                <span>Nilai terakhir</span>
                <span className="font-semibold text-slate-900">{summary?.nilai_terakhir ?? '-'}</span>
              </div>
              <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-3">
                <span>Slope per tahun</span>
                <span className="font-semibold text-slate-900">{summary?.slope_per_tahun ?? '-'}</span>
              </div>
              <div className="flex items-center justify-between gap-4 border-b border-slate-100 pb-3">
                <span>Historis</span>
                <span className="font-semibold text-slate-900">{historical.length} titik</span>
              </div>
              <div className="flex items-center justify-between gap-4">
                <span>Proyeksi</span>
                <span className="font-semibold text-slate-900">{projection.length} titik</span>
              </div>
            </div>
          </div>

          <div className="rounded-[28px] border border-dashed border-red-200 bg-red-50/60 p-6">
            <p className="text-sm font-semibold text-red-800">Catatan model</p>
            <p className="mt-2 text-sm leading-relaxed text-red-900/80">
              {summary?.catatan || 'Model baseline memakai regresi linear sederhana dari data yang tersedia.'}
            </p>
          </div>
        </div>
      </section>

      <section className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900">Historis</h3>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="text-xs uppercase tracking-wider text-slate-400">
                <tr>
                  <th className="py-2 pr-4">Tahun</th>
                  <th className="py-2 pr-4">Nilai</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loadingSeries && !historical.length ? (
                  <tr>
                    <td className="py-3 text-slate-500" colSpan="2">
                      Memuat data...
                    </td>
                  </tr>
                ) : (
                  historical.map((item) => (
                    <tr key={`historical-${item.tahun}`}>
                      <td className="py-3 pr-4 text-slate-600">{item.tahun}</td>
                      <td className="py-3 pr-4 font-semibold text-slate-900">{item.nilai}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>

        <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-bold text-slate-900">Proyeksi</h3>
          <div className="mt-4 overflow-x-auto">
            <table className="min-w-full text-left text-sm">
              <thead className="text-xs uppercase tracking-wider text-slate-400">
                <tr>
                  <th className="py-2 pr-4">Tahun</th>
                  <th className="py-2 pr-4">Nilai</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-100">
                {loadingSeries && !projection.length ? (
                  <tr>
                    <td className="py-3 text-slate-500" colSpan="2">
                      Memuat data...
                    </td>
                  </tr>
                ) : (
                  projection.map((item) => (
                    <tr key={`projection-${item.tahun}`}>
                      <td className="py-3 pr-4 text-slate-600">{item.tahun}</td>
                      <td className="py-3 pr-4 font-semibold text-red-700">{item.nilai}</td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </section>
    </div>
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
        {activeView === 'trend' ? (
          <TrendPredictionDashboard />
        ) : (
          <HomeView onOpenTrend={() => setActiveView('trend')} />
        )}
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
