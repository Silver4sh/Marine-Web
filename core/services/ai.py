"""core/services/ai.py — moved from services/ai_service.py"""
import pandas as pd
import random
from typing import Dict, Any, List


class MarineSLM:
    """
    Marine Small Language Model (Local Generative Engine).
    Uses Probabilistic Context-Free Grammar (PCFG) to generate dynamic,
    context-aware insights without external API dependencies.

    TRAINING DATA VERSION: v4.0 (Cognitive - Cross Domain)
    """

    def __init__(self):
        self.vocab = {
            "openers_positive": [
                "Kabar baik,", "Data menunjukkan hal positif:", "Secara umum,",
                "Terlihat tren bagus:", "Sistem memantau:", "Laporan terbaru mencatat:",
                "Hasil evaluasi menunjukan:", "Pantauan langsung mengonfirmasi:"
            ],
            "openers_negative": [
                "Perlu perhatian:", "Ada yang tidak beres:", "Peringatan dini:",
                "Hati-hati, ada risiko:", "Terdeteksi masalah pada:", "Segera cek bagian ini:",
                "Data menunjukkan penurunan:"
            ],
            "adjectives_strong":   ["sangat besar", "besar sekali", "kuat", "utama", "hebat", "keren", "banyak", "kokoh"],
            "adjectives_steady":   ["stabil", "lancar", "aman", "terjaga", "bagus", "tahan banting", "seimbang"],
            "adjectives_worrying": ["gawat", "mengkhawatirkan", "cukup tajam", "berisiko", "tidak stabil", "naik turun", "rawan"],
            "verbs_growth":  ["naik tinggi", "meningkat", "tumbuh", "semakin kuat", "melaju kencang", "meroket", "makin cepat"],
            "verbs_decline": ["turun", "merosot", "berkurang", "melambat", "melemah", "hilang", "jalan di tempat"],
            "connectors": ["yang artinya", "gara-gara", "menandakan", "memastikan", "sejalan dengan",
                           "berhubungan erat dengan", "didorong oleh", "yang disebabkan oleh"],
            "contrast_connectors": ["tapi", "meskipun begitu", "kebalikan dari", "beda dengan",
                                    "padahal di sisi lain", "anehnya"],
            "maritime_terms": ["kelancaran logistik", "waktu sandar", "waktu tunggu", "pemakaian kapal",
                               "kesiapan armada", "kecepatan bongkar muat", "siklus uang masuk"],
            "actions_retention": ["kunjungi mereka", "kasih diskon khusus", "ajak meeting santai",
                                  "prioritaskan layanan mereka", "cek lagi kontraknya"],
            "env_terms":     ["kualitas air", "keadaan laut", "kestabilan sensor", "kesehatan lingkungan"],
            "admin_terms":   ["keamanan sistem", "aturan akses", "kegiatan user", "rekam jejak"],
            "anomaly_terms": ["kapal hantu", "pergerakan tidak sah", "kelainan operasional", "penyimpangan kecepatan"],
        }

    def generate(self, intent: str, context: Dict[str, Any] = None) -> str:
        if context is None:
            context = {}
        result = "Data tidak tersedia."

        if intent == "cognitive_inefficiency":
            templates = [
                "{opener} kapal sibuk ({util}%) tapi uang yang masuk {verb}. Sepertinya ada biaya yang bocor.",
                "Pemakaian kapal tinggi ({util}%) {contrast} pendapatan malah {verb}. Cek lagi pengeluaran operasional.",
                "Armada kerja keras tapi hasilnya {verb}. Perlu audit biaya logistik.",
            ]
            result = random.choice(templates).format(
                util=context.get("util", "0"),
                opener=random.choice(self.vocab["openers_negative"]),
                conn=random.choice(self.vocab["connectors"]),
                contrast=random.choice(self.vocab["contrast_connectors"]),
                verb=random.choice(self.vocab["verbs_decline"]),
            )
        elif intent == "cognitive_hazard":
            templates = [
                "BAHAYA: Kapal sibuk banget ({util}%) padahal cuaca {adj}. Risiko kecelakaan meningkat.",
                "{opener} bahaya buat aset. Kapal jalan terus di tengah cuaca buruk. Tolong perketat aturan keselamatan.",
                "Gabungan cuaca {adj} dan lalu lintas padat butuh pengawasan ekstra.",
            ]
            result = random.choice(templates).format(
                util=context.get("util", "0"),
                opener=random.choice(self.vocab["openers_negative"]),
                adj=random.choice(self.vocab["adjectives_worrying"]),
            )
        elif intent == "cognitive_compounding_crisis":
            templates = [
                "GAWAT: Pendapatan turun ({growth}%) {conn} risiko klien kabur. Dampaknya bisa {adj}.",
                "{opener} efek domino buruk. Uang seret {contrast} klien mau pergi. Butuh penanganan segera.",
                "Bisnis lagi sakit: Arus kas {verb} dan klien {adj}. Fokus dulu ke kestabilan.",
            ]
            result = random.choice(templates).format(
                growth=context.get("growth", "0"),
                conn="diperparah oleh", contrast="bersamaan dengan",
                adj=random.choice(self.vocab["adjectives_worrying"]),
                opener=random.choice(self.vocab["openers_negative"]),
                verb=random.choice(self.vocab["verbs_decline"]),
            )
        elif intent == "cognitive_optimal":
            templates = [
                "PERFORMA PUNCAK: Kapal ({util}%), keuangan, dan lingkungan aman semua. Pertahankan kondisi {adj} ini.",
                "Sistem berjalan sangat efisien. Semua indikator (Kapal, Uang, Alam) statusnya 'HIJAU'.",
                "{opener} kerja sama tim yang bagus. Untung dan produktivitas naik {conn}.",
            ]
            result = random.choice(templates).format(
                util=context.get("util", "0"),
                adj=random.choice(self.vocab["adjectives_strong"]),
                opener=random.choice(self.vocab["openers_positive"]),
                conn="bersamaan",
            )
        elif intent == "whale_detected":
            templates = [
                "Ada {count} mitra besar (Paus) yang punya peran {adj} dalam {term} kita.",
                "Analisis menemukan {count} klien kunci yang kontribusinya {adj}. Sebaiknya {action}.",
                "Fokus jaga {count} klien besar ini; pola transaksi mereka {adj} banget buat {term}.",
                "{opener} {count} akun prioritas menguasai pendapatan. Harus dilayani spesial.",
            ]
            result = random.choice(templates).format(
                count=context.get("count", "beberapa"),
                adj=random.choice(self.vocab["adjectives_strong"]),
                term=random.choice(self.vocab["maritime_terms"]),
                action=random.choice(self.vocab["actions_retention"]),
                opener=random.choice(self.vocab["openers_positive"]),
            )
        elif intent == "churn_risk":
            templates = [
                "{opener} ada {count} klien yang mungkin mau kabur. {term} mereka {verb} drastis.",
                "Risiko kehilangan {count} akun. Pola pesanan terlihat {adj} dibanding dulu.",
                "Perlu tindakan buat {count} klien ini. Orderan lagi {verb}, segera {action}.",
                "Ada yang aneh pada {term} di {count} akun klien. Status: {adj}.",
            ]
            result = random.choice(templates).format(
                count=context.get("count", "beberapa"),
                opener=random.choice(self.vocab["openers_negative"]),
                verb=random.choice(self.vocab["verbs_decline"]),
                adj=random.choice(self.vocab["adjectives_worrying"]),
                term=random.choice(["frekuensi order", "nilai transaksi", "komunikasi", "pemesanan"]),
                action=random.choice(self.vocab["actions_retention"]),
            )
        elif intent == "high_utilization":
            templates = [
                "Efisiensi armada {verb} sampai {val}%. Ini performa yang {adj} banget.",
                "{opener} pemakaian kapal sangat {adj} ({val}%), {conn} manajemen rute pelayaran yang oke.",
                "Kapal beroperasi {adj} dengan tingkat pemakaian {val}%. Awas kru & mesin capek.",
            ]
            result = random.choice(templates).format(
                val=context.get("val", "0"),
                verb=random.choice(self.vocab["verbs_growth"]),
                adj=random.choice(self.vocab["adjectives_strong"]),
                opener=random.choice(self.vocab["openers_positive"]),
                conn=random.choice(self.vocab["connectors"]),
            )
        elif intent == "revenue_positive":
            templates = [
                "Pendapatan {verb} secara {adj} bulan ini, {conn} strategi jualan yang pas.",
                "{opener} arus kas positif. Pertumbuhan terlihat {adj} dan konsisten.",
                "Keuangan {verb}, tandanya bisnis lagi {adj}.",
            ]
            result = random.choice(templates).format(
                verb=random.choice(self.vocab["verbs_growth"]),
                adj=random.choice(self.vocab["adjectives_strong"]),
                opener=random.choice(self.vocab["openers_positive"]),
                conn=random.choice(self.vocab["connectors"]),
            )
        elif intent == "revenue_negative":
            templates = [
                "Pendapatan {verb} cukup {adj}. Cek lagi harga atau tagihan yang macet.",
                "{opener} uang masuk berkurang. Tren keuangan lagi {adj}.",
                "Kesehatan keuangan {verb}. Harus segera dicegah risikonya.",
            ]
            result = random.choice(templates).format(
                verb=random.choice(self.vocab["verbs_decline"]),
                adj=random.choice(self.vocab["adjectives_worrying"]),
                opener=random.choice(self.vocab["openers_negative"]),
            )
        elif intent == "forecast_insight":
            templates = [
                "Prediksi menunjukkan tren yang {adj} sampai akhir kuartal, {conn} data historis.",
                "Masa depan terlihat {adj}. {opener} ada potensi tumbuh terus.",
                "Ramalan menunjukkan kondisi {adj}, tapi tetap waspada pasar berubah.",
            ]
            result = random.choice(templates).format(
                adj=random.choice(self.vocab["adjectives_steady"] + self.vocab["adjectives_strong"]),
                conn=random.choice(self.vocab["connectors"]),
                opener=random.choice(self.vocab["openers_positive"]),
            )
        elif intent == "env_stable":
            adj  = random.choice(self.vocab["adjectives_steady"])
            adj2 = random.choice(self.vocab["adjectives_strong"] + ["normal"])
            result = random.choice([
                f"Kualitas air dalam kondisi {adj}. Sensor menunjukkan angka yang {adj2}.",
                f"{random.choice(self.vocab['openers_positive'])} kesehatan laut terpantau {adj}. Tidak ada masalah besar.",
                f"Pantauan lingkungan statusnya {adj}, aman buat operasional.",
            ])
        elif intent == "env_anomaly":
            result = random.choice([
                "{opener} ada nilai aneh di {count} ocean. Awas dampaknya ke {term}.",
                "Ada masalah kualitas air. Nilai sensor terlihat {adj}.",
                "Kondisi lingkungan berubah di lokasi. Perlu cek langsung ke sana.",
            ]).format(
                opener=random.choice(self.vocab["openers_negative"]),
                count=context.get("count", "beberapa"),
                term=random.choice(self.vocab["env_terms"]),
                adj=random.choice(self.vocab["adjectives_worrying"]),
            )
        elif intent == "admin_summary":
            adj = random.choice(self.vocab["adjectives_steady"])
            result = random.choice([
                f"Sistem berjalan {adj}. {context.get('count', '0')} user baru masuk minggu ini.",
                f"{random.choice(self.vocab['openers_positive'])} kegiatan user terlihat wajar. {context.get('count', '0')} log baru tercatat.",
                f"Akses user terpantau {adj}. Sistem aman.",
            ])
        elif intent == "vessel_anomaly":
            result = random.choice([
                "{opener} terdeteksi {count} {term} di armada. Segera verifikasi kondisi di lapangan.",
                "Ada {count} kapal menunjukkan perilaku {adj}. Sistem mendeteksi {term}.",
                "WASPADA: {count} insiden {term}. Ini bisa merugikan {conn} efisiensi operasional.",
            ]).format(
                opener=random.choice(self.vocab["openers_negative"]),
                count=context.get("count", "beberapa"),
                adj=random.choice(self.vocab["adjectives_worrying"]),
                term=random.choice(self.vocab["anomaly_terms"]),
                conn=random.choice(self.vocab["connectors"]),
            )
        elif intent == "kpi_achievement":
            pct = context.get("pct", 0)
            if pct >= 80:
                result = random.choice([
                    f"Pencapaian KPI bulan ini sangat {random.choice(self.vocab['adjectives_strong'])}: {pct}% dari target terpenuhi.",
                    f"{random.choice(self.vocab['openers_positive'])} kinerja {pct}% sudah melampaui ekspektasi. Pertahankan!",
                    f"Target tercapai {pct}%. Sistem berjalan dalam kondisi {random.choice(self.vocab['adjectives_steady'])}.",
                ])
            else:
                result = random.choice([
                    f"{random.choice(self.vocab['openers_negative'])} KPI bulan ini baru {pct}%. Diperlukan akselerasi segera.",
                    f"Pencapaian {pct}% terhadap target, {random.choice(self.vocab['adjectives_worrying'])}. Cek bottleneck proses.",
                    f"Hanya {pct}% target terkumpul. Ada risiko {random.choice(self.vocab['adjectives_worrying'])} di akhir periode.",
                ])
        elif intent == "target_progress":
            pct = context.get("pct", 0)
            rem = 100 - pct
            adj = "Terus semangat" if pct >= 60 else "Perlu percepatan"
            result = random.choice([
                f"Progress target: {round(pct,1)}% tercapai, masih kekurangan {round(rem,1)}% lagi untuk bulan ini.",
                f"{random.choice(self.vocab['openers_positive' if pct >= 60 else 'openers_negative'])} {round(pct,1)}% target bulanan sudah terpenuhi. Sisa {round(rem,1)}% harus dikejar.",
                f"Realisasi {round(pct,1)}% — {round(rem,1)}% lagi menuju target. {adj}!",
            ])
        return result


class MarineAIAnalyst:
    """Centralized AI Logic powered by MarineSLM."""
    slm = MarineSLM()

    @classmethod
    def analyze_holistic(cls, financials: Dict[str, Any], fleet: Dict[str, Any], anomaly_count: int, churn_risk_count: int) -> Dict[str, List[Dict[str, str]]]:
        insights: List[Dict[str, str]] = []
        rev_growth  = float(financials.get("delta_revenue", 0.0))
        utilization = float(fleet.get("utilization", 0.0))

        if utilization > 75 and rev_growth < -5:
            insights.append({"title": "🚨 Deteksi Inefisiensi Operasional",
                             "desc": cls.slm.generate("cognitive_inefficiency", {"util": f"{utilization:.0f}"}),
                             "type": "critical"})
        if utilization > 70 and anomaly_count >= 2:
            insights.append({"title": "⛈️ Risiko Keselamatan & Aset",
                             "desc": cls.slm.generate("cognitive_hazard", {"util": f"{utilization:.0f}"}),
                             "type": "warning"})
        if churn_risk_count > 3 and rev_growth < -10:
            insights.append({"title": "📉 Krisis Bisnis Majemuk",
                             "desc": cls.slm.generate("cognitive_compounding_crisis", {"growth": f"{rev_growth:.1f}"}),
                             "type": "critical"})
        if utilization > 60 and rev_growth > 5 and anomaly_count == 0:
            insights.append({"title": "✨ Sinergi Operasional Sempurna",
                             "desc": cls.slm.generate("cognitive_optimal", {"util": f"{utilization:.0f}"}),
                             "type": "positive"})
        return {"insights": insights}

    @classmethod
    def analyze_clients(cls, df: pd.DataFrame) -> Dict[str, List[Dict[str, str]]]:
        if df.empty:
            return {"insights": [{"title": "Data Kosong", "desc": "Data klien tidak tersedia saat ini.", "type": "info"}]}
        df = df.copy()
        df["ltv"]          = pd.to_numeric(df["ltv"],          errors="coerce").fillna(0)
        df["total_orders"] = pd.to_numeric(df["total_orders"], errors="coerce").fillna(0)
        high_ltv = df["ltv"].quantile(0.7)          if len(df) > 5 else 1e9
        high_act = df["total_orders"].quantile(0.7) if len(df) > 5 else 5
        whales = df[(df["ltv"] >= high_ltv) & (df["total_orders"] >= high_act)]
        churn  = df[df["churn_risk"] == "Tinggi"] if "churn_risk" in df.columns else pd.DataFrame()
        insights = []
        if not whales.empty:
            insights.append({"title": "Mitra Strategis",
                             "desc": MarineAIAnalyst.slm.generate("whale_detected", {"count": len(whales)}),
                             "type": "positive"})
        if not churn.empty:
            insights.append({"title": "Risiko Churn",
                             "desc": MarineAIAnalyst.slm.generate("churn_risk", {"count": len(churn)}),
                             "type": "warning"})
        if not insights:
            insights.append({"title": "Status Normal", "desc": "Portofolio klien stabil.", "type": "info"})
        return {"insights": insights}

    @classmethod
    def analyze_fleet(cls, utilization_rate: float) -> Dict[str, List[Dict[str, str]]]:
        if utilization_rate > 80:
            txt, t = cls.slm.generate("high_utilization", {"val": f"{utilization_rate:.1f}"}), "positive"
        elif utilization_rate < 40:
            txt, t = "Utilisasi armada rendah. Pertimbangkan optimasi rute.", "warning"
        else:
            txt, t = "Utilisasi armada stabil dan optimal.", "info"
        return {"insights": [{"title": "Efisiensi Armada", "desc": txt, "type": t}]}

    @classmethod
    def analyze_financials(cls, revenue_data: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
        delta = float(revenue_data.get("delta_revenue", 0.0))
        txt   = cls.slm.generate("revenue_positive" if delta >= 0 else "revenue_negative")
        insights = [
            {"title": "Kinerja Finansial",  "desc": txt, "type": "positive" if delta >= 0 else "warning"},
            {"title": "Outlook Masa Depan", "desc": cls.slm.generate("forecast_insight"), "type": "info"},
        ]
        return {"insights": insights}

    @classmethod
    def analyze_environment(cls, anomaly_df: pd.DataFrame) -> Dict[str, List[Dict[str, str]]]:
        if not anomaly_df.empty:
            txt, t = cls.slm.generate("env_anomaly", {"count": str(len(anomaly_df))}), "warning"
        else:
            txt, t = cls.slm.generate("env_stable"), "positive"
        return {"insights": [{"title": "Kualitas Lingkungan", "desc": txt, "type": t}]}

    @classmethod
    def analyze_admin(cls, users_summary: Dict[str, Any]) -> Dict[str, List[Dict[str, str]]]:
        count = users_summary.get("new_users", 0)
        return {"insights": [{"title": "Ringkasan Sistem",
                               "desc": cls.slm.generate("admin_summary", {"count": str(count)}),
                               "type": "info"}]}

    @classmethod
    def analyze_correlations(cls, corr_matrix: pd.DataFrame) -> Dict[str, List[Dict[str, str]]]:
        if corr_matrix.empty:
            return {"insights": []}
        pairs   = []
        columns = corr_matrix.columns
        for i in range(len(columns)):
            for j in range(i + 1, len(columns)):
                val = corr_matrix.iloc[i, j]
                if abs(val) >= 0.4:
                    pairs.append((columns[i], columns[j], val))
        if not pairs:
            return {"insights": [{"title": "🔗 Data Berdiri Sendiri",
                                   "desc": "Belum terlihat hubungan yang jelas antar data.",
                                   "type": "info"}]}
        insights = []
        for c1, c2, val in sorted(pairs, key=lambda x: abs(x[2]), reverse=True)[:3]:
            direction = "Positif" if val > 0 else "Negatif"
            strength  = "Sangat Erat" if abs(val) > 0.8 else ("Erat" if abs(val) > 0.6 else "Cukup Terlihat")
            desc = f"Hubungan **{direction} {strength}** ({val:.2f}) terlihat antara **{c1}** dan **{c2}**."
            if "Pendapatan" in [c1, c2]:
                desc += " Artinya: Jika satu naik, kemungkinan besar pendapatan juga ikut naik." if val > 0 \
                    else " Artinya: Hati-hati, jika faktor ini naik, pendapatan justru bisa turun."
            elif "Hari Bayar" in [c1, c2]:
                desc += " Ini bisa membuat uang masuk menjadi lebih lambat." if val > 0 \
                    else " Ini bagus karena bisa mempercepat penerimaan uang tunai."
            else:
                desc += " Keduanya cenderung naik atau turun bersamaan." if val > 0 \
                    else " Jika satu naik, yang lain biasanya turun."
            insights.append({"title": f"🔗 Hubungan: {c1} & {c2}", "desc": desc,
                              "type": "critical" if abs(val) > 0.8 else ("warning" if abs(val) > 0.6 else "info")})
        return {"insights": insights}

    @classmethod
    def analyze_anomalies(cls, anomaly_df: pd.DataFrame) -> Dict[str, List[Dict[str, str]]]:
        if anomaly_df is None or anomaly_df.empty:
            return {"insights": [{"title": "✅ Armada Normal",
                                   "desc": "Tidak ada anomali kapal yang terdeteksi dalam 2 jam terakhir.",
                                   "type": "positive"}]}
        count = len(anomaly_df)
        return {"insights": [{"title": f"🚨 {count} Anomali Kapal Aktif",
                               "desc": cls.slm.generate("vessel_anomaly", {"count": str(count)}),
                               "type": "critical"}]}

    @classmethod
    def analyze_kpi(cls, achieved_pct: float) -> Dict[str, List[Dict[str, str]]]:
        txt   = cls.slm.generate("kpi_achievement", {"pct": round(achieved_pct, 1)})
        itype = "positive" if achieved_pct >= 80 else ("warning" if achieved_pct >= 50 else "critical")
        return {"insights": [{"title": "🎯 Analisis KPI", "desc": txt, "type": itype}]}

    @classmethod
    def analyze_target_progress(cls, progress_pct: float) -> Dict[str, List[Dict[str, str]]]:
        txt   = cls.slm.generate("target_progress", {"pct": round(progress_pct, 1)})
        itype = "positive" if progress_pct >= 100 else ("warning" if progress_pct >= 60 else "critical")
        return {"insights": [{"title": "💰 Progres Target Bulanan", "desc": txt, "type": itype}]}

    @classmethod
    def ask_analyst(cls, message: str) -> str:
        msg = message.lower()
        if "kapal" in msg or "armada" in msg:
            return cls.slm.generate("high_utilization", {"val": "85.0"})
        elif "uang" in msg or "pendapatan" in msg or "revenue" in msg:
            return cls.slm.generate("revenue_positive")
        elif "anomali" in msg or "bahaya" in msg:
            return cls.slm.generate("vessel_anomaly", {"count": "2"})
        else:
            return "Halo! Saya Marine AI Analyst. Anda bisa bertanya tentang performa *kapal*, *pendapatan*, atau cek *anomali*."
