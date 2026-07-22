import { useEffect, useState } from 'react'

const NARASI_API_BASE = import.meta.env.VITE_NARASI_API_BASE || ''

const buildApiUrl = (path) => `${NARASI_API_BASE}${path}`

async function fetchJson(path, options = {}) {
  const response = await fetch(buildApiUrl(path), options)
  let payload = {}

  try {
    payload = await response.json()
  } catch {
    payload = {}
  }

  if (!response.ok) {
    throw new Error(payload.detail || payload.message || 'Permintaan gagal')
  }

  return payload
}

function Icon({ name, className = 'h-5 w-5' }) {
  const icons = {
    arrowLeft: <path d="M19 12H5m6 6-6-6 6-6" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />,
    document: <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2-2V8zm0 0v6h6M8 13h8M8 17h5" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />,
    sparkle: <path d="m12 3-1.6 5.4L5 10l5.4 1.6L12 17l1.6-5.4L19 10l-5.4-1.6zM19 16l-.7 2.3L16 19l2.3.7L19 22l.7-2.3L22 19l-2.3-.7z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="1.7" />,
    arrowRight: <path d="M5 12h14m-6-6 6 6-6 6" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />,
    info: <><circle cx="12" cy="12" r="9" /><path d="M12 11v5m0-8h.01" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" /></>,
    close: <path d="m6 6 12 12M18 6 6 18" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" />,
    layers: <><path d="m12 3 8 4.5-8 4.5-8-4.5L12 3Z" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" /><path d="m4 12.5 8 4.5 8-4.5M4 17l8 4.5 8-4.5" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" /></>,
    check: <path d="m5 12 4.5 4.5L19 7" strokeLinecap="round" strokeLinejoin="round" strokeWidth="2.4" />,
  }

  return <svg className={className} fill="none" stroke="currentColor" viewBox="0 0 24 24" aria-hidden="true">{icons[name]}</svg>
}

export default function NarasiLaporanView({ onBack }) {
  const [opsiDataset, setOpsiDataset] = useState([])
  const [filterDataset, setFilterDataset] = useState('')
  const [jumlahHasilDitampilkan, setJumlahHasilDitampilkan] = useState(12)
  const [uuidDipilih, setUuidDipilih] = useState('')
  const [datasetTerpilih, setDatasetTerpilih] = useState([])
  const [memuatDataset, setMemuatDataset] = useState(true)
  const [loading, setLoading] = useState(false)
  const [hasil, setHasil] = useState(null)
  const [error, setError] = useState('')
  const [riwayat, setRiwayat] = useState([])
  const [sinkronisasi, setSinkronisasi] = useState(false)

  useEffect(() => {
    const controller = new AbortController()
    const muatDataset = async () => {
      try {
        const data = await fetchJson('/dataset', { signal: controller.signal })
        const daftarDataset = Array.isArray(data) ? data : []

        if (!controller.signal.aborted) {
          if (daftarDataset.length) {
            setOpsiDataset(daftarDataset)
            return
          }

          setSinkronisasi(true)
          const hasilSinkronisasi = await fetchJson('/dataset/sinkronkan', { method: 'POST', signal: controller.signal })
          const datasetSinkron = Array.isArray(hasilSinkronisasi.dataset) ? hasilSinkronisasi.dataset : []
          setOpsiDataset(datasetSinkron)
          if (!datasetSinkron.length) {
            setError('Sinkronisasi selesai, tetapi katalog dataset masih kosong. Periksa koneksi ke Satu Data Aceh.')
          }
        }
      } catch (err) {
        if (!controller.signal.aborted) {
          setError(err.message || 'Tidak dapat memuat daftar dataset.')
          setOpsiDataset([])
        }
      } finally {
        if (!controller.signal.aborted) {
          setMemuatDataset(false)
          setSinkronisasi(false)
        }
      }
    }

    muatDataset()
    return () => controller.abort()
  }, [])

  const tambahDataset = (dataset) => {
    if (!datasetTerpilih.some((item) => item.uuid === dataset.uuid)) {
      setDatasetTerpilih((previous) => [...previous, dataset])
    }
    setUuidDipilih('')
    setError('')
  }

  const hapusDataset = (uuid) => setDatasetTerpilih((previous) => previous.filter((dataset) => dataset.uuid !== uuid))
  const hapusSemuaDataset = () => setDatasetTerpilih([])

  const opsiTersaring = opsiDataset.filter((dataset) => (dataset.judul || '').toLocaleLowerCase('id-ID').includes(filterDataset.trim().toLocaleLowerCase('id-ID')))
  const hasilCepat = opsiTersaring.slice(0, jumlahHasilDitampilkan)

  const sinkronkanDataset = async () => {
    if (sinkronisasi || memuatDataset) return

    setSinkronisasi(true)
    setMemuatDataset(true)
    setError('')

    try {
      const hasilSinkronisasi = await fetchJson('/dataset/sinkronkan', { method: 'POST' })
      const datasetSinkron = Array.isArray(hasilSinkronisasi.dataset) ? hasilSinkronisasi.dataset : []
      setOpsiDataset(datasetSinkron)
      setFilterDataset('')
      setJumlahHasilDitampilkan(12)
      setUuidDipilih('')

      if (!datasetSinkron.length) {
        setError('Sinkronisasi selesai, tetapi katalog dataset masih kosong.')
      }
    } catch (err) {
      setError(err.message || 'Tidak dapat menyinkronkan dataset.')
    } finally {
      setMemuatDataset(false)
      setSinkronisasi(false)
    }
  }

  const buatLaporan = async () => {
    if (!datasetTerpilih.length || loading) return

    setLoading(true)
    setError('')
    setHasil(null)
    const labelDataset = datasetTerpilih.map((dataset) => dataset.judul).join(', ')

    try {
      const params = new URLSearchParams()
      datasetTerpilih.forEach((dataset) => {
        params.append('uuid', dataset.uuid)
        params.append('judul', dataset.judul)
      })
      const data = await fetchJson(`/narasi?${params.toString()}`)

      if (data.pesan) setError(data.pesan)
      if (data.narasi) setHasil(data)

      setRiwayat((previous) => [
        { dataset: labelDataset, status: data.pesan ? 'Data kosong' : 'Selesai', waktu: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) },
        ...previous,
      ].slice(0, 5))
    } catch (err) {
      const message = err.message || 'Tidak dapat terhubung ke server narasi.'
      setError(message.includes('fetch') ? 'Tidak dapat terhubung ke server narasi. Pastikan backend berjalan di port 8010.' : message)
      setRiwayat((previous) => [
        { dataset: labelDataset, status: 'Gagal', waktu: new Date().toLocaleTimeString('id-ID', { hour: '2-digit', minute: '2-digit' }) },
        ...previous,
      ].slice(0, 5))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="space-y-6 md:space-y-8">
      <section className="hero-panel relative overflow-hidden rounded-[32px] border border-white/80 bg-white px-6 py-8 shadow-xl shadow-slate-200/50 md:px-10 md:py-10">
        <div className="hero-orb hero-orb-one" aria-hidden="true" />
        <div className="hero-orb hero-orb-two" aria-hidden="true" />
        <div className="relative flex flex-col gap-7 animate-enter">
          <div className="flex flex-wrap items-center justify-between gap-4">
            <span className="inline-flex items-center gap-2 rounded-full bg-red-50 px-4 py-2 text-[11px] font-bold uppercase tracking-[0.16em] text-red-700"><Icon name="sparkle" className="h-4 w-4" /> AI Narasi Laporan</span>
            <button type="button" onClick={onBack} className="inline-flex items-center gap-2 rounded-full px-3 py-2 text-sm font-semibold text-slate-600 transition hover:bg-slate-100 hover:text-slate-900"><Icon name="arrowLeft" className="h-4 w-4" /> Beranda</button>
          </div>
          <div className="max-w-3xl">
            <h1 className="text-3xl font-bold leading-tight text-slate-900 md:text-5xl">AI yang menyusun data menjadi narasi laporan.</h1>
            <p className="mt-4 max-w-2xl text-sm leading-relaxed text-slate-600 md:text-base">Pilih satu atau beberapa dataset resmi Satu Data Aceh. AI akan merangkai angka, wilayah, dan periode datanya menjadi draf narasi formal yang siap ditinjau.</p>
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <button type="button" onClick={sinkronkanDataset} disabled={memuatDataset || sinkronisasi} className="inline-flex items-center gap-2 rounded-full border border-red-200 bg-red-50 px-4 py-2 text-sm font-semibold text-red-700 transition hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-60">
              <Icon name="layers" className="h-4 w-4" />
              {sinkronisasi ? 'Menyinkronkan...' : 'Sinkronkan data'}
            </button>
            <span className="text-sm text-slate-500">{opsiDataset.length ? `${opsiDataset.length.toLocaleString('id-ID')} dataset tersedia` : 'Menunggu katalog dataset'}</span>
          </div>
          <div className="grid gap-3 sm:grid-cols-3">
            {['Pilih dataset', 'Tambahkan ke daftar', 'Dapatkan narasi'].map((step, index) => <div key={step} className="feature-card flex items-center gap-3 rounded-2xl border border-slate-100 bg-white/85 px-4 py-3 shadow-sm"><span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-full bg-red-700 text-xs font-bold text-white shadow-sm">0{index + 1}</span><span className="text-sm font-semibold text-slate-700">{step}</span></div>)}
          </div>
        </div>
      </section>

      <div className="grid items-start gap-6 lg:grid-cols-[minmax(0,1fr)_300px]">
        <section className="feature-card rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm md:p-8">
          <div className="flex items-start gap-4 border-b border-slate-100 pb-6"><span className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-red-50 text-red-700"><Icon name="document" /></span><div><p className="text-xs font-bold uppercase tracking-[0.16em] text-red-700">Buat laporan</p><h2 className="mt-1 text-xl font-bold text-slate-900">Pilih dataset untuk dinarasikan</h2><p className="mt-1 text-sm text-slate-500">Pilih topik, lalu klik <b>Tambah</b> pada dataset yang ingin digunakan. Anda dapat menambahkan lebih dari satu dataset.</p></div></div>
          <div className="mt-6">
            <label className="block"><span className="mb-2 block text-sm font-semibold text-slate-700">1. Pilih atau cari topik</span><div className="relative"><input type="search" value={filterDataset} onChange={(event) => { setFilterDataset(event.target.value); setUuidDipilih(''); setJumlahHasilDitampilkan(12) }} placeholder="Contoh: pendidikan, penduduk, kesehatan" className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3.5 pr-24 text-sm text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-red-300 focus:bg-white focus:ring-4 focus:ring-red-50" />{filterDataset && <button type="button" onClick={() => { setFilterDataset(''); setUuidDipilih(''); setJumlahHasilDitampilkan(12) }} className="absolute right-3 top-1/2 -translate-y-1/2 rounded-full px-2 py-1 text-xs font-semibold text-slate-500 hover:bg-slate-200 hover:text-slate-800">Reset</button>}</div></label>
            <div className="mt-3 flex flex-wrap gap-2">{['Penduduk', 'Pendidikan', 'Kesehatan', 'Ekonomi', 'Kemiskinan'].map((topik) => <button key={topik} type="button" onClick={() => { setFilterDataset(topik); setUuidDipilih(''); setJumlahHasilDitampilkan(12) }} className="rounded-full border border-slate-200 px-3 py-1.5 text-xs font-semibold text-slate-600 transition hover:border-red-200 hover:bg-red-50 hover:text-red-700">{topik}</button>)}</div>
            <div className="mt-4 overflow-hidden rounded-2xl border border-slate-200 bg-white shadow-sm"><div className="border-b border-slate-100 bg-slate-50 px-4 py-3"><p className="text-sm font-semibold text-slate-800">2. Pilih dari hasil</p><p className="mt-0.5 text-xs text-slate-500">{memuatDataset ? 'Memuat katalog dataset...' : `Menampilkan ${hasilCepat.length.toLocaleString('id-ID')} dari ${opsiTersaring.length.toLocaleString('id-ID')} dataset`}</p></div>{memuatDataset ? <p className="px-4 py-5 text-sm text-slate-500">Menyiapkan daftar dataset...</p> : hasilCepat.length ? <><div className="max-h-80 divide-y divide-slate-100 overflow-y-auto">{hasilCepat.map((dataset) => { const sudahDipilih = datasetTerpilih.some((item) => item.uuid === dataset.uuid); return <div key={dataset.uuid} className="group flex items-center justify-between gap-4 px-4 py-3.5 transition hover:bg-red-50/60"><span className="feature-icon flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-red-50 text-red-700"><Icon name="document" className="h-4 w-4" /></span><p className="min-w-0 flex-1 text-sm font-semibold leading-relaxed text-slate-800">{dataset.judul}</p><button type="button" onClick={() => tambahDataset(dataset)} disabled={sudahDipilih} className="feature-link inline-flex shrink-0 items-center gap-1.5 rounded-full border border-red-200 px-3.5 py-2 text-xs font-bold text-red-700 disabled:cursor-not-allowed disabled:bg-emerald-600 disabled:text-white"><Icon name={sudahDipilih ? 'check' : 'arrowRight'} className="h-3.5 w-3.5" />{sudahDipilih ? 'Ditambahkan' : 'Tambah'}</button></div> })}</div>{opsiTersaring.length > hasilCepat.length && <div className="border-t border-slate-100 bg-white p-3 text-center"><button type="button" onClick={() => setJumlahHasilDitampilkan((jumlah) => jumlah + 12)} className="feature-link rounded-full border border-red-100 bg-red-50 px-4 py-2 text-sm font-semibold text-red-700">Tampilkan 12 dataset lagi</button></div>}</> : <p className="px-4 py-5 text-sm text-slate-500">Tidak ada dataset yang cocok. Coba pilih topik lain atau hapus filter.</p>}</div>
            <div className="mt-4 flex flex-col gap-3 border-t border-slate-100 pt-4 sm:flex-row sm:items-end"><label className="block min-w-0 flex-1"><span className="mb-2 block text-xs font-semibold text-slate-500">Tidak menemukan dataset? Pilih dari daftar lengkap</span><select value={uuidDipilih} onChange={(event) => setUuidDipilih(event.target.value)} disabled={memuatDataset || !opsiTersaring.length} className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-red-300 focus:bg-white focus:ring-4 focus:ring-red-50 disabled:cursor-not-allowed disabled:opacity-60"><option value="">{memuatDataset ? 'Memuat dataset...' : opsiTersaring.length ? 'Pilih dataset' : 'Tidak ada dataset sesuai filter'}</option>{opsiTersaring.map((dataset) => <option key={dataset.uuid} value={dataset.uuid} disabled={datasetTerpilih.some((item) => item.uuid === dataset.uuid)}>{dataset.judul}{datasetTerpilih.some((item) => item.uuid === dataset.uuid) ? ' (sudah dipilih)' : ''}</option>)}</select></label><button type="button" onClick={() => { const dataset = opsiDataset.find((item) => item.uuid === uuidDipilih); if (dataset) tambahDataset(dataset) }} disabled={!uuidDipilih} className="rounded-full border border-red-200 bg-red-50 px-5 py-3 text-sm font-semibold text-red-700 transition hover:bg-red-100 disabled:cursor-not-allowed disabled:opacity-50">+ Tambah</button></div>
          </div>
          <div className="mt-5 rounded-2xl border border-red-100 bg-gradient-to-br from-red-50 to-white p-4"><div className="flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-3"><span className="flex h-10 w-10 items-center justify-center rounded-xl bg-red-700 text-white shadow-sm"><Icon name="layers" className="h-5 w-5" /></span><div><p className="text-sm font-bold text-slate-900">Dataset untuk narasi <span className="text-red-700">({datasetTerpilih.length})</span></p><p className="text-xs text-slate-500">Pilih minimal satu dataset untuk melanjutkan.</p></div></div>{datasetTerpilih.length > 0 && <button type="button" onClick={hapusSemuaDataset} className="text-xs font-semibold text-slate-500 hover:text-red-700">Hapus semua</button>}</div><div className="mt-4 flex flex-wrap gap-2">{datasetTerpilih.length ? datasetTerpilih.map((dataset) => <span key={dataset.uuid} className="inline-flex items-center gap-2 rounded-xl border border-red-100 bg-white py-2 pl-3 pr-2 text-xs font-semibold text-slate-700 shadow-sm">{dataset.judul}<button type="button" onClick={() => hapusDataset(dataset.uuid)} aria-label={`Hapus ${dataset.judul}`} className="rounded-lg p-1 text-slate-400 transition hover:bg-red-50 hover:text-red-700"><Icon name="close" className="h-3.5 w-3.5" /></button></span>) : <p className="text-sm text-slate-500">Belum ada dataset dipilih. Klik tombol <b>Tambah</b> pada daftar di atas.</p>}</div></div>
          <div className="mt-5 border-t border-slate-100 pt-5"><button type="button" onClick={buatLaporan} disabled={!datasetTerpilih.length || loading} className="flex w-full items-center justify-center gap-3 rounded-2xl bg-red-700 px-5 py-4 text-sm font-bold text-white shadow-lg shadow-red-100 transition hover:bg-red-800 disabled:cursor-not-allowed disabled:bg-slate-300 disabled:shadow-none"><span className="flex h-7 w-7 items-center justify-center rounded-full bg-white/15"><Icon name="sparkle" className="h-4 w-4" /></span>{loading ? 'AI sedang menyusun narasi...' : datasetTerpilih.length ? `Buat narasi dari ${datasetTerpilih.length} dataset` : 'Pilih dataset untuk membuat narasi'}<Icon name="arrowRight" className="h-4 w-4" /></button></div>
          {error && <div className="mt-5 flex gap-3 rounded-2xl border border-red-100 bg-red-50 px-4 py-3 text-sm leading-relaxed text-red-800"><Icon name="info" className="mt-0.5 h-5 w-5 shrink-0" />{error}</div>}
        </section>
        <aside className="hero-panel overflow-hidden rounded-[32px] border border-white/80 bg-white p-6 text-slate-900 shadow-xl shadow-slate-200/50"><span className="flex h-11 w-11 items-center justify-center rounded-2xl bg-red-700 text-white shadow-sm"><Icon name="sparkle" /></span><p className="mt-5 text-xs font-bold uppercase tracking-[0.16em] text-red-700">Tentang fitur ini</p><h2 className="mt-2 text-xl font-bold">AI Narasi Laporan</h2><p className="mt-3 text-sm leading-relaxed text-slate-600">Asisten ini mengubah dataset statistik menjadi draf narasi formal. Gunakan hasilnya sebagai bahan laporan, lalu verifikasi kembali angka dan konteksnya.</p><div className="mt-6 space-y-3 border-t border-slate-100 pt-5">{['Menggabungkan beberapa dataset', 'Mempertahankan angka dari sumber data', 'Menyusun bahasa laporan yang formal'].map((item) => <div key={item} className="flex gap-2 text-xs leading-relaxed text-slate-600"><span className="mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full bg-red-700 text-white"><Icon name="check" className="h-3 w-3" /></span>{item}</div>)}</div></aside>
      </div>
      {loading && <section className="animate-pulse rounded-[32px] border border-slate-200 bg-white p-8 shadow-sm"><div className="h-3 w-28 rounded bg-slate-100" /><div className="mt-5 h-8 max-w-md rounded bg-slate-100" /><div className="mt-6 space-y-3"><div className="h-3 rounded bg-slate-100" /><div className="h-3 rounded bg-slate-100" /><div className="h-3 w-3/4 rounded bg-slate-100" /></div></section>}
      {hasil && !loading && <section className="feature-card rounded-[32px] border border-slate-200 bg-white p-6 shadow-sm md:p-8"><div className="border-b border-slate-100 pb-6"><span className="inline-flex rounded-full bg-red-50 px-3 py-1.5 text-[11px] font-bold uppercase tracking-[0.14em] text-red-700">Narasi berhasil dibuat</span><h2 className="mt-3 text-2xl font-bold text-slate-900">{hasil.judul}</h2><p className="mt-2 text-sm text-slate-500">Menggunakan {hasil.dataset?.length ?? datasetTerpilih.length} dataset terpilih.</p></div><article className="mt-6 max-w-4xl whitespace-pre-line text-[15px] leading-8 text-slate-700">{hasil.narasi}</article><p className="mt-7 border-t border-slate-100 pt-4 text-xs leading-relaxed text-slate-400">Sumber: Satu Data Aceh. Mohon verifikasi narasi sebelum digunakan sebagai dokumen resmi.</p></section>}
      <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm"><div className="flex items-center justify-between gap-4"><div><p className="text-xs font-bold uppercase tracking-[0.16em] text-slate-400">Sesi ini</p><h2 className="mt-1 text-lg font-bold text-slate-900">Riwayat pembuatan narasi</h2></div><span className="rounded-full bg-slate-100 px-3 py-1.5 text-xs font-semibold text-slate-600">{riwayat.length} aktivitas</span></div><div className="mt-5 overflow-x-auto">{riwayat.length === 0 ? <p className="rounded-2xl bg-slate-50 px-4 py-5 text-sm text-slate-500">Belum ada narasi yang dibuat pada sesi ini.</p> : <table className="min-w-full text-left text-sm"><thead className="border-b border-slate-100 text-[11px] font-bold uppercase tracking-wider text-slate-400"><tr><th className="pb-3 pr-5">Dataset</th><th className="pb-3 pr-5">Status</th><th className="pb-3">Waktu</th></tr></thead><tbody className="divide-y divide-slate-100">{riwayat.map((item, index) => <tr key={`${item.dataset}-${index}`}><td className="py-4 pr-5 font-semibold text-slate-800">{item.dataset}</td><td className={`py-4 pr-5 font-semibold ${item.status === 'Selesai' ? 'text-emerald-600' : item.status === 'Gagal' ? 'text-red-600' : 'text-amber-600'}`}>{item.status}</td><td className="py-4 text-slate-500">{item.waktu}</td></tr>)}</tbody></table>}</div></section>
    </div>
  )
}
