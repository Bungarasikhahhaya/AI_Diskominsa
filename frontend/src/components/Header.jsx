export default function Header() {
    return (
        <header
            className="
            bg-white
            rounded-2xl
            shadow
            border
            border-l-4
            border-[#FF0000]
            px-8
            py-6
            flex
            items-center
            justify-between"
        >
            <div>
                <h2
                    className="
                    text-2xl
                    font-bold
                    text-[#1A1A1B]"
                >
                    Portal SADA-AI
                </h2>

                <p className="text-gray-500">
                    Platform AI untuk Analisis Data Satu Data Aceh
                </p>
            </div>
        </header>
    );
}