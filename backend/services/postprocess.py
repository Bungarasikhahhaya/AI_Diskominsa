import pandas as pd

class PostprocessEngine:
    # ==========================================
    # Mapping hasil model AI
    # ==========================================
    def map_result(
        self,
        display_df,
        anomaly_df,
        indicator
    ):
        result = display_df.copy()
        result.insert(0, "row_number", range(1, len(result) + 1))
        result["anomaly"] = anomaly_df["anomaly"].values
        result["status"] = anomaly_df["status"].values
        result["severity"] = anomaly_df["severity"].values
        result["score"] = (anomaly_df["score"].abs().round(3))
        result["indicator"] = indicator
        result["indicator_value"] = result[indicator]
        return result
    
    # ==========================================
    # Report Generator
    # ==========================================

    def build_report(self, dataframe):

        anomaly = dataframe[
            dataframe["anomaly"] == -1
        ]

        return {
            "total_rows": len(dataframe),
            "anomaly_count": len(anomaly),
            "normal_count": len(dataframe) - len(anomaly),
            "anomaly_percentage": round(
                len(anomaly) / len(dataframe) * 100,
                2
            ),
            "top_anomalies": (
                anomaly
                .sort_values("score")
                .head(10)
                .to_dict(orient="records")
            )
        }

    # ==========================================
    # Insight Generator
    # ==========================================
    def build_insight(
        self, dataframe, report
        ):
        df = dataframe
        anomaly_df = df[
            df["anomaly"] == -1
        ]
        summary = ""
        findings = []

        # ==========================================
        # Kondisi Dataset
        # ==========================================

        percentage = report["anomaly_percentage"]
        if percentage < 5:
            summary = (
                f"Sebanyak {percentage:.1f}% data teridentifikasi sebagai anomali. "
                "Sebagian besar data mengikuti pola yang serupa."
            )
        elif percentage < 20:
           summary = (
                f"Sebanyak {percentage:.1f}% data teridentifikasi sebagai anomali. "
                "Beberapa data menunjukkan pola yang berbeda dari mayoritas."
            )
        else:
            summary = (
                f"Sebanyak {percentage:.1f}% data teridentifikasi sebagai anomali. "
                "Penyimpangan pola relatif banyak ditemukan pada dataset."
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
            findings.append(
                f"Mayoritas penyimpangan berada pada kategori prioritas tinggi ({severity_count[dominan]} data) sehingga perlu segera diperiksa."
            )

        elif dominan == "Sedang":
            findings.append(
                f"Mayoritas penyimpangan berada pada kategori prioritas sedang ({severity_count[dominan]} data)."
            )

        else:
            findings.append(
                f"Sebagian besar penyimpangan termasuk kategori prioritas rendah ({severity_count[dominan]} data)."
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

            if len(wilayah_terbanyak) == 1:
                findings.append(
                    f"{wilayah_terbanyak[0]} memiliki jumlah anomali terbanyak ({maksimum} data)."
                )
            else:
                daftar = ", ".join(wilayah_terbanyak)
                findings.append(
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
                    findings.append(
                        f"Anomali prioritas tinggi paling banyak ditemukan di {wilayah_prioritas[0]}."
                    )
                else:
                    daftar = ", ".join(wilayah_prioritas)
                    findings.append(
                        f"Anomali prioritas tinggi ditemukan pada {daftar}."
                    )

        # ==========================================
        # Anomali paling ekstrem
        # ==========================================

        if len(anomaly_df) > 0:
            top = anomaly_df.sort_values(
                by="score",
                ascending=False
            ).iloc[0]
            indikator = report.get("indicator")

            if "indicator" in top.index:
                indikator = top["indicator"]

            if indikator is not None and indikator in top.index:
                findings.append(
                    f"Penyimpangan terbesar ditemukan di {top['bps_nama_kabupaten_kota']} (skor AI {top['score']:.3f})."
                )

        return {
            "summary": summary,
            "findings": findings
        }
    
    # ========================================
    # Recommendation Generator
    # ========================================    
    def build_recommendation(
        self,
        dataframe,
        report
    ):
        anomaly=dataframe[
            dataframe["anomaly"]==-1
        ]
        percentage = report["anomaly_percentage"]

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
        indicator = report.get("indicator")

        # ==========================================
        # Rekomendasi
        # ==========================================
        if percentage < 5:
            recommendation.append({
                "text":
                "Validasi beberapa data yang ditandai AI sebelum publikasi.",
                "row_number": None
            })

        elif percentage < 20:
            recommendation.append({
                "text":
                "Lakukan validasi pada seluruh data anomali sebelum digunakan.",
                "row_number": None
            })

        else:
            recommendation.append({
                "text":
                "Audit proses pengumpulan data sebelum dataset digunakan.",
                "row_number": None
            })
        
        # ==========================================
        # Prioritas severity
        # ==========================================
        if tinggi > 0:
            recommendation.append({
                "text":
                f"Periksa terlebih dahulu {tinggi} data prioritas tinggi.",
                "row_number": None
            })

        elif sedang > 0:
            recommendation.append({
                "text":
                f"Fokuskan validasi pada {sedang} data prioritas sedang.",
                "row_number": None
            })

        # ==========================================
        # Fokus wilayah
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
                f"Mulai pemeriksaan dari {wilayah} ({jumlah} data).",
                "row_number": None
            })

        # ==========================================
        # Fokus wilayah
        # ==========================================
        if top is not None:
            if indicator and indicator in top.index:
                recommendation.append({
                    "text":
                    f"Verifikasi nilai {top[indicator]} di {top['bps_nama_kabupaten_kota']} (skor AI {top['score']:.3f}).",
                    "row_number":
                    int(top["row_number"])
                })

        recommendation.append({
            "text":
            "Jalankan analisis ulang setelah data diperbaiki.",
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
    
    # ========================================
    # Response Builder
    # ========================================    
    def build_response(
        self,
        dataset_info,
        statistics,
        validation,
        anomaly,
        mapped_result,
        report,
        insight,
        recommendation
    ):
        from datetime import datetime
        anomaly_only = mapped_result[
            mapped_result["anomaly"] == -1
        ]

        return {
            "generated_at": datetime.now().isoformat(),
            "dataset": dataset_info,
            "summary": {
                "rows": statistics["dataset"]["rows"],
                "columns": statistics["dataset"]["columns"],
                "validation": validation["valid"],
                "algorithm": anomaly["report"]["algorithm"],
                "anomaly_count": anomaly["report"]["anomaly_count"],
                "normal_count": anomaly["report"]["normal_count"],
                "anomaly_percentage": anomaly["report"]["anomaly_percentage"]
            },
            "report": report,
            "insight": insight,
            "recommendation": recommendation,
            "anomaly": {
                "count": len(anomaly_only),
                "top": (
                    anomaly_only
                    .sort_values(by="score")
                    .head(10)
                    .to_dict(orient="records")
                ),
                "all": mapped_result.to_dict(
                    orient="records"
                )
            }

        }

    