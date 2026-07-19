import { useEffect, useMemo, useRef, useState } from "react";
import DatasetSelector from "../components/DatasetSelector";
import SummaryCard from "../components/SummaryCard";
import InsightCard from "../components/InsightCard";
import RecommendationCard from "../components/RecommendationCard";
import AnomalyTable from "../components/AnomalyTable";
import LoadingSpinner from "../components/LoadingSpinner";
import DatasetInfo from "../components/DatasetInfo";
import { getDatasets, analyzeDataset } from "../api/anomalyApi";
import HorizontalChart from "../components/HorizontalChart";

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
    const [selectedRow, setSelectedRow] = useState(null);
    const [progressText, setProgressText] = useState("");
    const [topChart, setTopChart] = useState(10);
    const [chartSeverity, setChartSeverity] = useState("Semua");
    const inputRef = useRef(null);
    const [showSuggestion, setShowSuggestion] = useState(false);

    // ==========================
    // Load Dataset
    // ==========================

    useEffect(() => {
        const timer = setTimeout(() => {
            setDebouncedSearch(datasetSearch);
        },1);
        return ()=>clearTimeout(timer);
    },[datasetSearch]);

    useEffect(() => {
        if (datasetSearch.length < 1) {
            setDatasets([]);
            return;
        }
        loadDatasets();
    }, [datasetSearch]);

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
        setProgressText("Menjalankan analisis AI...");
        try {
            const data = await analyzeDataset(selected);
            setProgressText("Menyusun hasil...");

            if (!data) {
                setResult(null);
                alert("Dataset ini belum dapat dianalisis. Silakan pilih dataset lain atau gunakan dataset yang memiliki data lebih lengkap.");
                return;
            }

            setResult(data);
            setProgressText("");

            if (data.anomaly.all.length > 0) {
                setSelectedRow(data.anomaly.all[0]);
            }
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

    const handleRecommendationClick = (rowNumber) => {
        if (!rowNumber) return;
        document
            .getElementById("anomaly-table")
            ?.scrollIntoView({
                behavior: "smooth",
                block: "start"
            });

        setTimeout(() => {
            document
                .getElementById(`row-${rowNumber}`)
                ?.scrollIntoView({
                    behavior: "smooth",
                    block: "center"
                });
        }, 500);
        setTimeout(() => {
            setHighlightRow(null);
        }, 3000);
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
        let rows = result.anomaly.all.filter(
            row => row.status === "Anomali"
        );
        if (chartSeverity !== "Semua") {
            rows = rows.filter(
                row => row.severity === chartSeverity
            );
        }
        return rows;
    }, [result, chartSeverity]);

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
        
    const highRisk =
        result
            ? result.anomaly.all.filter(
                row=>row.severity==="Tinggi"
            ).length
            : 0;

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
        <div className="space-y-6">

            {/* ========================== */}
            {/* Analyze Card */}
            {/* ========================== */}

            <div
                className="
                bg-white
                rounded-2xl
                shadow
                hover:shadow-xl
                transition-all
                duration-300
                p-8"
            >

                <h1
                    className="
                    text-3xl
                    font-bold
                    text-[#1A1A1B]"
                >
                    Modul AI Deteksi Anomali
                </h1>

                <p
                    className="
                    mt-2
                    text-gray-500"
                >
                    Mendeteksi data yang menyimpang dari pola umum menggunakan Artificial Intelligence untuk membantu proses validasi kualitas dataset Satu Data Aceh.
                </p>

                <div
                    className="
                    w-24
                    h-1
                    bg-[#FF0000]
                    rounded-full
                    mt-4
                    mb-8"
                />

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

                <button
                    onClick={handleAnalyze}
                    disabled={loading}
                    className="
                    mt-6
                    bg-red-700
                    text-white
                    font-semibold
                    px-6
                    py-3
                    rounded-xl
                    transition-all
                    duration-300
                    disabled:bg-gray-400"
                >
                    {loading ? "Menganalisis..." : "Analisis Dataset"}
                </button>

            </div>
            {/* ========================== */}
            {/* Spinner */}
            {/* ========================== */}

            {
                loading &&
                <LoadingSpinner />
            }

            {
                loading &&

                <p
                className="
                text-center
                text-gray-500
                mt-4"
                >

                {progressText}

                </p>

                }

            {/* ========================== */}
            {/* Result */}
            {/* ========================== */}
            {
                result && (
                    <>
                        <DatasetInfo
                            dataset={result.dataset}
                        />

                        {/* Summary */}
                        <div className="mt-8">

                            <h2
                                className="
                                text-xl
                                font-bold
                                text-[#1A1A1B]
                                mb-5"
                            >
                                Ringkasan Analisis
                            </h2>
                            <div
                                className="
                                w-20
                                h-1
                                bg-[#FF0000]
                                rounded-full
                                mb-6"
                                />
                            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">

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
                                    ).toFixed(1)}% Normal`}
                                    badgeColor="green"
                                />

                                <SummaryCard
                                    icon="anomaly"
                                    title="Data Anomali"
                                    value={result.summary.anomaly_count}
                                    badge={`${result.summary.anomaly_percentage}% Anomali`}
                                    badgeColor="red"
                                />

                                <SummaryCard
                                    icon="risk"
                                    title="Tingkat Risiko"
                                    value={risk}
                                    badge={
                                        highRisk > 0
                                            ? `${highRisk} Anomali Tinggi`
                                            : "Tidak ada anomali tinggi"
                                    }
                                    badgeColor={color}
                                />

                            </div>
                        </div>

                        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                            <HorizontalChart
                                rows={chartRows}
                                top={topChart}
                                severity={chartSeverity}
                                onSeverityChange={setChartSeverity}
                            />

                            <InsightCard
                                insight={result.insight}
                            />
                        </div>

                        <div className="mt-6">
                            <RecommendationCard
                                recommendation={result.recommendation}
                            />
                        </div>

                        {/* Filter */}
                        <div className="bg-white rounded-2xl shadow p-6">
                            <div className="flex flex-col md:flex-row gap-4">
                                <input
                                    type="text"
                                    placeholder="Cari Kabupaten/Kota"
                                    value={tableSearch}
                                    onChange={(e) =>{
                                        setTableSearch(
                                            e.target.value
                                        );
                                        setCurrentPage(1);
                                    }}
                                    className="border rounded-xl px-4 py-2 flex-1"
                                />
                                <select
                                    value={severity}
                                    onChange={(e) => {
                                        setSeverity(e.target.value)
                                    }}
                                    className="border rounded-xl px-4 py-2"
                                >
                                    <option>Semua</option>
                                    <option>Tinggi</option>
                                    <option>Sedang</option>
                                    <option>Rendah</option>
                                </select>
                            </div>
                        </div>

                        <>
                            <div
                                className="
                                flex
                                justify-between
                                items-center
                                mb-4"
                                >
                                <h2
                                className="
                                text-xl
                                font-bold"
                                >
                                Data Anomali Terdeteksi
                                </h2>
                                <p
                                className="
                                text-gray-500"
                                >
                                Menampilkan <strong> {currentRows.length} </strong>
                                dari <strong> {filteredRows.length} </strong>
                                data anomali 
                                </p>
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
                                        justify-between
                                        items-center
                                        mt-6"
                                    >
                                        <button
                                            disabled={currentPage === 1}
                                            onClick={() =>
                                                setCurrentPage(currentPage - 1)
                                            }
                                            className="
                                            px-4
                                            py-2
                                            rounded-xl
                                            border
                                            disabled:opacity-40"
                                        >
                                            Sebelumnya
                                        </button>

                                        <span className="font-medium">
                                            Halaman {currentPage} dari {totalPages}
                                        </span>

                                        <button
                                            disabled={currentPage === totalPages}
                                            onClick={() =>
                                                setCurrentPage(currentPage + 1)
                                            }
                                            className="
                                            px-4
                                            py-2
                                            rounded-xl
                                            border
                                            disabled:opacity-40"
                                        >
                                            Berikutnya
                                        </button>
                                    </div>
                                )
                            }
                        </>
                    </>
                )
            }
        </div>
    );
}