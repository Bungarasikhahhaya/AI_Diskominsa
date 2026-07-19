import { useRef } from "react";

export default function DatasetSelector({
    datasets,
    selected,
    search,
    setSearch,
    onSelect,
    showSuggestion,
    setShowSuggestion
}) {

    const inputRef = useRef(null);

    return (
        <div className="space-y-3">
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
                    border
                    border-gray-300
                    rounded-xl
                    p-3
                    focus:outline-none
                    focus:ring-2
                    focus:ring-[#FF0000]
                "
            />
            {
                showSuggestion &&
                search.length >= 1 &&
                datasets.length > 0 && (
                    <div
                        className="
                            border
                            border-gray-200
                            rounded-xl
                            bg-white
                            shadow-sm
                            max-h-72
                            overflow-y-auto
                        "
                    >
                        {
                            datasets.map((dataset) => (
                                <div
                                    key={dataset.identifier}
                                    onMouseDown={(e) => {
                                        e.preventDefault();
                                        setShowSuggestion(false);
                                        onSelect(dataset);
                                        inputRef.current?.blur();
                                    }}
                                    className={`
                                        p-3
                                        cursor-pointer
                                        border-b
                                        last:border-b-0
                                        hover:bg-red-50
                                        transition
                                        ${
                                            selected === dataset.identifier
                                                ? "bg-red-100"
                                                : ""
                                        }
                                    `}
                                >
                                    <div className="font-semibold text-[#1A1A1B]">
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