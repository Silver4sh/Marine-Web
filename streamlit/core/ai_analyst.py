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
        # --- KNOWLEDGE BASE / VOCABULARY ---
        self.vocab = {
            "openers_positive": [
                "Indikator kinerja maritim menunjukkan", "Analisis data operasional memperlihatkan", "Secara keseluruhan,",
                "Tren saat ini mengindikasikan", "Pemantauan sistem mendeteksi", "Laporan intelijen mencatat",
                "Evaluasi kuartal ini mengonfirmasi", "Data real-time mengonfirmasi"
            ],
            "openers_negative": [
                "Perhatian khusus diperlukan karena", "Sistem mendeteksi anomali operasional:", "Peringatan dini:",
                "Analisis risiko menunjukkan", "Terdapat indikasi friksi pada", "Perlu evaluasi segera:",
                "Penyimpangan data terdeteksi:"
            ],
            "adjectives_strong": [
                "signifikan", "masif", "kuat", "dominan", "luar biasa", "impresif", "substansial", "kokoh"
            ],
            "adjectives_steady": [
                "stabil", "konsisten", "berkelanjutan", "terjaga", "solid", "resilien", "seimbang"
            ],
            "adjectives_worrying": [
                "kritikal", "mengkhawatirkan", "cukup tajam", "berisiko", "tidak stabil", "volatil", "rentan"
            ],
            "verbs_growth": [
                "melonjak", "meningkat", "tumbuh", "menguat", "berakselerasi", "meroket", "terakselerasi"
            ],
            "verbs_decline": [
                "terkoreksi", "menurun", "menyusut", "melambat", "melemah", "tergerus", "stagnan"
            ],
            "connectors": [
                "yang mencerminkan", "sebagai akibat dari", "menandakan", "mengonfirmasi", "sejalan dengan",
                "berkorelasi positif dengan", "didorong oleh", "yang dipicu oleh"
            ],
            "contrast_connectors": [
                "namun", "meskipun demikian", "berlawanan dengan", "kontradiktif dengan", 
                "sementara di sisi lain", "ironisnya"
            ],
            # --- MARITIME & ANALYTICS TERMS ---
            "maritime_terms": [
                "efisiensi logistik", "turnaround time", "dwelling time", "utilisasi aset", 
                "ketersediaan armada", "produktivitas bongkar muat", "siklus pendapatan"
            ],
            "actions_retention": [
                "lakukan kunjungan bisnis", "tawarkan insentif volume", "jadwalkan rapat strategis",
                "berikan prioritas layanan", "evaluasi kontrak kerjasama"
            ],
            "env_terms": [
                "kualitas air", "ekosistem perairan", "stabilitas parameter", "kesehatan lingkungan"
            ],
             "admin_terms": [
                "integritas sistem", "protokol keamanan", "aktivitas pengguna", "jejak audit"
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
                "{opener} disonansi antara aktivitas armada ({util}%) dan hasil finansial. {conn} pendapatan {verb}. Indikasi inefisiensi biaya.",
                "Utilisasi aset sangat tinggi ({util}%) {contrast} kinerja revenue yang {verb}. Waspadai kebocoran margin operasional.",
                "Armada bekerja keras namun produktivitas finansial {verb}. Perlu audit pada struktur biaya logistik."
            ]
            opener = random.choice(self.vocab["openers_negative"])
            conn = random.choice(self.vocab["connectors"])
            contrast = random.choice(self.vocab["contrast_connectors"])
            verb = random.choice(self.vocab["verbs_decline"])
            result = random.choice(templates).format(util=context.get('util', '0'), opener=opener, conn=conn, contrast=contrast, verb=verb)
            
        elif intent == "cognitive_hazard":
            # High Activity + Bad Weather
            templates = [
                "PERINGATAN KESELAMATAN: Tingkat operasional tinggi ({util}%) terdeteksi saat kondisi lingkungan {adj}. Risiko insiden meningkat.",
                "{opener} paparan risiko aset. Armada beroperasi penuh di tengah anomali cuaca. Protokol keselamatan harus diperketat.",
                "Kombinasi cuaca {adj} dan lalu lintas padat memerlukan pengawasan ekstra dari menara kontrol."
            ]
            opener = random.choice(self.vocab["openers_negative"])
            adj = random.choice(self.vocab["adjectives_worrying"])
            result = random.choice(templates).format(util=context.get('util', '0'), opener=opener, adj=adj)

        elif intent == "cognitive_compounding_crisis":
            # Churn Risk + Revenue Drop
            templates = [
                "SITUASI KRITIS: Penurunan pendapatan ({growth}%) {conn} risiko churn pada klien utama. Potensi dampak jangka panjang {adj}.",
                "{opener} efek domino negatif. Koreksi finansial {contrast} ancaman retensi klien. Diperlukan 'Crisis Management' segera.",
                "Kesehatan bisnis terganggu ganda: Arus kas {verb} dan basis klien {adj}. Fokuskan sumber daya pada stabilitas."
            ]
            conn = "diperparah oleh"
            contrast = "berimpitan dengan"
            adj = random.choice(self.vocab["adjectives_worrying"])
            opener = random.choice(self.vocab["openers_negative"])
            verb = random.choice(self.vocab["verbs_decline"])
            result = random.choice(templates).format(growth=context.get('growth', '0'), conn=conn, contrast=contrast, adj=adj, opener=opener, verb=verb)
        
        elif intent == "cognitive_optimal":
            # High Rev + High Util + Stable Env
            templates = [
                "PERFORMA PUNCAK: Keselarasan sempurna antara operasional ({util}%), finansial, dan lingkungan. Pertahankan momentum {adj} ini.",
                "Sistem berjalan dalam efisiensi maksimum. Semua indikator (Fleet, Fin, Env) menunjukkan status 'HIJAU'.",
                "{opener} sinergi positif antar departemen. Profitabilitas dan produktivitas tumbuh {conn}."
            ]
            adj = random.choice(self.vocab["adjectives_strong"])
            opener = random.choice(self.vocab["openers_positive"])
            conn = "beriringan"
            result = random.choice(templates).format(util=context.get('util', '0'), adj=adj, opener=opener, conn=conn)

        # --- EXISTING INTENTS (Base v3.0) ---
        elif intent == "whale_detected":
            templates = [
                "Terdeteksi {count} mitra strategis (Whales) yang memegang peran {adj} dalam {term} perusahaan.",
                "Analisis portofolio mengidentifikasi {count} klien kunci dengan kontribusi LTV yang {adj}. Disarankan untuk {action}.",
                "Fokuskan retensi pada {count} klien 'Whale' ini; mereka menunjukkan pola transaksi {adj} yang vital bagi {term}.",
                "{opener} {count} akun prioritas mendominasi revenue stream. Perlakuan khusus wajib diberikan."
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
                "{opener} adanya {count} klien dengan probabilitas churn tinggi. Aktivitas {term} mereka {verb} drastis.",
                "Risiko retensi terdeteksi pada {count} akun. Pola pesanan terlihat {adj} dibandingkan periode lalu.",
                "Diperlukan intervensi untuk {count} klien berisiko. Tren keterlibatan sedang {verb}, segera {action}.",
                "Anomali pada {term} terdeteksi di {count} akun klien. Status: {adj}."
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
                "Efisiensi armada {verb} mencapai {val}%. Ini adalah performa {adj} untuk standar industri.",
                "{opener} tingkat utilisasi kapal sangat {adj} ({val}%), {conn} manajemen {term} yang optimal.",
                "Operasional armada berjalan {adj} dengan tingkat pemakaian {val}%. Waspadai kelelahan kru & mesin."
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
                "Pendapatan {verb} secara {adj} bulan ini, {conn} strategi komersial yang efektif.",
                "{opener} arus kas positif. Pertumbuhan tercatat {adj} dan konsisten di seluruh lini bisnis.",
                "Performa finansial {verb}, menunjukkan traksi bisnis yang {adj}."
            ]
            verb = random.choice(self.vocab["verbs_growth"])
            adj = random.choice(self.vocab["adjectives_strong"])
            opener = random.choice(self.vocab["openers_positive"])
            conn = random.choice(self.vocab["connectors"])
            result = random.choice(templates).format(verb=verb, adj=adj, opener=opener, conn=conn)

        elif intent == "revenue_negative":
            templates = [
                "Pendapatan {verb} cukup {adj}. Evaluasi ulang strategi pricing atau tagihan tertunda.",
                "{opener} kontraksi pada arus kas. Tren finansial sedang {adj}.",
                "Kesehatan finansial {verb}. Diperlukan mitigasi risiko segera."
            ]
            verb = random.choice(self.vocab["verbs_decline"])
            adj = random.choice(self.vocab["adjectives_worrying"])
            opener = random.choice(self.vocab["openers_negative"])
            result = random.choice(templates).format(verb=verb, adj=adj, opener=opener)
            
        elif intent == "forecast_insight":
            templates = [
                "Model prediksi memperkirakan tren yang {adj} hingga akhir kuartal, {conn} data historis terkini.",
                "Outlook masa depan terlihat {adj}. {opener} potensi pertumbuhan berkelanjutan.",
                "Prakiraan menunjukkan stabilitas yang {adj}, namun waspadai volatilitas pasar."
            ]
            adj = random.choice(self.vocab["adjectives_steady"] + self.vocab["adjectives_strong"])
            conn = random.choice(self.vocab["connectors"])
            opener = random.choice(self.vocab["openers_positive"])
            result = random.choice(templates).format(adj=adj, conn=conn, opener=opener)

        elif intent == "env_stable":
            templates = [
                "Kualitas perairan dalam kondisi {adj}. Parameter sensor menunjukkan pola yang {adj2}.",
                "{opener} kesehatan ekosistem terpantau {adj}. Tidak ada anomali mayor.",
                "Monitoring lingkungan menunjukkan status {adj}, mendukung operasional yang aman."
            ]
            adj = random.choice(self.vocab["adjectives_steady"])
            adj2 = random.choice(self.vocab["adjectives_strong"] + ["normal"])
            opener = random.choice(self.vocab["openers_positive"])
            result = random.choice(templates).format(adj=adj, adj2=adj2, opener=opener)

        elif intent == "env_anomaly":
            templates = [
                "{opener} deteksi parameter ekstrem pada {count} buoy. Waspadai dampak terhadap {term}.",
                "Anomali kualitas air teridentifikasi. Fluktuasi nilai sensor terlihat {adj}.",
                "Kondisi lingkungan {verb} secara lokal. Perlu inspeksi fisik pada titik pantau."
            ]
            opener = random.choice(self.vocab["openers_negative"])
            term = random.choice(self.vocab["env_terms"])
            adj = random.choice(self.vocab["adjectives_worrying"])
            verb = "berubah"
            result = random.choice(templates).format(opener=opener, count=context.get('count', 'beberapa'), term=term, adj=adj, verb=verb)

        elif intent == "admin_summary":
            templates = [
                "Administrasi sistem berjalan {adj}. {count} pengguna baru telah ditambahkan minggu ini.",
                "{opener} aktivitas pengguna dalam batas wajar. {count} entri log baru tercatat.",
                "Manajemen akses pengguna terpantau {adj}. Sistem beroperasi optimal."
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
        
        # Find strong correlations (> 0.7 or < -0.7)
        strong_pairs = []
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                val = corr_matrix.iloc[i, j]
                if abs(val) >= 0.7:
                    c1 = corr_matrix.columns[i]
                    c2 = corr_matrix.columns[j]
                    strong_pairs.append((c1, c2, val))
        
        if strong_pairs:
            # Sort by strength
            strong_pairs.sort(key=lambda x: abs(x[2]), reverse=True)
            top = strong_pairs[0]
            
            relation = "Positif Kuat" if top[2] > 0 else "Negatif Kuat"
            desc = f"Terdeteksi hubungan **{relation}** ({top[2]}) antara **{top[0]}** dan **{top[1]}**. "
            
            if top[2] > 0:
                desc += "Kenaikan pada satu variabel cenderung diikuti kenaikan variabel lainnya. Sinergi ini dapat dimanfaatkan untuk optimasi."
            else:
                desc += "Kenaikan salah satu variabel menekan variabel lainnya. Waspadai trade-off ini dalam strategi operasional."
                
            insights.append({"title": "🔗 Korelasi Dominan", "desc": desc, "type": "critical"})
        else:
             insights.append({"title": "🔗 Pola Tersebar", "desc": "Tidak ditemukan korelasi linear yang kuat antar variabel utama. Data menunjukkan independensi yang tinggi.", "type": "info"})
             
        return {"insights": insights}
