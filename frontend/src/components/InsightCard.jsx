export default function InsightCard({ insight }) {

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
                Hasil Analisis AI
            </h3>

            <div
                className="
                h-[500px]
                overflow-y-auto
                pr-3
                space-y-3"
            >

                {
                    insight.map((item,index)=>(
                        <div
                            key={index}
                            className="
                            flex
                            items-start
                            gap-4"
                        >

                            <div
                                className="
                                w-2.5
                                h-2.5
                                rounded-full
                                bg-[#FF0000]
                                mt-2
                                shrink-0"
                            />

                            <p
                                className="
                                text-[15px]
                                leading-6
                                text-gray-700"
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