export default function DatasetInfo({ dataset }) {
    if (!dataset) return null;
    const formatDate = (date) => {
        if (!date) return "-";
        return new Date(date)
            .toLocaleDateString(
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
            bg-white
            rounded-2xl
            shadow
            hover:shadow-xl
            transition-all
            duration-300
            p-8"
            >
            <h2
                className="
                text-xl
                font-bold
                text-[#1A1A1B]
                mb-6"
                >
                Informasi Dataset
            </h2>
            <div>
                <p
                className="
                text-sm
                text-gray-500"
                >
                Nama Dataset
                </p>
                <p
                className="
                text-lg
                font-semibold
                leading-7
                break-words
                text-[#1A1A1B]
                mt-1"
                >
                    {dataset.title || "-"}
                </p>
            </div>
            <hr className="my-6"/>
            <div
                className="
                grid
                grid-cols-1
                md:grid-cols-3
                gap-6"
                >
                <div>
                    <p className="text-sm text-gray-500">
                        Sumber Data
                    </p>
                    <p className="font-medium mt-1">
                        {dataset.publisher || "-"}
                    </p>
                </div>
                <div>
                    <p className="text-sm text-gray-500">
                        Tahun Data
                    </p>
                    <p className="font-medium mt-1">
                        {dataset.year || "-"}
                    </p>
                </div>
                <div>
                    <p className="text-sm text-gray-500">
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