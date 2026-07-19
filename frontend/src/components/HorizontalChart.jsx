import {
    ResponsiveContainer,
    BarChart,
    Bar,
    XAxis,
    YAxis,
    Tooltip,
    LabelList
} from "recharts";
import { Cell } from "recharts";

export default function HorizontalChart({ 
    rows = [],
    severity,
    onSeverityChange
 }) {
    // ===============================
    // Tidak ada data
    // ===============================

    if (!rows || rows.length === 0) {
        return (
            <div
                className="
                bg-white
                rounded-2xl
                shadow
                hover:shadow-lg
                hover:-translate-y-1
                transition-all
                duration-300
                p-6"
            >
                <h3 className="text-lg font-bold mb-6">
                    Distribusi Anomali
                </h3>

                <div
                    className="
                    h-[420px]
                    flex
                    items-center
                    justify-center
                    text-gray-400"
                >
                    Belum ada data.
                </div>
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
        .map((item) => {
            let dominant = "Rendah";

            if (item.tinggi >= item.sedang &&
                item.tinggi >= item.rendah)
                dominant = "Tinggi";

            else if (item.sedang >= item.rendah)
                dominant = "Sedang";

            return {
                ...item,
                dominant,
                color:
                    dominant === "Tinggi"
                        ? "#DC2626"
                        : dominant === "Sedang"
                        ? "#F59E0B"
                        : "#22C55E"
            };
        })
        .sort((a,b)=>{
            if(b.total!==a.total)
                return b.total-a.total;
            if(b.tinggi!==a.tinggi)
                return b.tinggi-a.tinggi;
            if(b.sedang!==a.sedang)
                return b.sedang-a.sedang;
            return a.nama.localeCompare(b.nama);
        });
        const chartHeight = Math.max(
            500,
            chartData.length * 25
        );

    // ===============================
    // UI
    // ===============================

    return (
        <div
            className="
            bg-white
            rounded-2xl
            shadow
            hover:shadow-lg
            hover:-translate-y-1
            transition-all
            duration-300
            p-6"
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
                        text-[#1A1A1B]"
                    >
                        Distribusi Anomali
                    </h3>
                    <p
                        className="
                        text-sm
                        text-gray-500"
                    >
                        {chartData.length} Kabupaten/Kota
                    </p>
                </div>

                <select
                    value={severity}
                    onChange={(e)=>
                        onSeverityChange(
                            e.target.value
                        )
                    }
                    className="
                    border
                    rounded-xl
                    px-3
                    py-2
                    text-sm
                    focus:outline-none
                    focus:ring-2
                    focus:ring-red-500"
                >
                    <option value="Semua">
                        Semua Severity
                    </option>
                    <option value="Tinggi">
                        Tinggi
                    </option>
                    <option value="Sedang">
                        Sedang
                    </option>
                    <option value="Rendah">
                        Rendah
                    </option>
                </select>
            </div>
            <div
                className="
                h-[500px]
                overflow-y-auto
                pr-2
                scroll-smooth"
            >
                <ResponsiveContainer
                    width="100%"
                    height={chartHeight}
                >
                    <BarChart
                        layout="vertical"
                        barSize={
                            chartData.length <= 5
                                ? 26
                                : chartData.length <= 15
                                ? 22
                                : chartData.length <= 20
                                ? 18
                                : 14
                        }
                        data={chartData}
                        barCategoryGap="10%"
                        margin={{
                            top:10,
                            right:30,
                            left:10,
                            bottom:10
                        }}
                    >

                        <XAxis
                            type="number"
                            allowDecimals={false}
                            tickCount={6}
                        />

                        <YAxis
                            type="category"
                            dataKey="nama"
                            width={120}
                        />

                        <Tooltip
                            content={({active,payload})=>{
                                if(!active || !payload || !payload.length)
                                    return null;
                                const data = payload[0].payload;
                                return(
                                    <div
                                        className="
                                        bg-white
                                        border
                                        rounded-xl
                                        shadow-lg
                                        p-4
                                        text-sm"
                                    >
                                        <p className="font-semibold mb-2">
                                            {data.nama}
                                        </p>
                                        <p>
                                            Total Anomali: <strong>{data.total}</strong>
                                            </p>
                                            {
                                            severity === "Semua"
                                            ? (
                                                <>
                                                    <p className="text-red-600">Tinggi: {data.tinggi}</p>
                                                    <p className="text-yellow-600">Sedang: {data.sedang}</p>
                                                    <p className="text-green-600">Rendah: {data.rendah}</p>
                                                </>
                                            )
                                            : (
                                                <p>
                                                    Severity: <strong>{severity}</strong>
                                                </p>
                                            )
                                            }
                                    </div>
                                );
                            }}
                        />

                        <Bar
                            dataKey="total"
                            radius={[0, 8, 8, 0]}
                        >
                            <LabelList
                                dataKey="total"
                                position="right"
                            />
                            {chartData.map((entry, index) => (
                                <Cell
                                    key={index}
                                    fill={
                                        severity==="Tinggi"
                                        ? "#DC2626"
                                        :
                                        severity==="Sedang"
                                        ? "#F59E0B"
                                        :
                                        severity==="Rendah"
                                        ? "#22C55E"
                                        :
                                        entry.color
                                        }
                                />
                            ))}
                        </Bar>
                    </BarChart>

                </ResponsiveContainer>
            </div>
        </div>
    );
}
