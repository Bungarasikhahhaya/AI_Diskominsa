class RecommendationGenerator:

    def __init__(
        self,
        dataframe,
        report
    ):
        self.df = dataframe
        self.report = report

    def build(self):
        anomaly = self.df[
            self.df["anomaly"] == -1
        ]
        percentage = self.report["anomaly_percentage"]

        tinggi = (
            anomaly["severity"] == "Tinggi"
        ).sum()

        sedang = (
            anomaly["severity"] == "Sedang"
        ).sum()

        rendah = (
            anomaly["severity"] == "Rendah"
        ).sum()

        recommendation = []

        # ==========================================
        # Cari data paling ekstrem
        # ==========================================

        top = None
        if len(anomaly) > 0:
            top = anomaly.sort_values(
                by="score",
                ascending=False
            ).iloc[0]
        indicator = self.report.get("indicator")

        # ==========================================
        # 1. Kondisi umum dataset
        # ==========================================

        if percentage < 5:
            recommendation.append({
                "text":
                "Dataset memiliki tingkat penyimpangan yang rendah. Pemeriksaan dapat difokuskan pada beberapa data yang ditandai AI.",
                "row_number": None
            })
        elif percentage < 20:
            recommendation.append({
                "text":
                "Lakukan validasi terhadap data yang terdeteksi sebagai anomali sebelum dataset digunakan untuk analisis atau dipublikasikan.",
                "row_number": None
            })
        else:
            recommendation.append({
                "text":
                "Jumlah anomali relatif tinggi. Disarankan melakukan audit terhadap proses pengumpulan maupun pengolahan data sebelum dataset dipublikasikan.",
                "row_number": None
            })

        # ==========================================
        # 2. Prioritas berdasarkan severity
        # ==========================================

        if tinggi > 0:
            recommendation.append({
                "text":
                f"Prioritaskan pemeriksaan pada {tinggi} data dengan tingkat risiko tinggi karena memiliki penyimpangan paling besar dari pola normal.",
                "row_number": None
            })
        elif sedang > 0:
            recommendation.append({
                "text":
                "Fokuskan pemeriksaan pada data dengan tingkat risiko sedang karena jumlahnya mendominasi anomali yang ditemukan.",
                "row_number": None
            })
        elif rendah > 0:
            recommendation.append({
                "text":
                "Anomali yang ditemukan sebagian besar bersifat ringan sehingga validasi dapat dilakukan secara bertahap.",
                "row_number": None
            })

        # ==========================================
        # 3. Wilayah terbanyak
        # ==========================================

        if (
            "bps_nama_kabupaten_kota" in anomaly.columns
            and len(anomaly) > 0
        ):
            counts = (
                anomaly["bps_nama_kabupaten_kota"]
                .value_counts()
            )

            wilayah = counts.idxmax()
            jumlah = counts.max()
            recommendation.append({
                "text":
                f"Mulailah proses verifikasi dari {wilayah} karena memiliki jumlah anomali terbanyak ({jumlah} data).",
                "row_number": None
            })

        # ==========================================
        # 4. Data paling ekstrem (klik -> highlight)
        # ==========================================

        if top is not None:
            if indicator and indicator in top.index:
                recommendation.append({
                    "text":
                    f"Prioritaskan pemeriksaan terhadap {top['bps_nama_kabupaten_kota']} karena memiliki nilai {indicator.lower()} sebesar {top[indicator]} dengan skor AI {top['score']:.3f}, yang merupakan penyimpangan paling ekstrem.",
                    "row_number":
                    int(top["row_number"])
                })
            else:
                recommendation.append({
                    "text":
                    f"Prioritaskan pemeriksaan terhadap {top['bps_nama_kabupaten_kota']} karena memiliki skor AI {top['score']:.3f}, yang merupakan penyimpangan paling ekstrem.",
                    "row_number":
                    int(top["row_number"])
                })

        # ==========================================
        # 5. Penutup
        # ==========================================

        if percentage < 10:
            recommendation.append({
                "text":
                "Setelah data anomali diverifikasi, dataset dapat digunakan sebagai dasar analisis maupun publikasi.",
                "row_number": None
            })
        else:
            recommendation.append({
                "text":
                "Disarankan melakukan analisis ulang setelah proses perbaikan untuk memastikan kualitas dataset telah meningkat.",
                "row_number": None
            })

        # ==========================================
        # Hapus duplikasi
        # ==========================================

        unique = []
        seen = set()
        for item in recommendation:
            if item["text"] not in seen:
                unique.append(item)
                seen.add(item["text"])
        return unique
    