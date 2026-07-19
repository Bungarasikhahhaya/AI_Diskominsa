export default function AnomalyTable({
    rows,
    startIndex = 0
}) {

    if (!rows || rows.length === 0) {
        return (
            <div
                id="anomaly-table"
                className="
                bg-white
                rounded-2xl
                shadow
                p-10
                hover:shadow-lg
                transition-all
                duration-300
                text-center"
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
            shadow
            p-6"
        >
            <div
                className="w-full"
            >
                <table
                    className="
                    w-full
                    border-collapse"
                >
                    <thead className="sticky top-0 z-10 bg-[#FF0000] text-white">
                        <tr>
                            <th className="p-3 text-left">
                                No
                            </th>

                            <th className="p-3">
                                Baris
                            </th>

                            <th className="p-3 text-left">
                                Kabupaten/Kota
                            </th>

                            <th className="p-3 text-left">
                                {indicatorName}
                            </th>

                            <th
                                className="p-3 text-left"
                                title="Prioritas menunjukkan tingkat penyimpangan data"
                            >
                                Prioritas
                            </th>

                            <th
                                className="p-3 text-left"
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
                                        hover:bg-gray-50
                                        transition"
                                    >

                                        {/* Nomor */}
                                        <td className="p-3">
                                            {startIndex + index + 1}
                                        </td>

                                        {/* Nomor Baris Dataset Asli */}
                                        <td className="p-3">
                                            {row.row_number}
                                        </td>

                                        {/* Kabupaten */}
                                        <td className="p-3">
                                                {namaKabupaten}
                                        </td>

                                        {/* Nilai indikator */}
                                        <td className="p-3 font-medium">
                                            {row.indicator_value}
                                        </td>

                                        {/* Severity */}
                                        <td className="p-3">
                                            {
                                                row.severity === "Tinggi" ? (

                                                    <span className="inline-flex items-center gap-2 bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm font-semibold">
                                                        🔴 Tinggi
                                                    </span>

                                                ) : row.severity === "Sedang" ? (

                                                    <span className="inline-flex items-center gap-2 bg-yellow-100 text-yellow-700 px-3 py-1 rounded-full text-sm font-semibold">
                                                        🟡 Sedang
                                                    </span>

                                                ) : row.severity === "Rendah" ? (

                                                    <span className="inline-flex items-center gap-2 bg-green-100 text-green-700 px-3 py-1 rounded-full text-sm font-semibold">
                                                        🟢 Rendah
                                                    </span>

                                                ) : (

                                                    <span className="inline-flex items-center gap-2 bg-gray-100 text-gray-500 px-3 py-1 rounded-full text-sm">
                                                        -
                                                    </span>

                                                )
                                            }
                                        </td>

                                        {/* Score */}
                                        <td
                                            className={`p-3 font-semibold ${
                                                row.score < -0.25
                                                    ? "text-red-600"
                                                    : row.score < -0.10
                                                    ? "text-yellow-600"
                                                    : "text-green-600"
                                            }`}
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