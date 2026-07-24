import { useEffect, useMemo, useRef, useState } from "react";
import {
    Activity,
    ArrowLeft,
    Database,
    Lightbulb,
    ListChecks,
    Search,
    ShieldCheck,
    TriangleAlert
} from "lucide-react";
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
            <Search
                size={17}
                className="absolute left-4 top-1/2 -translate-y-1/2 text-[#B42318]"
            />
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
                border-[#D9E1EA]
                bg-white
                pl-11
                pr-4
                text-base
                placeholder:text-[#98A2B3]
                focus:ring-2
                focus:ring-[#FECACA]
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
                    border-[#D9E1EA]
                    rounded-lg
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
                                        border-[#F1F3F6]
                                        last:border-b-0
                                        hover:bg-[#FFF7F7]
                                        transition
                                        ${
                                            selected === dataset.identifier
                                                ? "bg-[#FFF1F1]"
                                                : ""
                                        }
                                    `}
                                >
                                    <div className="font-semibold text-[#101828]">
                                        {dataset.title}
                                    </div>
                                    <div className="text-[15px] text-gray-500">
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
            border-[#D9E1EA]
            p-4
            py-4"
        >

            <div
                className="
                flex
                items-center
                gap-2
                text-[#5B6B82]
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
                    text-[15px]
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
                    <p className="text-[15px] text-[#667085]">
                        Sumber Data
                    </p>
                    <p className="font-medium mt-1">
                        {dataset.publisher || "-"}
                    </p>
                </div>

                <div>
                    <p className="text-[15px] text-[#667085]">
                        Tahun Data
                    </p>
                    <p className="font-medium mt-1">
                        {dataset.year || "-"}
                    </p>
                </div>

                <div>
                    <p className="text-[15px] text-[#667085]">
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
        <div className="flex h-full flex-col">
            <h3
                className="
                flex
                items-center
                gap-2
                text-lg
                font-bold
                text-[#101828]"
            >
                <Lightbulb size={19} className="text-[#C56A36]" />
                Ringkasan Analisis AI
            </h3>

            <p
                className="
                mt-3
                text-[15px]
                leading-7
                text-[#667085]"
            >
                {insight.summary}
            </p>

            <div className="border-t border-[#E4E7EC] my-3"/>

            <h4
                className="
                text-sm
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
                                text-[15px]
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
        <div className="flex h-full flex-col">
            <h3
                className="
                flex
                items-center
                gap-2
                text-lg
                font-bold
                text-[#101828]
                "
            >
                <ListChecks size={19} className="text-[#5F87A6]" />
                Rekomendasi AI
            </h3>

            <p
                className="
                text-[#667085]
                text-[15px]
                leading-7
                mt-3"
            >
                Prioritas tindakan yang disarankan AI berdasarkan pola anomali yang ditemukan.
            </p>

            <div className="border-t border-[#E4E7EC] my-3"/>

            <h4
                className="
                text-sm
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
                                    
                                    text-[15px]
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
                    text-base
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
        360,
        chartData.length * 36
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
                        text-base
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
                            right:28,
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
                            width={170}
                            interval={0}
                            axisLine={false}
                            tickLine={false}
                            tick={{
                            fill:"#344054",
                            fontSize:14
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
                border-[#D9E1EA]
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
            overflow-x-auto"
        >
            <div
                className="w-full"
            >
                <table
                    className="
                    w-full
                    text-[15px]"
                >
                    <thead
                        className="
                        sticky
                        top-0
                        bg-[#F1F5F9]
                        text-[#52627A]
                        shadow-[0_0_0_1px_#D9E1EA]
                        "
                    >
                        <tr className="border-b border-[#D9E1EA]">
                            <th className="w-14 px-4 py-2 text-left text-sm font-semibold uppercase tracking-wide">
                                No
                            </th>

                            <th className="w-20 px-4 py-2 text-left text-sm font-semibold uppercase tracking-wide">
                                Baris
                            </th>

                            <th className="px-4 py-2 text-left text-sm font-semibold uppercase tracking-wide">
                                Kabupaten/Kota
                            </th>

                            <th className="px-4 py-2 text-left text-sm font-semibold uppercase tracking-wide">
                                {indicatorName}
                            </th>

                            <th
                                className="w-32 px-4 py-2 text-left text-sm font-semibold uppercase tracking-wide"
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
                                text-sm
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
                                        border-[#EEF2F6]
                                        hover:bg-[#FCFCFD]
                                        transition-colors"
                                    >

                                        {/* Nomor */}
                                        <td className="px-4 py-2 text-sm text-gray-400">
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

                                                    <span className="inline-flex items-center gap-2 bg-[#FEE2E2] text-[#B42318] px-2 py-0.5 rounded-full text-sm font-medium">
                                                        Tinggi
                                                    </span>

                                                ) : row.severity === "Sedang" ? (

                                                    <span className="inline-flex items-center gap-2 bg-[#FEF3C7] text-[#B45309] px-2 py-0.5 rounded-full text-sm font-medium">
                                                        Sedang
                                                    </span>

                                                ) : row.severity === "Rendah" ? (

                                                    <span className="inline-flex items-center gap-2 bg-[#DCFCE7] text-[#15803D] px-2 py-0.5 rounded-full text-sm font-medium">
                                                        Rendah
                                                    </span>

                                                ) : (

                                                    <span className="inline-flex items-center gap-2 bg-gray-100 text-gray-500 px-2 py-0.5 rounded-full text-sm">
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
    const [validationModal, setValidationModal] = useState(null);

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
            setValidationModal({
                title: "Dataset Belum Dipilih",
                message: "Pilih dataset terlebih dahulu sebelum memulai analisis.",
                reasons: []
            });
            return;
        }

        setLoading(true);

        try {
            const data = await analyzeDataset(selected);

            if (!data) {
                setResult(null);
                setValidationModal({
                    title: "Dataset Belum Siap Dianalisis",
                    message: "Dataset ini belum memenuhi persyaratan minimum untuk analisis.",
                    reasons: ["Data yang diperlukan belum tersedia atau belum dapat diproses."]
                });
                return;
            }

            if (
                !Array.isArray(data?.anomaly?.all)
                || !data?.summary
            ) {
                setResult(null);
                setCurrentPage(1);
                setSeverity("Semua");
                setTableSearch("");

                const validationErrors = Array.isArray(
                    data?.validation?.errors
                )
                    ? data.validation.errors.join(" ")
                    : "Struktur data belum memenuhi persyaratan analisis ML.";

                setValidationModal({
                    title: "Dataset Belum Siap Dianalisis",
                    message: "Dataset ini belum memenuhi persyaratan minimum untuk analisis.",
                    reasons: validationErrors
                        .split(".")
                        .map(reason => reason.trim())
                        .filter(Boolean)
                });
                return;
            }

            setResult(data);
            setCurrentPage(1);
        }
        catch (err) {
            console.error(err);
            setResult(null);
            setValidationModal({
                title: "Analisis Belum Selesai",
                message: "Dataset belum dapat dianalisis saat ini.",
                reasons: ["Periksa kembali dataset dan coba lagi."]
            });
        }
        finally {
            setLoading(false);
        }
    };

    // ==========================
    // Filter Table
    // ==========================

    const filteredRows = useMemo(() => {
        if (!result || !Array.isArray(result.anomaly?.all)) return [];
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
        if (!result || !Array.isArray(result.anomaly?.all)) return [];

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
            bg-[#F7F9FC]
            bg-[radial-gradient(#DDE5EE_0.7px,transparent_0.7px)]
            bg-[size:18px_18px]
            font-sans
            tracking-[0.01em]
            px-5
            py-6
            sm:px-8
            lg:px-10"
        >
            <main
                className="
                max-w-[1180px]
                mx-auto
                space-y-7"
            >

            {/* ========================== */}
            {/* Analyze Card */}
            {/* ========================== */}

            <section
                className="
                relative
                overflow-hidden
                bg-[radial-gradient(circle_at_100%_0%,rgba(254,226,226,0.72),transparent_35%),linear-gradient(125deg,#FFFFFF_0%,#FFFFFF_66%,#FFF8F8_100%)]
                border
                border-[#D9E1EA]
                rounded-2xl
                p-6
                shadow-[0_8px_24px_rgba(16,24,40,0.04)]
                space-y-5
                sm:p-8
                "
            >

                <div
                    aria-hidden="true"
                    className="
                    pointer-events-none
                    absolute
                    right-4
                    top-4
                    hidden
                    h-40
                    w-48
                    opacity-40
                    sm:block"
                >
                    <div className="absolute inset-x-0 bottom-5 h-px bg-gradient-to-r from-transparent via-[#E7A5A0] to-transparent" />
                    <div className="absolute bottom-5 right-2 flex h-36 items-end gap-2">
                        <div className="h-10 w-3 rounded-t-sm bg-gradient-to-t from-[#B42318] to-[#F4B2AD]" />
                        <div className="h-20 w-3 rounded-t-sm bg-gradient-to-t from-[#B42318] to-[#F4B2AD]" />
                        <div className="h-14 w-3 rounded-t-sm bg-gradient-to-t from-[#B42318] to-[#F4B2AD]" />
                        <div className="h-28 w-3 rounded-t-sm bg-gradient-to-t from-[#B42318] to-[#F4B2AD]" />
                        <div className="h-24 w-3 rounded-t-sm bg-gradient-to-t from-[#B42318] to-[#F4B2AD]" />
                        <div className="h-32 w-3 rounded-t-sm bg-gradient-to-t from-[#B42318] to-[#F4B2AD]" />
                    </div>
                    <div className="absolute right-0 top-1 h-24 w-24 rounded-full border border-[#E7A5A0]/40" />
                </div>

                <span
                    className="
                    relative
                    z-10
                    inline-flex
                    items-center
                    rounded-full
                    bg-[#FFF1F1]
                    text-[#B42318]
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
                    relative
                    z-10
                    text-[28px]
                    font-bold
                    tracking-tight
                    text-[#111827]"
                >
                    Modul AI Deteksi Anomali
                </h1>

                <p
                className="
                relative
                z-10
                mt-3
                max-w-[42rem]
                text-[15px]
                leading-7
                text-[#5B6B82]"
                >
                    Identifikasi data yang menyimpang dari pola umum untuk membantu validasi kualitas dataset Satu Data Aceh.
                </p>

                <div
                    className="
                    relative
                    z-10
                    pt-2
                    flex
                    gap-3
                    items-stretch
                    flex-col
                    max-w-4xl
                    sm:flex-row
                    sm:items-end"
                    >

                    <div className="w-full sm:w-[680px]">
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
                        border-[#D40000]
                        bg-[#D40000]
                        text-white
                        text-base
                        font-semibold
                        shadow-[0_5px_12px_rgba(212,0,0,0.18)]
                        transition
                        hover:bg-[#B80000]
                        hover:border-[#B80000]
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
                    <section className="relative overflow-hidden rounded-2xl bg-white/35 px-3 py-5 sm:px-5 sm:py-8">
                        <h2
                            className="
                            relative
                            z-10
                            text-lg
                            font-semibold
                            text-[#111827]
                            mb-8"
                        >
                            Bagaimana AI Membantu
                        </h2>

                        <div
                            className="
                            relative
                            z-10
                            rounded-xl
                            bg-gradient-to-r
                            from-white/20
                            via-[#FFF8F8]/55
                            to-white/20
                            px-2
                            py-4
                            grid
                            grid-cols-1
                            gap-5
                            md:grid-cols-[1fr_auto_1fr_auto_1fr_auto_1fr]
                            md:items-start
                            md:px-4"
                        >

                            {/* STEP 1 */}
                            <div className="flex-1 text-center">
                                <div
                                    className="
                                    w-10
                                    h-10
                                    mx-auto
                                    rounded-full
                                    bg-[#FFF1F1]
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

                            <div className="hidden md:block w-10 h-px bg-gradient-to-r from-[#E7A5A0] to-[#F1D8D6] mt-5"></div>
                            {/* STEP 2 */}
                            <div className="flex-1 text-center">
                                <div
                                    className="
                                    w-10
                                    h-10
                                    mx-auto
                                    rounded-full
                                    bg-[#FFF1F1]
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

                            <div className="hidden md:block w-10 h-px bg-gradient-to-r from-[#E7A5A0] to-[#F1D8D6] mt-5"></div>
                            {/* STEP 3 */}
                            <div className="flex-1 text-center">
                                <div
                                    className="
                                    w-10
                                    h-10
                                    mx-auto
                                    rounded-full
                                    bg-[#FFF1F1]
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

                            <div className="hidden md:block w-10 h-px bg-gradient-to-r from-[#E7A5A0] to-[#F1D8D6] mt-5"></div>
                            {/* STEP 4 */}
                            <div className="flex-1 text-center">
                                <div
                                    className="
                                    w-10
                                    h-10
                                    mx-auto
                                    rounded-full
                                    bg-[#FFF1F1]
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
                            bg-white/95
                            rounded-2xl
                            border
                            border-[#D9E1EA]
                            p-6
                            shadow-[0_8px_24px_rgba(16,24,40,0.04)]
                            sm:p-8
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
                            grid
                            grid-cols-1
                            gap-6
                            lg:grid-cols-[minmax(0,1.35fr)_minmax(360px,0.9fr)]
                            lg:items-stretch"
                        >
                        <div
                            className="
                            h-full
                            bg-white/95
                            rounded-2xl
                            border
                            border-[#D9E1EA]
                            p-6
                            shadow-[0_8px_24px_rgba(16,24,40,0.04)]
                            sm:p-8"
                        >

                            <HorizontalChart
                                rows={chartRows}
                            />
                        </div>

                        <div
                            className="
                            flex
                            flex-col
                            gap-6"
                        >

                            <div
                                className="
                                flex-1
                                bg-white
                                rounded-2xl
                                border
                                border-[#D9E1EA]
                                p-6
                                shadow-[0_8px_24px_rgba(16,24,40,0.04)]
                                sm:p-8"
                            >
                                <InsightCard
                                    insight={result.insight}
                                />
                            </div>

                            <div
                                className="
                                flex-1
                                bg-white
                                rounded-2xl
                                border
                                border-[#D9E1EA]
                                p-6
                                shadow-[0_8px_24px_rgba(16,24,40,0.04)]
                                sm:p-8"
                            >
                                <RecommendationCard
                                    recommendation={result.recommendation}
                                />
                            </div>

                        </div>
                        </div>
                        <div className="mt-12"></div>

                        {/* Filter */}
                        <>
                            <div
                                className="
                                bg-white
                                border
                                border-[#D9E1EA]
                                rounded-xl
                                shadow-[0_5px_18px_rgba(16,24,40,0.03)]
                                overflow-hidden
                                mb-6"
                            >

                                <div
                                    className="
                                    px-5
                                    py-5
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
                                        text-[#111827]"
                                    >
                                        Data Anomali
                                    </h2>

                                    <p
                                        className="
                                        text-[15px]
                                        text-[#5B6B82]
                                        mt-1"
                                    >
                                        {filteredRows.length} data anomali terdeteksi dalam dataset
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
                                            border-[#D9E1EA]
                                            rounded-lg
                                            px-4
                                            py-2
                                            w-72
                                            text-base
                                            focus:outline-none
                                            focus:ring-1
                                            focus:ring-[#FECACA]"
                                    />

                                    <select
                                        value={severity}
                                        onChange={(e)=>setSeverity(e.target.value)}
                                        className="
                                            border
                                            border-[#D9E1EA]
                                            rounded-lg
                                            px-4
                                            py-2
                                            text-base
                                            focus:outline-none
                                            focus:ring-1
                                            focus:ring-[#FECACA]"
                                    >

                                        <option>Semua</option>
                                        <option>Tinggi</option>
                                        <option>Sedang</option>
                                        <option>Rendah</option>

                                    </select>
                                </div>
                            </div>

                            <AnomalyTable
                                rows={currentRows}
                                startIndex={startIndex}
                            />
                            </div>

                            {
                                filteredRows.length > 0 && (

                                    <div
                                        className="
                                        flex
                                        justify-center
                                        items-center
                                        gap-5
                                        mt-8
                                        text-[15px]"
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

            {
                validationModal && (
                    <div
                        className="
                        fixed
                        inset-0
                        z-50
                        flex
                        items-center
                        justify-center
                        bg-[#101828]/35
                        px-5
                        py-8
                        backdrop-blur-[2px]"
                        role="presentation"
                    >
                        <div
                            className="
                            w-full
                            max-w-md
                            rounded-2xl
                            border
                            border-[#D9E1EA]
                            bg-white
                            p-6
                            shadow-[0_20px_50px_rgba(16,24,40,0.18)]
                            sm:p-7"
                            role="dialog"
                            aria-modal="true"
                            aria-labelledby="validation-modal-title"
                        >
                            <div
                                className="
                                flex
                                h-11
                                w-11
                                items-center
                                justify-center
                                rounded-xl
                                bg-[#FFF4E5]
                                text-[#B54708]"
                            >
                                <TriangleAlert size={22} />
                            </div>

                            <h2
                                id="validation-modal-title"
                                className="
                                mt-5
                                text-xl
                                font-bold
                                text-[#101828]"
                            >
                                {validationModal.title}
                            </h2>

                            <p
                                className="
                                mt-2
                                text-base
                                leading-7
                                text-[#5B6B82]"
                            >
                                {validationModal.message}
                            </p>

                            <button
                                type="button"
                                onClick={() => setValidationModal(null)}
                                className="
                                mt-7
                                ml-auto
                                block
                                rounded-lg
                                border
                                border-[#E4B7B3]
                                bg-[#FFF8F7]
                                px-4
                                py-2
                                text-sm
                                font-semibold
                                text-[#B42318]
                                transition
                                hover:bg-[#FFF1F1]
                                hover:border-[#D98A82]"
                            >
                                Tutup
                            </button>
                        </div>
                    </div>
                )
            }
        </div>
    );
}