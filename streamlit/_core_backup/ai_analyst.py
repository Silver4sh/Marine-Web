import pandas as pd
import numpy as np
import random

class MarineSLM:
    """
    Marine Small Language Model (Local Generative Engine).
    Uses Probabilistic Context-Free Grammar (PCFG) to generate dynamic, 
    context-aware insights without external API dependencies.
    
    TRAINING DATA VERSION: v4.0 (Cognitive - Cross Domain)
    """
    
    def __init__(self):
        # --- KNOWLEDGE BASE / VOCABULARY (SIMPLIFIED v5.0) ---
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
            "adjectives_strong": [
                "sangat besar", "besar sekali", "kuat", "utama", "hebat", "keren", "banyak", "kokoh"
            ],
            "adjectives_steady": [
                "stabil", "lancar", "aman", "terjaga", "bagus", "tahan banting", "seimbang"
            ],
            "adjectives_worrying": [
                "gawat", "mengkhawatirkan", "cukup tajam", "berisiko", "tidak stabil", "naik turun", "rawan"
            ],
            "verbs_growth": [
                "naik tinggi", "meningkat", "tumbuh", "semakin kuat", "melaju kencang", "meroket", "makin cepat"
            ],
            "verbs_decline": [
                "turun", "merosot", "berkurang", "melambat", "melemah", "hilang", "jalan di tempat"
            ],
            "connectors": [
                "yang artinya", "gara-gara", "menandakan", "memastikan", "sejalan dengan",
                "berhubungan erat dengan", "didorong oleh", "yang disebabkan oleh"
            ],
            "contrast_connectors": [
                "tapi", "meskipun begitu", "kebalikan dari", "beda dengan", 
                "padahal di sisi lain", "anehnya"
            ],
            # --- MARITIME & ANALYTICS TERMS (SIMPLIFIED) ---
            "maritime_terms": [
                "kelancaran logistik", "waktu sandar", "waktu tunggu", "pemakaian kapal", 
                "kesiapan armada", "kecepatan bongkar muat", "siklus uang masuk"
            ],
            "actions_retention": [
                "kunjungi mereka", "kasih diskon khusus", "ajak meeting santai",
                "prioritaskan layanan mereka", "cek lagi kontraknya"
            ],
            "env_terms": [
                "kualitas air", "keadaan laut", "kestabilan sensor", "kesehatan lingkungan"
            ],
             "admin_terms": [
                "keamanan sistem", "aturan akses", "kegiatan user", "rekam jejak"
            ]
        }

    def generate(self, intent, context={}):
        """
        Generates a unique sentence based on intent and context variables.
        Uses advanced slot-filling and randomization.
        """
        result = "Data tidak tersedia."
        
        # --- COGNITIVE / HOLISTIC INTENTS (v4.0) ---
        if intent == "cognitive_inefficiency":
            # High Fleet Activity BUT Low Revenue
            templates = [
                "{opener} kapal sibuk ({util}%) tapi uang yang masuk {verb}. Sepertinya ada biaya yang bocor.",
                "Pemakaian kapal tinggi ({util}%) {contrast} pendapatan malah {verb}. Cek lagi pengeluaran operasional.",
                "Armada kerja keras tapi hasilnya {verb}. Perlu audit biaya logistik."
            ]
            opener = random.choice(self.vocab["openers_negative"])
            conn = random.choice(self.vocab["connectors"])
            contrast = random.choice(self.vocab["contrast_connectors"])
            verb = random.choice(self.vocab["verbs_decline"])
            result = random.choice(templates).format(util=context.get('util', '0'), opener=opener, conn=conn, contrast=contrast, verb=verb)
            
        elif intent == "cognitive_hazard":
            # High Activity + Bad Weather
            templates = [
                "BAHAYA: Kapal sibuk banget ({util}%) padahal cuaca {adj}. Risiko kecelakaan meningkat.",
                "{opener} bahaya buat aset. Kapal jalan terus di tengah cuaca buruk. Tolong perketat aturan keselamatan.",
                "Gabungan cuaca {adj} dan lalu lintas padat butuh pengawasan ekstra."
            ]
            opener = random.choice(self.vocab["openers_negative"])
            adj = random.choice(self.vocab["adjectives_worrying"])
            result = random.choice(templates).format(util=context.get('util', '0'), opener=opener, adj=adj)

        elif intent == "cognitive_compounding_crisis":
            # Churn Risk + Revenue Drop
            templates = [
                "GAWAT: Pendapatan turun ({growth}%) {conn} risiko klien kabur. Dampaknya bisa {adj}.",
                "{opener} efek domino buruk. Uang seret {contrast} klien mau pergi. Butuh penanganan segera.",
                "Bisnis lagi sakit: Arus kas {verb} dan klien {adj}. Fokus dulu ke kestabilan."
            ]
            conn = "diperparah oleh"
            contrast = "bersamaan dengan"
            adj = random.choice(self.vocab["adjectives_worrying"])
            opener = random.choice(self.vocab["openers_negative"])
            verb = random.choice(self.vocab["verbs_decline"])
            result = random.choice(templates).format(growth=context.get('growth', '0'), conn=conn, contrast=contrast, adj=adj, opener=opener, verb=verb)
        
        elif intent == "cognitive_optimal":
            # High Rev + High Util + Stable Env
            templates = [
                "PERFORMA PUNCAK: Kapal ({util}%), keuangan, dan lingkungan aman semua. Pertahankan kondisi {adj} ini.",
                "Sistem berjalan sangat efisien. Semua indikator (Kapal, Uang, Alam) statusnya 'HIJAU'.",
                "{opener} kerja sama tim yang bagus. Untung dan produktivitas naik {conn}."
            ]
            adj = random.choice(self.vocab["adjectives_strong"])
            opener = random.choice(self.vocab["openers_positive"])
            conn = "bersamaan"
            result = random.choice(templates).format(util=context.get('util', '0'), adj=adj, opener=opener, conn=conn)

        # --- EXISTING INTENTS (Base v3.0) ---
        elif intent == "whale_detected":
            templates = [
                "Ada {count} mitra besar (Paus) yang punya peran {adj} dalam {term} kita.",
                "Analisis menemukan {count} klien kunci yang kontribusinya {adj}. Sebaiknya {action}.",
                "Fokus jaga {count} klien besar ini; pola transaksi mereka {adj} banget buat {term}.",
                "{opener} {count} akun prioritas menguasai pendapatan. Harus dilayani spesial."
            ]
            term = random.choice(self.vocab["maritime_terms"])
            action = random.choice(self.vocab["actions_retention"])
            adj = random.choice(self.vocab["adjectives_strong"])
            opener = random.choice(self.vocab["openers_positive"])
            
            result = random.choice(templates).format(
                count=context.get('count', 'beberapa'),
                adj=adj, term=term, action=action, opener=opener
            )
            
        elif intent == "churn_risk":
            templates = [
                "{opener} ada {count} klien yang mungkin mau kabur. {term} mereka {verb} drastis.",
                "Risiko kehilangan {count} akun. Pola pesanan terlihat {adj} dibanding dulu.",
                "Perlu tindakan buat {count} klien ini. Orderan lagi {verb}, segera {action}.",
                "Ada yang aneh pada {term} di {count} akun klien. Status: {adj}."
            ]
            opener = random.choice(self.vocab["openers_negative"])
            verb = random.choice(self.vocab["verbs_decline"])
            adj = random.choice(self.vocab["adjectives_worrying"])
            term = random.choice(["frekuensi order", "nilai transaksi", "komunikasi", "pemesanan"])
            action = random.choice(self.vocab["actions_retention"])
            
            result = random.choice(templates).format(
                count=context.get('count', 'beberapa'),
                opener=opener, verb=verb, adj=adj, term=term, action=action
            )
            
        elif intent == "high_utilization":
            templates = [
                "Efisiensi armada {verb} sampai {val}%. Ini performa yang {adj} banget.",
                "{opener} pemakaian kapal sangat {adj} ({val}%), {conn} manajemen {term} yang oke.",
                "Kapal beroperasi {adj} dengan tingkat pemakaian {val}%. Awas kru & mesin capek."
            ]
            verb = random.choice(self.vocab["verbs_growth"])
            adj = random.choice(self.vocab["adjectives_strong"])
            opener = random.choice(self.vocab["openers_positive"])
            conn = random.choice(self.vocab["connectors"])
            term = "rute pelayaran"
            
            result = random.choice(templates).format(
                val=context.get('val', '0'),
                verb=verb, adj=adj, opener=opener, conn=conn, term=term
            )
        
        elif intent == "revenue_positive":
            templates = [
                "Pendapatan {verb} secara {adj} bulan ini, {conn} strategi jualan yang pas.",
                "{opener} arus kas positif. Pertumbuhan terlihat {adj} dan konsisten.",
                "Keuangan {verb}, tandanya bisnis lagi {adj}."
            ]
            verb = random.choice(self.vocab["verbs_growth"])
            adj = random.choice(self.vocab["adjectives_strong"])
            opener = random.choice(self.vocab["openers_positive"])
            conn = random.choice(self.vocab["connectors"])
            result = random.choice(templates).format(verb=verb, adj=adj, opener=opener, conn=conn)

        elif intent == "revenue_negative":
            templates = [
                "Pendapatan {verb} cukup {adj}. Cek lagi harga atau tagihan yang macet.",
                "{opener} uang masuk berkurang. Tren keuangan lagi {adj}.",
                "Kesehatan keuangan {verb}. Harus segera dicegah risikonya."
            ]
            verb = random.choice(self.vocab["verbs_decline"])
            adj = random.choice(self.vocab["adjectives_worrying"])
            opener = random.choice(self.vocab["openers_negative"])
            result = random.choice(templates).format(verb=verb, adj=adj, opener=opener)
            
        elif intent == "forecast_insight":
            templates = [
                "Prediksi menunjukkan tren yang {adj} sampai akhir kuartal, {conn} data historis.",
                "Masa depan terlihat {adj}. {opener} ada potensi tumbuh terus.",
                "Ramalan menunjukkan kondisi {adj}, tapi tetap waspada pasar berubah."
            ]
            adj = random.choice(self.vocab["adjectives_steady"] + self.vocab["adjectives_strong"])
            conn = random.choice(self.vocab["connectors"])
            opener = random.choice(self.vocab["openers_positive"])
            result = random.choice(templates).format(adj=adj, conn=conn, opener=opener)

        elif intent == "env_stable":
            templates = [
                "Kualitas air dalam kondisi {adj}. Sensor menunjukkan angka yang {adj2}.",
                "{opener} kesehatan laut terpantau {adj}. Tidak ada masalah besar.",
                "Pantauan lingkungan statusnya {adj}, aman buat operasional."
            ]
            adj = random.choice(self.vocab["adjectives_steady"])
            adj2 = random.choice(self.vocab["adjectives_strong"] + ["normal"])
            opener = random.choice(self.vocab["openers_positive"])
            result = random.choice(templates).format(adj=adj, adj2=adj2, opener=opener)

        elif intent == "env_anomaly":
            templates = [
                "{opener} ada nilai aneh di {count} buoy. Awas dampaknya ke {term}.",
                "Ada masalah kualitas air. Nilai sensor terlihat {adj}.",
                "Kondisi lingkungan {verb} di lokasi. Perlu cek langsung ke sana."
            ]
            opener = random.choice(self.vocab["openers_negative"])
            term = random.choice(self.vocab["env_terms"])
            adj = random.choice(self.vocab["adjectives_worrying"])
            verb = "berubah"
            result = random.choice(templates).format(opener=opener, count=context.get('count', 'beberapa'), term=term, adj=adj, verb=verb)

        elif intent == "admin_summary":
            templates = [
                "Sistem berjalan {adj}. {count} user baru masuk minggu ini.",
                "{opener} kegiatan user terlihat wajar. {count} log baru tercatat.",
                "Akses user terpantau {adj}. Sistem aman."
            ]
            adj = random.choice(self.vocab["adjectives_steady"])
            opener = random.choice(self.vocab["openers_positive"])
            result = random.choice(templates).format(adj=adj, count=context.get('count', '0'), opener=opener)

            
        return result


class MarineAIAnalyst:
    """
    Centralized AI Logic powered by MarineSLM.
    """
    slm = MarineSLM()
    
    @staticmethod
    def analyze_holistic(financials, fleet, anomaly_count, churn_risk_count):
        """
        New V4.0 Capability: Cross-Domain Cognitive Analysis
        """
        insights = []
        
        # Extract metrics
        rev_growth = financials.get('delta_revenue', 0)
        utilization = fleet.get('utilization', 0)
        
        # Inefficiency (High Work, Low Pay)
        if utilization > 75 and rev_growth < -5:
            txt = MarineAIAnalyst.slm.generate("cognitive_inefficiency", {"util": f"{utilization:.0f}", "verb": "menurun"})
            insights.append({"title": "🚨 Deteksi Inefisiensi Operasional", "desc": txt, "type": "critical"})
            
        # Safety Hazard (High Work, Bad Env) - Assuming anomaly > 2 is bad
        if utilization > 70 and anomaly_count >= 2:
            txt = MarineAIAnalyst.slm.generate("cognitive_hazard", {"util": f"{utilization:.0f}"})
            insights.append({"title": "⛈️ Risiko Keselamatan & Aset", "desc": txt, "type": "warning"})
            
        # Compounding Crisis (Churn + Rev Drop)
        if churn_risk_count > 3 and rev_growth < -10:
             txt = MarineAIAnalyst.slm.generate("cognitive_compounding_crisis", {"growth": f"{rev_growth:.1f}"})
             insights.append({"title": "📉 Krisis Bisnis Majemuk", "desc": txt, "type": "critical"})

        # Optimal State
        if utilization > 60 and rev_growth > 5 and anomaly_count == 0:
            txt = MarineAIAnalyst.slm.generate("cognitive_optimal", {"util": f"{utilization:.0f}"})
            insights.append({"title": "✨ Sinergi Operasional Sempurna", "desc": txt, "type": "positive"})
            
        return {"insights": insights}

    @staticmethod
    def analyze_clients(df):
        if df.empty: return {"insight": "Data tidak tersedia."}
        df = df.copy()
        df['ltv'] = pd.to_numeric(df['ltv'], errors='coerce').fillna(0)
        df['total_orders'] = pd.to_numeric(df['total_orders'], errors='coerce').fillna(0)
        
        high_ltv = df['ltv'].quantile(0.7) if len(df) > 5 else 1e9
        high_act = df['total_orders'].quantile(0.7) if len(df) > 5 else 5
        whales = df[(df['ltv'] >= high_ltv) & (df['total_orders'] >= high_act)]
        churn = df[df['churn_risk'] == 'Tinggi'] if 'churn_risk' in df.columns else pd.DataFrame()
        
        insights = []
        if not whales.empty:
            insights.append({"title": "Mitra Strategis", "desc": MarineAIAnalyst.slm.generate("whale_detected", {"count": len(whales)}), "type": "positive"})
        if not churn.empty:
            insights.append({"title": "Risiko Churn", "desc": MarineAIAnalyst.slm.generate("churn_risk", {"count": len(churn)}), "type": "warning"})
        if not insights:
            insights.append({"title": "Status Normal", "desc": "Portofolio klien stabil.", "type": "info"})
            
        return {"insights": insights}

    @staticmethod
    def analyze_fleet(utilization_rate):
        insights = []
        if utilization_rate > 80:
            txt = MarineAIAnalyst.slm.generate("high_utilization", {"val": f"{utilization_rate:.1f}"})
            type_k = "positive"
        elif utilization_rate < 40:
            txt = "Utilisasi armada rendah. Pertimbangkan optimasi rute."
            type_k = "warning"
        else:
            txt = "Utilisasi armada stabil dan optimal."
            type_k = "info"
            
        insights.append({"title": "Efisiensi Armada", "desc": txt, "type": type_k})
        return {"insights": insights}

    @staticmethod
    def analyze_financials(revenue_data):
        delta = revenue_data.get('delta_revenue', 0)
        insights = []
        if delta >= 0:
            txt = MarineAIAnalyst.slm.generate("revenue_positive")
            type_k = "positive"
        else:
            txt = MarineAIAnalyst.slm.generate("revenue_negative")
            type_k = "warning"
            
        insights.append({"title": "Kinerja Finansial", "desc": txt, "type": type_k})
        
        forecast_txt = MarineAIAnalyst.slm.generate("forecast_insight")
        insights.append({"title": "Outlook Masa Depan", "desc": forecast_txt, "type": "info"})
        
        return {"insights": insights}

    @staticmethod
    def analyze_environment(anomaly_df):
        insights = []
        if not anomaly_df.empty:
            txt = MarineAIAnalyst.slm.generate("env_anomaly", {"count": len(anomaly_df)})
            type_k = "warning"
        else:
            txt = MarineAIAnalyst.slm.generate("env_stable")
            type_k = "positive"
        
        insights.append({"title": "Kualitas Lingkungan", "desc": txt, "type": type_k})
        return {"insights": insights}

    @staticmethod
    def analyze_admin(users_summary):
        count = users_summary.get('new_users', 0)
        txt = MarineAIAnalyst.slm.generate("admin_summary", {"count": count})
        return {"insights": [{"title": "Ringkasan Sistem", "desc": txt, "type": "info"}]}

    @staticmethod
    def analyze_correlations(corr_matrix):
        insights = []
        if corr_matrix.empty: return {"insights": []}
        
        # Find correlations (Threshold lowered to 0.4 for more sensitivity)
        pairs = []
        columns = corr_matrix.columns
        for i in range(len(columns)):
            for j in range(i+1, len(columns)):
                val = corr_matrix.iloc[i, j]
                if abs(val) >= 0.4:
                    c1 = columns[i]
                    c2 = columns[j]
                    pairs.append((c1, c2, val))
        
        if pairs:
            # Sort by absolute strength
            pairs.sort(key=lambda x: abs(x[2]), reverse=True)
            
            # Take top 3
            top_pairs = pairs[:3]
            
            for p in top_pairs:
                c1, c2, val = p
                direction = "Positif" if val > 0 else "Negatif"
                strength = "Sangat Erat" if abs(val) > 0.8 else ("Erat" if abs(val) > 0.6 else "Cukup Terlihat")
                
                # Contextual Description (Simplified Language)
                desc = f"Hubungan **{direction} {strength}** ({val:.2f}) terlihat antara **{c1}** dan **{c2}**."
                
                if "Pendapatan" in [c1, c2]:
                    if val > 0: desc += " Artinya: Jika satu naik, kemungkinan besar pendapatan juga ikut naik."
                    else: desc += " Artinya: Hati-hati, jika faktor ini naik, pendapatan justru bisa turun."
                elif "Hari Bayar" in [c1, c2]:
                    if val > 0: desc += " Ini bisa membuat uang masuk menjadi lebih lambat."
                    else: desc += " Ini bagus karena bisa mempercepat penerimaan uang tunai."
                else:
                    if val > 0: desc += " Keduanya cenderung naik atau turun bersamaan."
                    else: desc += " Jika satu naik, yang lain biasanya turun."
                
                # Determine alert type based on strength
                alert_type = "critical" if abs(val) > 0.8 else ("warning" if abs(val) > 0.6 else "info")
                
                insights.append({
                    "title": f"🔗 Hubungan: {c1} & {c2}", 
                    "desc": desc, 
                    "type": alert_type
                })
        else:
             insights.append({
                 "title": "🔗 Data Berdiri Sendiri", 
                 "desc": "Belum terlihat hubungan yang jelas antar data. Saat ini, setiap faktor bergerak sendiri-sendiri.", 
                 "type": "info"
             })
             
        return {"insights": insights}
