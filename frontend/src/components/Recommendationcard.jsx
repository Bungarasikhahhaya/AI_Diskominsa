export default function RecommendationCard({
    recommendation
}) {
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
            p-8"
        >

            <h3
                className="
                text-xl
                font-bold
                text-[#1A1A1B]
                mb-6"
            >
                Rekomendasi AI
            </h3>

            <div className="space-y-2">
                {
                    recommendation.map((item,index)=>(
                        <div
                            key={index}
                            className="
                            flex
                            items-start
                            gap-4
                            p-2"
                        >

                            <div
                                className="
                                flex
                                items-center
                                justify-center
                                w-6
                                h-6
                                rounded-full
                                bg-green-100
                                text-green-700
                                text-sm
                                font-bold
                                shrink-0"
                            >
                                ✓
                            </div>
                            <p
                                className="
                                flex-1
                                text-gray-700
                                leading-7
                                break-words"
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