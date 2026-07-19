import {
    LayoutDashboard,
    ShieldAlert,
    MessageCircle,
    FileText,
    TrendingUp,
    Info,
    PanelLeftClose,
    PanelLeftOpen
} from "lucide-react";

export default function Sidebar({
    open,
    setOpen
}) {

    return (

        <aside
            className={`
                bg-white
                border-r
                border-gray-200
                min-h-screen
                transition-all
                duration-300
                ${
                    open
                        ? "w-72 p-6"
                        : "w-20 p-4"
                }
            `}
        >
            <div className="flex justify-end mb-6">
                <button
                    onClick={() => setOpen(!open)}
                    className="
                    p-2
                    rounded-lg
                    hover:bg-gray-100
                    transition"
                >
                    {
                        open
                        ? <PanelLeftClose size={20}/>
                        : <PanelLeftOpen size={20}/>
                    }
                </button>
            </div>

            <div
                className={`
                    mb-10
                    ${
                        open
                        ? ""
                        : "flex justify-center"
                    }
                `}
            >
                <h1
                    className="
                    text-2xl
                    font-bold
                    text-[#FF0000]"
                >
                    SADA-AI
                </h1>
                {
                    open &&
                    (
                        <p
                            className="
                            text-sm
                            text-gray-500
                            mt-1"
                        >
                            Portal AI Satu Data Aceh
                        </p>
                    )
                }
            </div>

            <button
                className={`
                    group
                    flex
                    items-center
                    gap-3
                    w-full
                    py-3
                    rounded-xl
                    transition
                    hover:bg-red-50
                    hover:text-[#FF0000]
                    ${
                        open
                            ? "px-4"
                            : "justify-center"
                    }
                `}
            >
                <LayoutDashboard size={20}/>
                    {
                        open &&
                        "Dashboard"
                    }
            </button>
            {
                open &&
                <p
                    className="
                        text-xs
                        uppercase
                        tracking-widest
                        text-gray-400
                        mt-8
                        mb-3
                        px-2"
                    >
                        AI Modules
                </p>
            }
            <button
                className={`
                    group
                    flex
                    items-center
                    gap-3
                    w-full
                    py-3
                    rounded-xl
                    transition
                    hover:bg-red-50
                    hover:text-[#FF0000]
                    ${
                        open
                            ? "px-4"
                            : "justify-center"
                    }
                `}
                >
                <MessageCircle size={20}/>
                {
                    open &&
                    "Statistical Q&A"
                }
            </button>
            <button
                className={`
                    group
                    flex
                    items-center
                    gap-3
                    w-full
                    py-3
                    rounded-xl
                    transition
                    hover:bg-red-50
                    hover:text-[#FF0000]
                    ${
                        open
                            ? "px-4"
                            : "justify-center"
                    }
                `}
                >
                <FileText size={20}/>
                {
                    open &&
                    "Report Summarizer"
                }
            </button>
            <button
                className={`
                    group
                    flex
                    items-center
                    gap-3
                    w-full
                    py-3
                    rounded-xl
                    transition
                    hover:bg-red-50
                    hover:text-[#FF0000]
                    ${
                        open
                            ? "px-4"
                            : "justify-center"
                    }
                `}
                >
                <TrendingUp size={20}/>
                {
                    open &&
                    "Trend Prediction"
                }
            </button>
            <button
                className={`
                    group
                    flex
                    items-center
                    gap-3
                    w-full
                    py-3
                    rounded-xl
                    transition
                    hover:bg-red-50
                    hover:text-[#FF0000]
                    ${
                        open
                            ? "px-4"
                            : "justify-center"
                    }
                `}
                >
                <ShieldAlert size={20}/>
                {
                    open &&
                    "Deteksi Anomali"
                }
            </button>
        </aside>
    );
}