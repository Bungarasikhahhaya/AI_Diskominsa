import { useEffect, useMemo, useState, useRef } from 'react'

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
          <p className="text-sm font-semibold text-slate-900">Historis hitam, proyeksi merah</p>
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

          {years.map((year, index) => {
            const x = 54 + ((year - years[0]) / Math.max(years[years.length - 1] - years[0], 1)) * (800 - 108)
            const step = Math.ceil(years.length / 12)
            const showLabel = years.length <= 12 || index % step === 0 || index === years.length - 1

            // Hindari tumpang tindih antara label terakhir dan label sebelumnya
            const isOverlappingLast = index === years.length - 1 ? false : (years.length - 1 - index) < step * 0.7 && (index % step === 0)

            return (
              <g key={year}>
                <line x1={x} x2={x} y1="42" y2="318" stroke="#f1f5f9" />
                {showLabel && !isOverlappingLast && (
                  <text x={x} y="342" textAnchor="middle" className="fill-slate-500" fontSize="12">
                    {year}
                  </text>
                )}
              </g>
            )
          })}

          {points.historical && <path d={points.historical} fill="none" stroke="#0f172a" strokeWidth="3.5" strokeLinecap="round" strokeLinejoin="round" />}

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

function HistoricalDetailTable({ rows }) {
  if (!rows.length) {
    return null
  }

  const parsedRows = rows.flatMap((row) => {
    if (!row.detail_json) {
      return [{ tahun: row.tahun, nilai: row.nilai, detail: '-' }]
    }

    try {
      const detail = JSON.parse(row.detail_json)
      const detailText = Object.entries(detail).map(([key, value]) => `${key}=${value}`).join(' | ')
      return [{ tahun: row.tahun, nilai: row.nilai, detail: detailText || '-' }]
    } catch {
      return [{ tahun: row.tahun, nilai: row.nilai, detail: '-' }]
    }
  })

  return (
    <div className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
      <h3 className="text-lg font-bold text-slate-900">Detail historis tambahan</h3>
      <p className="mt-2 text-sm text-slate-600">
        Detail ini menyimpan breakdown seperti bulan/triwulan tanpa dipakai sebagai join key utama.
      </p>
      <div className="mt-4 overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-xs uppercase tracking-wider text-slate-400">
            <tr>
              <th className="py-2 pr-4">Tahun</th>
              <th className="py-2 pr-4">Nilai</th>
              <th className="py-2 pr-4">Detail</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100">
            {parsedRows.slice(0, 8).map((row) => (
              <tr key={`${row.tahun}-${row.detail}`}>
                <td className="py-3 pr-4 text-slate-600">{row.tahun}</td>
                <td className="py-3 pr-4 font-semibold text-slate-900">{row.nilai}</td>
                <td className="py-3 pr-4 text-slate-600">{row.detail}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

function SearchableSelect({ options, value, onChange, disabled, placeholder }) {
  const [isOpen, setIsOpen] = useState(false)
  const [search, setSearch] = useState('')
  const wrapperRef = useRef(null)

  useEffect(() => {
    function handleClickOutside(event) {
      if (wrapperRef.current && !wrapperRef.current.contains(event.target)) {
        setIsOpen(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const filteredOptions = options.filter((opt) =>
    opt.label.toLowerCase().includes(search.toLowerCase())
  )

  const selectedOption = options.find((opt) => opt.value === value)

  return (
    <div ref={wrapperRef} className="relative w-full">
      <div
        className={`w-full rounded-2xl border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition flex justify-between items-center cursor-pointer ${disabled ? 'opacity-50 cursor-not-allowed' : 'focus-within:border-red-300 focus-within:ring-4 focus-within:ring-red-50'}`}
        onClick={() => !disabled && setIsOpen(!isOpen)}
      >
        <span className="truncate">{selectedOption ? selectedOption.label : placeholder}</span>
        <svg className="h-4 w-4 text-slate-400 shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M19 9l-7 7-7-7" />
        </svg>
      </div>

      {isOpen && (
        <div className="absolute z-10 w-full mt-2 bg-white border border-slate-200 rounded-2xl shadow-lg max-h-72 flex flex-col">
          <div className="sticky top-0 bg-white p-2 border-b border-slate-100 rounded-t-2xl z-20">
            <input
              type="text"
              className="w-full px-3 py-2 text-sm bg-slate-50 border border-slate-200 rounded-xl outline-none focus:border-red-300 focus:ring-2 focus:ring-red-50"
              placeholder="Cari..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              onClick={(e) => e.stopPropagation()}
              autoFocus
            />
          </div>
          <div className="p-1 overflow-y-auto">
            {filteredOptions.length > 0 ? (
              filteredOptions.map((opt) => (
                <div
                  key={opt.value}
                  className={`px-3 py-2 text-sm rounded-xl cursor-pointer hover:bg-red-50 hover:text-red-700 ${value === opt.value ? 'bg-red-50 text-red-700 font-medium' : 'text-slate-700'}`}
                  onClick={() => {
                    onChange(opt.value)
                    setIsOpen(false)
                    setSearch('')
                  }}
                >
                  {opt.label}
                </div>
              ))
            ) : (
              <div className="px-3 py-4 text-sm text-center text-slate-500">Tidak ditemukan</div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}

export function TrendPredictionDashboard() {
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
  const historicalDetail = payload?.historis_detail || []
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
              Eksplorasi Prediksi Tren Data
            </h2>
            <p className="mt-3 text-sm leading-relaxed text-slate-600 md:text-base">
              Pilih indikator dan wilayah untuk melihat pergerakan data historis beserta proyeksi tren masa depan dengan mudah.
            </p>
          </div>
          <div className="rounded-3xl border border-slate-200 bg-slate-50 px-5 py-4 text-sm text-slate-600">
            <p className="font-semibold text-slate-900">Data source</p>
            <p className="break-all">{indicatorMeta?.file_sumber || 'Menunggu indikator'}</p>
            <p className="mt-1 text-xs text-slate-500">
              Historis: {selectedRegionDetail?.historical_count ?? 0} | Proyeksi: {selectedRegionDetail?.projection_count ?? 0}
            </p>
          </div>
        </div>

        <div className="mt-8 grid gap-4 lg:grid-cols-2">
          <label className="space-y-2">
            <span className="text-sm font-semibold text-slate-700">Indikator</span>
            <SearchableSelect
              options={indicators.map((item) => ({ value: item.indikator, label: item.indikator.replace(/_/g, ' ') }))}
              value={indicator}
              onChange={setIndicator}
              disabled={loadingIndicators}
              placeholder="Pilih indikator"
            />
          </label>

          <label className="space-y-2">
            <span className="text-sm font-semibold text-slate-700">Wilayah / Breakdown</span>
            <SearchableSelect
              options={regions.map((item) => ({ value: item, label: item }))}
              value={region}
              onChange={setRegion}
              disabled={!regions.length}
              placeholder="Pilih wilayah"
            />
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
          <p className="mt-2 text-3xl font-bold text-slate-900 truncate" title={summary?.r_squared}>
            {summary?.r_squared != null && !isNaN(Number(summary.r_squared))
              ? Number(summary.r_squared).toFixed(4)
              : (summary?.r_squared ?? '-')}
          </p>
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
                <span className="font-semibold text-slate-900 truncate" title={summary?.slope_per_tahun}>
                  {summary?.slope_per_tahun != null && !isNaN(Number(summary.slope_per_tahun))
                    ? Number(summary.slope_per_tahun).toFixed(4)
                    : (summary?.slope_per_tahun ?? '-')}
                </span>
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

          {summary?.insight_text && (
            <div className="rounded-[28px] border border-dashed border-emerald-200 bg-emerald-50/60 p-6">
              <div className="mb-2 flex items-center gap-2">
                <svg className="h-5 w-5 text-emerald-700" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M13 10V3L4 14h7v7l9-11h-7z" /></svg>
                <p className="text-sm font-semibold text-emerald-800">AI Insight</p>
              </div>
              <p className="text-sm leading-relaxed text-emerald-900/80">
                {summary.insight_text}
              </p>
            </div>
          )}
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

      <HistoricalDetailTable rows={historicalDetail} />
    </div>
  )
}

export function TrendPredictionView({ onBack }) {
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

