class InsightGenerator:

    def __init__(
        self,
        dataframe,
        report
    ):
        self.df = dataframe
        self.report = report

    def build(self):
        df = self.df
        anomaly_df = df[
            df["anomaly"] == -1
        ]
        insight = []

        # ==========================================
        # Kondisi Dataset
        # ==========================================

        percentage = self.report["anomaly_percentage"]
        if percentage < 5:
            insight.append(
                f"Hanya {percentage:.1f}% data yang teridentifikasi sebagai anomali sehingga kualitas dataset tergolong sangat baik. Validasi cukup difokuskan pada data yang ditandai AI tanpa perlu melakukan pemeriksaan ulang terhadap seluruh dataset."
            )
        elif percentage < 20:
            insight.append(
                f"Sebanyak {percentage:.1f}% data terdeteksi sebagai anomali. Dataset masih layak digunakan, namun beberapa data memerlukan validasi."
            )
        else:
            insight.append(
                f"Sebanyak {percentage:.1f}% data teridentifikasi sebagai anomali sehingga disarankan dilakukan pemeriksaan sebelum dataset digunakan lebih lanjut."
            )

        # ==========================================
        # Distribusi Severity
        # ==========================================

        tinggi = (
            anomaly_df["severity"] == "Tinggi"
        ).sum()
        sedang = (
            anomaly_df["severity"] == "Sedang"
        ).sum()
        rendah = (
            anomaly_df["severity"] == "Rendah"
        ).sum()

        total = len(anomaly_df)
        
        severity_count = {
            "Tinggi": tinggi,
            "Sedang": sedang,
            "Rendah": rendah
        }

        dominan = max(
            severity_count,
            key=severity_count.get
        )

        if dominan == "Tinggi":
            insight.append(
                f"Tingkat anomali yang paling banyak ditemukan adalah prioritas tinggi ({tinggi} dari {total} data). Hal ini menunjukkan cukup banyak penyimpangan yang perlu diprioritaskan untuk diperiksa."
            )
        elif dominan == "Sedang":
            insight.append(
                f"Tingkat anomali yang paling banyak ditemukan adalah prioritas sedang ({sedang} dari {total} data). Penyimpangan yang terjadi cenderung bersifat moderat."
            )
        else:
            insight.append(
                f"Tingkat anomali yang paling banyak ditemukan adalah prioritas rendah ({rendah} dari {total} data). Sebagian besar penyimpangan masih relatif ringan."
            )

        insight.append(
            f"Dari total {total} data anomali, terdapat {tinggi} prioritas tinggi, {sedang} prioritas sedang, dan {rendah} prioritas rendah."
        )

        # ==========================================
        # Wilayah dominan
        # ==========================================

        if (
            "bps_nama_kabupaten_kota" in anomaly_df.columns
            and len(anomaly_df) > 0
        ):
            counts = anomaly_df[
                "bps_nama_kabupaten_kota"
            ].value_counts()

            maksimum = counts.max()
            wilayah_terbanyak = counts[
                counts == maksimum
            ].index.tolist()

            jumlah = counts.max()
            persen = jumlah / len(anomaly_df) * 100

            if len(wilayah_terbanyak) == 1:
                insight.append(
                    f"Wilayah dengan jumlah anomali terbanyak adalah {wilayah_terbanyak[0]} ({maksimum} data)."
                )
            else:
                daftar = ", ".join(wilayah_terbanyak)
                insight.append(
                    f"Terdapat {len(wilayah_terbanyak)} wilayah dengan jumlah anomali tertinggi yang sama, yaitu {daftar} (masing-masing {maksimum} data)."
                )

            priority = (
                anomaly_df[
                    anomaly_df["severity"] == "Tinggi"
                ]
                ["bps_nama_kabupaten_kota"]
                .value_counts()
            )

            if not priority.empty:
                maks_prioritas = priority.max()
                wilayah_prioritas = priority[
                    priority == maks_prioritas
                ].index.tolist()
                if len(wilayah_prioritas) == 1:
                    insight.append(
                        f"Wilayah dengan anomali prioritas tinggi terbanyak adalah {wilayah_prioritas[0]} ({maks_prioritas} data)."
                    )
                else:
                    insight.append(
                        f"Anomali prioritas tinggi paling banyak ditemukan pada {', '.join(wilayah_prioritas)} (masing-masing {maks_prioritas} data)."
                    )

        # ==========================================
        # Anomali paling ekstrem
        # ==========================================

        if len(anomaly_df) > 0:
            top = anomaly_df.sort_values(
                by="score",
                ascending=False
            ).iloc[0]
            indikator = self.report.get("indicator")

            if "indicator" in top.index:
                indikator = top["indicator"]

            if indikator is not None and indikator in top.index:
                nama_indikator = indikator.replace("_", " ")
                insight.append(
                    f"Anomali paling ekstrem ditemukan pada {top['bps_nama_kabupaten_kota']} dengan nilai {nama_indikator} sebesar {top[indikator]}, prioritas {top['severity'].lower()}, dan skor AI {top['score']:.3f}."
                )

            jumlah_wilayah = counts.count()
            if percentage < 5:
                insight.append(
                    f"Secara keseluruhan dataset memiliki kualitas yang baik. Pemeriksaan cukup difokuskan pada {len(anomaly_df)} data anomali yang tersebar di {jumlah_wilayah} wilayah."
                )
            elif percentage < 20:
                insight.append(
                    f"Sebagian besar data masih konsisten. Namun, validasi terhadap {len(anomaly_df)} data anomali pada {jumlah_wilayah} wilayah disarankan sebelum dataset dipublikasikan."
                )
            else:
                insight.append(
                    f"Tingginya proporsi anomali menunjukkan perlunya evaluasi terhadap proses pengumpulan maupun pengolahan data sebelum dataset digunakan untuk analisis lanjutan."
                )

        return insight