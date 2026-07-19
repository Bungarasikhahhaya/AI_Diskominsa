import { Database, ShieldCheck, TriangleAlert, Activity } from "lucide-react";

export default function SummaryCard({
    title,
    value,
    badge,
    badgeColor = "gray",
    icon,
}) {

    const badgeStyle = {
        red: "bg-red-100 text-red-700",
        yellow: "bg-yellow-100 text-yellow-700",
        green: "bg-green-100 text-green-700",
        gray: "bg-gray-100 text-gray-700"
    };

    const icons = {
        database: <Database size={18} />,
        normal: <ShieldCheck size={18} />,
        anomaly: <TriangleAlert size={18} />,
        risk: <Activity size={18} />
    };

    return (
        <div
            className="
            bg-white
            rounded-2xl
            shadow-sm
            hover:shadow-lg
            transition-all
            duration-300
            p-5
            flex
            flex-col
            justify-between
            min-h-[140px]
        "
        >

            {/* Header */}
            <div className="flex items-center gap-2 text-gray-500">
                {icons[icon]}
                <span
                    className="
                    text-sm
                    font-medium
                "
                >
                    {title}
                </span>
            </div>

            {/* Value */}
            <div className="mt-3">
                <h2
                    className="
                    text-3xl
                    font-bold
                    text-[#1A1A1B]
                "
                >
                    {value}
                </h2>
            </div>

            {/* Badge */}
            <div className="mt-3">
                {
                    badge &&
                    (
                        <span
                            className={`
                            inline-flex
                            items-center
                            whitespace-nowrap
                            rounded-full
                            px-4
                            py-2
                            text-sm
                            font-semibold
                            ${badgeStyle[badgeColor]}
                        `}
                        >
                            {badge}
                        </span>
                    )
                }
            </div>
        </div>
    );
}