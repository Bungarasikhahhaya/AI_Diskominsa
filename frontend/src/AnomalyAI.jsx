import { useEffect, useMemo, useRef, useState } from "react";
import { Database, ShieldCheck, TriangleAlert, Activity } from "lucide-react";
import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    LabelList,
    CartesianGrid
} from "recharts";
import { getDatasets, analyzeDataset } from "./api/anomalyApi";

//=====================
// Dataset Selector
//=====================
function DatasetSelector({
    datasets,
    selected,
    search,
    setSearch,
    onSelect,
    showSuggestion,
    setShowSuggestion,
    inputRef
}) {

    return (
        <div className="flex-1 relative">
            <input
                ref={inputRef}
                type="text"
                placeholder="Cari nama dataset..."
                value={search}
                onChange={(e)=>{
                    setSearch(e.target.value);
                    setShowSuggestion(true);
                }}
                className="
                w-full
                h-[44px]
                rounded-xl
                border
                border-[#D0D5DD]
                bg-white
                px-4
                text-sm
                placeholder:text-[#98A2B3]
                border : #667085
                focus:ring-2
                focus:ring-[#EAECF0]
                outline-none
                transition"
            />
            {
                showSuggestion &&
                search.length >= 1 &&
                datasets.length > 0 && (
                    <div
                    className="
                    absolute
                    left-0
                    right-0
                    top-full
                    mt-2
                    z-20
                    border
                    border-gray-200
                    rounded-xl
                    bg-white
                    shadow-lg
                    max-h-72
                    overflow-y-auto"
                    >
                        {
                            datasets.map((dataset) => (
                                <div
                                    key={dataset.identifier}
                                    onMouseDown={(e) => {
                                        e.preventDefault();
                                        setShowSuggestion(false);
                                        onSelect(dataset);
                                    }}
                                    className={`
                                        p-3
                                        cursor-pointer
                                        border-b
                                        last:border-b-0
                                        hover:bg-gray-50
                                        transition
                                        ${
                                            selected === dataset.identifier
                                                ? "bg-red-100"
                                                : ""
                                        }
                                    `}
                                >
                                    <div className="font-semibold text-[#101828]">
                                        {dataset.title}
                                    </div>
                                    <div className="text-sm text-gray-500">
                                        {dataset.publisher || "-"}
                                    </div>
                                </div>
                            ))
                        }
                    </div>
                )
            }
        </div>
    );
}

//=====================
//SummaryCard
//=====================
function SummaryCard({
    title,
    value,
    badge,
    badgeColor = "gray",
    icon,
}) {

    const badgeStyle = {
        red: "bg-[#FEECEC] text-[#B42318]",
        yellow: "bg-[#FFF4E5] text-[#B54708]",
        green: "bg-[#ECFDF3] text-[#027A48]",
        gray: "bg-gray-100 text-gray-700"
    };

    const icons = {
        database: <Database size={16} />,
        normal: <ShieldCheck size={16} />,
        anomaly: <TriangleAlert size={16} />,
        risk: <Activity size={16} />
    };

    return (
        <div
            className="
            min-h-[108px]
            bg-white
            rounded-xl
            border
            border-gray-200
            p-4
            py-4"
        >

            <div
                className="
                flex
                items-center
                gap-2
                text-[#667085]
                uppercase
                tracking-wide"
            >
                {icons[icon]}

                <span
                    className="
                    text-[13px]
                    font-medium"
                >
                    {title}
                </span>
            </div>

            <div className="mt-2">
                <h2
                    className="
                    text-[23px]
                    leading-none
                    font-bold
                    text-[#101828]"
                >
                    {value}
                </h2>
            </div>

            {
                badge && (
                    <div className="mt-2">
                        <span
                            className={`
                            inline-flex
                            items-center
                            whitespace-nowrap
                            rounded-full
                            px-3
                            py-1
                            text-[13px]
                            font-medium
                            ${badgeStyle[badgeColor]}
                        `}
                        >
                            {badge}
                        </span>
                    </div>
                )
            }

        </div>
    );
}

//=====================
// DatasetInfo
//=====================
function DatasetInfo({ dataset }) {
    if (!dataset) return null;
    const formatDate = (date) => {
        if (!date) return "-";
        return new Date(date).toLocaleDateString(
            "id-ID",
            {
                day: "numeric",
                month: "long",
                year: "numeric"
            }
        );
    };

    return (
        <div
            className="
            gap-x-12
            gap-y-6
            py-2"
        >

            <h2
                className="
                text-xl
                font-bold
                text-[#101828]
                mb-6"
            >
                Informasi Dataset
            </h2>

            <div>
                <p
                    className="
                    text-sm
                    text-[#667085]"
                >
                    Nama Dataset
                </p>
                <p
                    className="
                    text-lg
                    font-semibold
                    leading-7
                    break-words
                    text-[#101828]
                    mt-1"
                >
                    {dataset.title || "-"}
                </p>
            </div>

            <div className="h-px bg-gray-100 my-5"/>
            <div
                className="
                grid
                grid-cols-1
                md:grid-cols-3
                gap-6"
            >

                <div>
                    <p className="text-sm text-[#667085]">
                        Sumber Data
                    </p>
                    <p className="font-medium mt-1">
                        {dataset.publisher || "-"}
                    </p>
                </div>

                <div>
                    <p className="text-sm text-[#667085]">
                        Tahun Data
                    </p>
                    <p className="font-medium mt-1">
                        {dataset.year || "-"}
                    </p>
                </div>

                <div>
                    <p className="text-sm text-[#667085]">
                        Terakhir Update
                    </p>
                    <p className="font-medium mt-1">
                        {formatDate(dataset.modified)}
                    </p>
                </div>
            </div>
        </div>
    );
}

//=====================
// InsightCard
//=====================
function InsightCard({ insight }) {
    if (!insight) return null;
    return (
        <div className="flex flex-col">
            <h3
                className="
                text-lg
                font-bold
                text-[#101828]"
            >
                Ringkasan Analisis AI
            </h3>

            <p
                className="
                mt-3
                text-sm
                leading-7
                text-[#667085]"
            >
                {insight.summary}
            </p>

            <div className="border-t border-gray-100 my-6"/>

            <h4
                className="
                text-xs
                font-semibold
                uppercase
                tracking-wider
                mb-4"
            >
                Temuan Penting
            </h4>

            <div className="space-y-3">
                {
                    insight.findings.map((item,index)=>(
                        <div
                            key={index}
                            className="
                            flex
                            gap-3
                            items-start"
                        >

                            <div
                                className="
                                w-1.5
                                h-1.5
                                rounded-full
                                bg-[#D0D5DD]
                                mt-2
                                shrink-0"
                            />

                            <p
                                className="
                                text-sm
                                leading-6
                                text-[#475467]"
                            >
                                {item}
                            </p>
                        </div>
                    ))
                }
            </div>
        </div>
    );
}

//=====================
// RecommendationCard
//=====================
function RecommendationCard({
    recommendation
}) {
    if (!recommendation) return null;
    return (
        <div className="min-h-[96px]">
            <h3
                className="
                text-lg
                font-bold
                text-[#101828]
                "
            >
                Rekomendasi AI
            </h3>

            <p
                className="
                text-[#667085]
                text-sm
                leading-7
                mt-3"
            >
                Prioritas tindakan yang disarankan AI berdasarkan pola anomali yang ditemukan.
            </p>

            <div className="border-t border-gray-100 my-6"/>

            <h4
                className="
                text-xs
                font-semibold
                uppercase
                tracking-wider
                mb-4"
            >
                Tindakan Prioritas
            </h4>

            <div className="space-y-3">
                {
                    recommendation.map((item,index)=>(
                        <div
                            key={index}
                            className="
                            flex
                            items-start
                            gap-3"
                        >

                            <div
                                className="
                                w-1.5
                                h-1.5
                                rounded-full
                                bg-[#D0D5DD]
                                mt-2
                                shrink-0"
                                />
                            <p
                                className="
                                    
                                    text-sm
                                    leading-6
                                    text-[#475467]"
                                >
                                {item.text}
                            </p>
                        </div>
                    ))
                }
            </div>
        </div>
    );
}

//=====================
// Chart
//=====================
function HorizontalChart({ 
    rows = []
 }) {

    if (!rows || rows.length === 0) {
        return (
            <div
                className="
                flex
                flex-col"
            >
                <h3
                    className="
                    text-lg
                    font-semibold
                    text-[#101828]"
                >
                    Distribusi Anomali
                </h3>
                <p
                    className="
                    mt-2
                    text-sm
                    text-[#667085]"
                >
                    Belum ada data yang dapat divisualisasikan.
                </p>
            </div>
        );
    }

    // ===============================
    // Group berdasarkan kabupaten
    // ===============================

    const grouped = {};
    rows.forEach((row) => {
        const nama =
            (row.bps_nama_kabupaten_kota || "Tidak diketahui")
                .replace(/^Kabupaten\s+/i, "")
                .replace(/^Kota\s+/i, "");

        if (!grouped[nama]) {
            grouped[nama] = {
                nama,
                total: 0,
                tinggi: 0,
                sedang: 0,
                rendah: 0
            };
        }
        grouped[nama].total++;
        switch (row.severity) {
            case "Tinggi":
                grouped[nama].tinggi++;
                break;
            case "Sedang":
                grouped[nama].sedang++;
                break;
            case "Rendah":
                grouped[nama].rendah++;
                break;
            default:
                break;
        }
    });

    // ===============================
    // Convert menjadi array
    // ===============================

    const chartData = Object.values(grouped)
    .sort((a, b) => {

        if (b.total !== a.total)
            return b.total - a.total;

        return a.nama.localeCompare(b.nama);

    });
    const chartHeight = Math.max(
        280,
        chartData.length * 24
    );

    // ===============================
    // UI
    // ===============================

    return (
        <div
            className="
            py-2"
        >
            <div
                className="
                flex
                justify-between
                items-center
                mb-6"
            >
                <div>
                    <h3
                        className="
                        text-lg
                        font-bold
                        text-[#101828]"
                    >
                        Distribusi Anomali
                    </h3>
                    <p
                        className="
                        text-sm
                        text-[#667085]"
                    >
                        {chartData.length} Kabupaten/Kota
                    </p>
                </div>
            </div>
            
            <div
                className="
                pr-2
                scroll-smooth
                "
            >
                <ResponsiveContainer
                    width="100%"
                    height={chartHeight}
                >
                    <BarChart
                        layout="vertical"
                        barSize={18}
                        data={chartData}
                        barCategoryGap={2}
                        margin={{
                            top:8,
                            right:20,
                            left:0,
                            bottom:8
                        }}
                    >

                        <XAxis
                            type="number"
                            allowDecimals={false}
                            axisLine={false}
                            tickLine={false}
                            tick={{
                            fill:"#667085",
                            fontSize:12
                        }}
                        />

                        <YAxis
                            type="category"
                            dataKey="nama"
                            width={120}
                            axisLine={false}
                            tickLine={false}
                            tick={{
                            fill:"#344054",
                            fontSize:13
                            }}
                        />

                        <CartesianGrid
                            stroke="#F2F4F7"
                            horizontal
                            vertical={false}
                        />

                        <Tooltip
                            content={({active,payload})=>{
                                if(!active || !payload || !payload.length)
                                    return null;
                                const data = payload[0].payload;
                                return(
                                    <div
                                        className="
                                        rounded-xl
                                        border
                                        border-gray-200
                                        bg-white
                                        px-4
                                        py-3
                                        shadow-sm"
                                    >
                                        <p className="font-semibold">
                                            {data.nama}
                                        </p>
                                        <p className="text-sm text-gray-600">
                                            {data.total} data anomali
                                        </p>
                                    </div>
                                )
                            }}
                        />

                        <Bar
                            dataKey="total"
                            radius={[4,4,4,4]}
                            fill="#B42318"
                        >
                            <LabelList
                                position="right"
                                dataKey="total"
                                style={{
                                    fontSize:12,
                                    fill:"#667085"
                                }}
                            />
                        </Bar>
                    </BarChart>

                </ResponsiveContainer>
            </div>
        </div>
    );
}

//=====================
// Chart
//=====================
function AnomalyTable({
    rows,
    startIndex = 0
}) {

    if (!rows || rows.length === 0) {
        return (
            <div
                id="anomaly-table"
                className="
                rounded-2xl
                border
                border-gray-50
                text-center
                overflow-hidden"
            >
                <div className="text-5xl mb-4">
                    🔍
                </div>
                <h3 className="text-xl font-bold">
                    Data tidak ditemukan
                </h3>
                <p className="text-gray-500 mt-2">
                    Coba ubah kata kunci pencarian atau filter severity.
                </p>
            </div>
        );
    }

    const indicatorName =
        rows.length > 0 && rows[0].indicator
            ? rows[0].indicator
                .replaceAll("_", " ")
                .replace(/\b\w/g, c => c.toUpperCase())
            : "Indikator";
            
    return (
        <div
            className="
            bg-white
            rounded-2xl
            border
            border-gray-200
            overflow-hidden"
        >
            <div
                className="w-full"
            >
                <div
                className="
                flex
                items-center
                justify-between
                px-5
                py-4
                border-b
                border-gray-100"
                >
                    <div>
                        <h3
                        className="
                        text-lg
                        font-semibold
                        text-[#101828]"
                        >
                            Detail Anomali
                        </h3>

                        <p
                        className="
                        text-sm
                        text-[#667085]
                        mt-1"
                        >
                            Daftar data yang memerlukan validasi lebih lanjut.
                        </p>
                    </div>
                </div>
                <table
                    className="
                    w-full
                    text-sm"
                >
                    <thead
                        className="
                        sticky
                        top-0
                        bg-[#F8F9FB]
                        shadow-[0_1px_0_0_#E4E7EC]
                        "
                    >
                        <tr>
                            <th className="w-14 px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide">
                                No
                            </th>

                            <th className="w-20 px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide">
                                Baris
                            </th>

                            <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide">
                                Kabupaten/Kota
                            </th>

                            <th className="px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide">
                                {indicatorName}
                            </th>

                            <th
                                className="w-32 px-4 py-2 text-left text-xs font-semibold uppercase tracking-wide"
                                title="Prioritas menunjukkan tingkat penyimpangan data"
                            >
                                Prioritas
                            </th>

                            <th
                                className="
                                w-24
                                px-4
                                py-2
                                text-left
                                text-xs
                                font-semibold
                                uppercase
                                tracking-wide"
                                title="Semakin besar skor AI maka semakin menyimpang"
                            >
                                Skor AI
                            </th>
                        </tr>
                        </thead>
                    <tbody>
                        {
                            rows.map((row, index) => {
                                const namaKabupaten = (row.bps_nama_kabupaten_kota || "-")
                                    .replace(/^Kabupaten\s+/i, "")
                                    .replace(/^Kota\s+/i, "");
                                
                                return (
                                    <tr
                                        key={index}
                                        id={`row-${row.row_number}`}
                                        className="
                                        border-b
                                        last:border-b-0
                                        border-gray-100
                                        hover:bg-[#FCFCFD]
                                        transition-colors"
                                    >

                                        {/* Nomor */}
                                        <td className="px-4 py-2 text-xs text-gray-400">
                                            {startIndex + index + 1}
                                        </td>

                                        {/* Nomor Baris Dataset Asli */}
                                        <td className="px-4 py-2">
                                            {row.row_number}
                                        </td>

                                        {/* Kabupaten */}
                                        <td
                                            className="
                                            px-4
                                            py-2
                                            font-semibold
                                            text-[#101828]
                                        "
                                        >
                                                {namaKabupaten}
                                        </td>

                                        {/* Nilai indikator */}
                                        <td
                                            className="
                                            px-4
                                            py-2
                                            max-w-[240px]
                                            lg:max-w-[320px]
                                        "
                                        >
                                            <div
                                                className="
                                                truncate
                                                text-[#344054]"
                                                title={row.indicator_value}
                                            >
                                                {row.indicator_value}
                                            </div>
                                        </td>

                                        {/* Severity */}
                                        <td className="px-4 py-2">
                                            {
                                                row.severity === "Tinggi" ? (

                                                    <span className="inline-flex items-center gap-2 bg-[#FEE2E2] text-[#B42318] px-2 py-0.5 rounded-full text-xs font-medium">
                                                        Tinggi
                                                    </span>

                                                ) : row.severity === "Sedang" ? (

                                                    <span className="inline-flex items-center gap-2 bg-[#FEF3C7] text-[#B45309] px-2 py-0.5 rounded-full text-xs font-medium">
                                                        Sedang
                                                    </span>

                                                ) : row.severity === "Rendah" ? (

                                                    <span className="inline-flex items-center gap-2 bg-[#DCFCE7] text-[#15803D] px-2 py-0.5 rounded-full text-xs font-medium">
                                                        Rendah
                                                    </span>

                                                ) : (

                                                    <span className="inline-flex items-center gap-2 bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full text-xs">
                                                        -
                                                    </span>

                                                )
                                            }
                                        </td>

                                        {/* Score */}
                                        <td
                                            className={`px-4 py-2 text-[#344054] text-left font-medium`}
                                        >
                                            {row.score.toFixed(3)}
                                        </td>
                                    </tr>
                                );
                            })
                        }
                    </tbody>
                </table>
            </div>
        </div>
    );
}


export default function AnomalyAI() {

    // ==========================
    // State
    // ==========================

    const [debouncedSearch, setDebouncedSearch] = useState("");
    const [datasets, setDatasets] = useState([]);
    const [selected, setSelected] = useState("");
    const [loading, setLoading] = useState(false);
    const [result, setResult] = useState(null);
    const [severity, setSeverity] = useState("Semua");
    const [datasetSearch, setDatasetSearch] = useState("");
    const [tableSearch, setTableSearch] = useState("");
    const [currentPage, setCurrentPage] = useState(1);
    const rowsPerPage = 10;
    const inputRef = useRef(null);
    const [showSuggestion, setShowSuggestion] = useState(false);

    // ==========================
    // Load Dataset
    // ==========================

    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(datasetSearch);
        },250);
        return ()=>clearTimeout(timer);
    },[datasetSearch]);

    useEffect(() => {
        if(debouncedSearch.length<1){
            setDatasets([]);
            return;
        }
        loadDatasets();
    },[debouncedSearch]);

    const requestId = useRef(0);

    const loadDatasets = async ()=>{
        const id = ++requestId.current;
        try{
            const data = await getDatasets(debouncedSearch);
            if(id!==requestId.current){
                return;
            }
            setDatasets(data);
        }
        catch(error){
            console.error(error);
        }
    }

    const handleSelectDataset = (dataset) => {
        setSelected(dataset.identifier);
        setDatasetSearch(dataset.title);
        setResult(null);
        setDatasets([]);
        setShowSuggestion(false);
        inputRef.current?.blur();
    };

    // ==========================
    // Analyze
    // ==========================

    const handleAnalyze = async () => {
        if (!selected) {
            alert("Silakan pilih dataset.");
            return;
        }

        setLoading(true);

        try {
            const data = await analyzeDataset(selected);

            if (!data) {
                setResult(null);
                alert("Dataset ini belum dapat dianalisis.");
                return;
            }

            setResult(data);
            setCurrentPage(1);
        }
        catch (err) {
            console.error(err);
            setResult(null);
            alert("Terjadi kesalahan saat melakukan analisis.");
        }
        finally {
            setLoading(false);
        }
    };

    // ==========================
    // Filter Table
    // ==========================

    const filteredRows = useMemo(() => {
        if (!result) return [];
        return result.anomaly.all
            .filter(row => row.status === "Anomali")
            .filter(row =>
                severity === "Semua"
                ||
                row.severity === severity
            )
            .filter(row =>
                (row.bps_nama_kabupaten_kota || "")
                    .toLowerCase()
                    .includes(
                        tableSearch.toLowerCase()
                    )
            );
    }, [result, severity, tableSearch]);


    const sortedRows = [...filteredRows].sort(
        (a, b) => b.score - a.score
    );

    const chartRows = useMemo(() => {
        if (!result) return [];

        return result.anomaly.all.filter(
            row => row.status === "Anomali"
        );
    }, [result]);

    const totalPages = Math.ceil(
        sortedRows.length / rowsPerPage
    );
    const startIndex =
        (currentPage - 1)
        *
        rowsPerPage;
    const endIndex =
        startIndex
        +
        rowsPerPage;
    const currentRows =
        sortedRows.slice(
            startIndex,
            endIndex
        );

    let risk="Rendah";
    let color="green";

    if(result){
        if(result.summary.anomaly_percentage>=20){
            risk="Tinggi";
            color="red";
        }

        else if(result.summary.anomaly_percentage>=5){
            risk="Sedang";
            color="yellow";
        }
    }

    // ==========================
    // UI
    // ==========================

    return (
        <div
            className="
            min-h-screen
            bg-[#F9FAFB]
            px-10
            py-8"
        >
            <main
                className="
                max-w-7xl
                mx-auto
                space-y-10"
            >
            <button
            className="
            inline-flex
            items-center
            gap-2
            text-sm
            font-medium
            text-[#667085]
            hover:text-[#101828]
            transition"
            >
            ← Kembali ke Beranda
        </button>

            {/* ========================== */}
            {/* Analyze Card */}
            {/* ========================== */}

            <section
                className="
                bg-white
                border
                border-gray-200
                rounded-3xl
                p-8
                space-y-6
                "
            >

                <span
                    className="
                    inline-flex
                    items-center
                    rounded-full
                    bg-red-50
                    text-red-700
                    text-xs
                    font-semibold
                    tracking-wide
                    uppercase
                    px-3
                    py-1
                    "
                    >
                    Anomaly AI
                </span>

                <h1
                    className="
                    text-[30px]
                    font-bold
                    tracking-tight
                    text-[#101828]"
                >
                    Modul AI Deteksi Anomali
                </h1>

                <p
                className="
                mt-3
                max-w-3xl
                text-[15px]
                leading-7
                text-[#667085]"
                >
                    Mendeteksi data yang menyimpang dari pola umum menggunakan Artificial Intelligence untuk membantu proses validasi kualitas dataset Satu Data Aceh.
                </p>

                <div
                    className="
                    pt-2
                    flex
                    gap-3
                    items-end
                    max-w-4xl"
                    >

                    <div className="w-[680px]">
                        <DatasetSelector
                            datasets={datasets}
                            selected={selected}
                            search={datasetSearch}
                            setSearch={setDatasetSearch}
                            onSelect={handleSelectDataset}
                            showSuggestion={showSuggestion}
                            setShowSuggestion={setShowSuggestion}
                            inputRef={inputRef}
                        />
                    </div>

                    <button
                        onClick={handleAnalyze}
                        disabled={loading}
                        className="
                        h-[44px]
                        px-5
                        rounded-xl
                        border
                        border-[#D92D20]
                        bg-white
                        text-[#D92D20]
                        text-sm
                        transition
                        hover:bg-[#D92D20]
                        hover:text-white
                        disabled:opacity-50
                        "
                    >
                        {loading ? (
                            <span className="flex items-center gap-2">
                                <span
                                    className="
                                    w-4
                                    h-4
                                    border-2
                                    border-white
                                    border-t-transparent
                                    rounded-full
                                    animate-spin"
                                />
                                Menganalisis...
                            </span>
                        ) : (
                            "Analisis"
                        )}
                    </button>
                </div>
            </section>
            
            {/* ========================== */}
            {/* Result */}
            {/* ========================== */}

            {
                !result && !loading && (
                    <section className="py-10">
                        <h2
                            className="
                            text-lg
                            font-semibold
                            text-[#101828]
                            mb-8"
                        >
                            Bagaimana AI Membantu
                        </h2>

                        <div
                            className="
                            flex
                            items-start
                            justify-between
                            gap-4"
                        >

                            {/* STEP 1 */}
                            <div className="flex-1 text-center">
                                <div
                                    className="
                                    w-10
                                    h-10
                                    mx-auto
                                    rounded-full
                                    bg-[#FEECEC]
                                    text-[#B42318]
                                    flex
                                    items-center
                                    justify-center
                                    font-semibold"
                                >
                                    1
                                </div>
                                <h3 className="mt-4 text-sm font-semibold text-[#101828]">
                                    Pilih Dataset
                                </h3>
                                <p className="mt-2 text-xs leading-5 text-gray-500">
                                    Cari dataset dari Portal Satu Data Aceh.
                                </p>
                            </div>

                            <div className="flex-1 h-px bg-gray-200 mt-5"></div>
                            {/* STEP 2 */}
                            <div className="flex-1 text-center">
                                <div
                                    className="
                                    w-10
                                    h-10
                                    mx-auto
                                    rounded-full
                                    bg-[#FEECEC]
                                    text-[#B42318]
                                    flex
                                    items-center
                                    justify-center
                                    font-semibold"
                                >
                                    2
                                </div>
                                <h3 className="mt-4 text-sm font-semibold text-[#101828]">
                                    Analisis AI
                                </h3>
                                <p className="mt-2 text-xs leading-5 text-gray-500">
                                    AI mempelajari pola numerik pada dataset.
                                </p>
                            </div>

                            <div className="flex-1 h-px bg-gray-200 mt-5"></div>
                            {/* STEP 3 */}
                            <div className="flex-1 text-center">
                                <div
                                    className="
                                    w-10
                                    h-10
                                    mx-auto
                                    rounded-full
                                    bg-[#FEECEC]
                                    text-[#B42318]
                                    flex
                                    items-center
                                    justify-center
                                    font-semibold"
                                >
                                    3
                                </div>
                                <h3 className="mt-4 text-sm font-semibold text-[#101828]">
                                    Deteksi
                                </h3>
                                <p className="mt-2 text-xs leading-5 text-gray-500">
                                    AI menemukan data yang menyimpang.
                                </p>
                            </div>

                            <div className="flex-1 h-px bg-gray-200 mt-5"></div>
                            {/* STEP 4 */}
                            <div className="flex-1 text-center">
                                <div
                                    className="
                                    w-10
                                    h-10
                                    mx-auto
                                    rounded-full
                                    bg-[#FEECEC]
                                    text-[#B42318]
                                    flex
                                    items-center
                                    justify-center
                                    font-semibold"
                                >
                                    4
                                </div>
                                <h3 className="mt-4 text-sm font-semibold text-[#101828]">
                                    Insight
                                </h3>
                                <p className="mt-2 text-xs leading-5 text-gray-500">
                                    Ringkasan dan rekomendasi dibuat otomatis.
                                </p>
                            </div>
                        </div>
                        </section>
                )
            }
            {
                result && (
                    <>
                        <div
                            className="
                            bg-white
                            rounded-3xl
                            border
                            border-gray-200
                            p-8
                        "
                        >
                        <DatasetInfo
                            dataset={result.dataset}
                        />

                        {/* Summary */}
                        <div className="mt-8">
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">

                                <SummaryCard
                                    icon="database"
                                    title="Total Data"
                                    value={result.summary.rows}
                                    badge="Baris dianalisis"
                                    badgeColor="gray"
                                />

                                <SummaryCard
                                    icon="normal"
                                    title="Data Normal"
                                    value={result.summary.normal_count}
                                    badge={`${(
                                        100 - result.summary.anomaly_percentage
                                    ).toFixed(1)}%`}
                                    badgeColor="green"
                                />

                                <SummaryCard
                                    icon="anomaly"
                                    title="Data Anomali"
                                    value={result.summary.anomaly_count}
                                    badge={`${result.summary.anomaly_percentage}%`}
                                    badgeColor="red"
                                />

                                <SummaryCard
                                    icon="risk"
                                    title="Tingkat Risiko"
                                    value={risk}
                                    badge={risk}
                                    badgeColor={color}
                                />

                            </div>
                        </div>
                        </div>

                        <div
                            className="
                            mt-10
                            bg-white
                            rounded-3xl
                            border
                            border-gray-200
                            p-8"
                        >

                            <HorizontalChart
                                rows={chartRows}
                            />
                        </div>

                        <div
                            className="
                            mt-8
                            grid
                            grid-cols-1
                            lg:grid-cols-2
                            gap-6"
                        >

                            <div
                                className="
                                bg-white
                                rounded-3xl
                                border
                                border-gray-200
                                p-8"
                            >
                                <InsightCard
                                    insight={result.insight}
                                />
                            </div>

                            <div
                                className="
                                bg-white
                                rounded-3xl
                                border
                                border-gray-200
                                p-8"
                            >
                                <RecommendationCard
                                    recommendation={result.recommendation}
                                />
                            </div>

                        </div>
                        <div className="mt-12"></div>

                        {/* Filter */}
                        <>
                            <div
                                className="
                                bg-white
                                border
                                border-gray-200
                                rounded-2xl
                                p-5
                                mb-6"
                            >

                                <div
                                    className="
                                    flex
                                    flex-col
                                    lg:flex-row
                                    lg:items-center
                                    lg:justify-between
                                    gap-4"
                                >
                                <div>
                                    <h2
                                        className="
                                        text-lg
                                        font-semibold
                                        text-gray-900"
                                    >
                                        Data Anomali
                                    </h2>

                                    <p
                                        className="
                                        text-sm
                                        text-gray-500
                                        mt-1"
                                    >
                                        {filteredRows.length} data terdeteksi
                                    </p>

                                </div>

                                <div
                                    className="
                                    flex
                                    flex-col
                                    md:flex-row
                                    gap-3"
                                >

                                    <input
                                        type="text"
                                        placeholder="Cari Kabupaten/Kota"
                                        value={tableSearch}
                                        onChange={(e)=>{
                                            setTableSearch(e.target.value);
                                            setCurrentPage(1);
                                        }}
                                        className="
                                            border
                                            border-gray-200
                                            rounded-lg
                                            px-4
                                            py-2
                                            w-72
                                            focus:outline-none
                                            focus:ring-1
                                            focus:ring-gray-300"
                                    />

                                    <select
                                        value={severity}
                                        onChange={(e)=>setSeverity(e.target.value)}
                                        className="
                                            border
                                            border-gray-200
                                            rounded-lg
                                            px-4
                                            py-2
                                            focus:outline-none
                                            focus:ring-1
                                            focus:ring-gray-300"
                                    >

                                        <option>Semua</option>
                                        <option>Tinggi</option>
                                        <option>Sedang</option>
                                        <option>Rendah</option>

                                    </select>
                                </div>
                            </div>
                            </div>

                            <AnomalyTable
                                rows={currentRows}
                                startIndex={startIndex}
                            />

                            {
                                filteredRows.length > 0 && (

                                    <div
                                        className="
                                        flex
                                        justify-center
                                        items-center
                                        gap-5
                                        mt-8
                                        text-sm"
                                    >

                                        {/* Previous */}
                                        <button
                                            disabled={currentPage===1}
                                            onClick={()=>setCurrentPage(currentPage-1)}
                                            className="
                                            text-gray-400
                                            hover:text-gray-700
                                            disabled:opacity-30
                                            transition"
                                        >
                                            &lt;
                                        </button>

                                        {
                                            Array.from(
                                                { length: totalPages },
                                                (_, i) => i + 1
                                            ).map(page=>(

                                                <button
                                                    key={page}
                                                    onClick={()=>setCurrentPage(page)}
                                                    className={`
                                                        transition
                                                        ${
                                                            currentPage===page
                                                            ? "text-[#101828] font-semibold border-b-2 border-[#101828] pb-0.5"
                                                            : "text-gray-400 hover:text-gray-700"
                                                        }
                                                    `}
                                                >
                                                    {page}
                                                </button>

                                            ))
                                        }

                                        {/* Next */}
                                        <button
                                            disabled={currentPage===totalPages}
                                            onClick={()=>setCurrentPage(currentPage+1)}
                                            className="
                                            text-gray-400
                                            hover:text-gray-700
                                            disabled:opacity-30
                                            transition"
                                        >
                                            &gt;
                                        </button>

                                    </div>

                                )
                                }
                        </>
                    </>
                )
            }
            </main>
        </div>
    );
}