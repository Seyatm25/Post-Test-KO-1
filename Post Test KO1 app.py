import streamlit as st
import time

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(page_title="Flowchart Auto-Analyzer 2D", page_icon="🧪", layout="wide")

# ================= CSS UNTUK TABUNG 2D MURNI =================
st.markdown("""
<style>
    .tube-wrap { display: flex; justify-content: center; height: 350px; padding-top: 20px;}
    .tube-glass { 
        width: 80px; 
        height: 300px; 
        border: 4px solid #cbd5e1; 
        border-top: none; 
        border-radius: 0 0 40px 40px; 
        position: relative; 
        overflow: hidden;
        background: transparent;
    }
    .tube-liquid { 
        position: absolute; 
        bottom: 0; left: 0; right: 0; 
        transition: height 0.5s ease, background 0.5s ease; 
    }
    .precipitate-layer { position: absolute; bottom: 0; left: 0; right: 0; height: 40px; background-color: rgba(0,0,0,0.5); }
    .cloudy-layer { position: absolute; top: 0; bottom: 0; left: 0; right: 0; background-color: rgba(255,255,255,0.6); }
    .bubble-fx { position: absolute; background: rgba(0,0,0,0.2); border-radius: 50%; width: 8px; height: 8px; animation: floatUp 1.2s infinite ease-in; }
    @keyframes floatUp { 0% { bottom: 0px; opacity: 1; } 100% { bottom: 250px; opacity: 0; } }
</style>
""", unsafe_allow_html=True)

def render_tube(tinggi, warna, efek):
    e_html = ""
    if efek == "precipitate":
        e_html = "<div class='precipitate-layer'></div>"
    elif efek == "cloudy":
        e_html = "<div class='cloudy-layer'></div>"
    elif efek == "bubbles":
        e_html = "<div class='bubble-fx' style='left:20px;'></div><div class='bubble-fx' style='left:50px; animation-delay:0.4s;'></div>"
        
    return f"<div class='tube-wrap'><div class='tube-glass'><div class='tube-liquid' style='height:{tinggi}; background:{warna};'>{e_html}</div></div></div>"

# ================= DATABASE WARNA REAGEN =================
reagen_colors = {
    "Ceric Nitrat": "#facc15", 
    "Pereaksi Jones": "#f97316", 
    "Pereaksi Lucas": "#f8fafc", 
    "Pereaksi Lucas (Panas)": "#f8fafc", 
    "Na-Bisulfit": "#f8fafc", 
    "Pereaksi Fehling": "#3b82f6", 
    "Pereaksi Schiff": "#f8fafc",
    "Uji Iodoform": "#f8fafc",
    "Hidroksilamin (Uji Ester)": "#f8fafc",
    "Uji Barit (NaHCO3)": "#f8fafc"
}

# ================= ALUR LOGIKA SESUAI FLOWCHART =================
# Menyimpan urutan spesifik pengujian untuk tiap senyawa berdasarkan decision tree
flowchart_paths = {
    "1-Butanol": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas (Panas)"],
    "2-Butanol": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas (Panas)", "Uji Iodoform"],
    "t-Butil Alkohol": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas"],
    "Formaldehida": ["Ceric Nitrat", "Na-Bisulfit", "Pereaksi Fehling", "Pereaksi Schiff"],
    "Aseton": ["Ceric Nitrat", "Na-Bisulfit", "Pereaksi Fehling", "Uji Iodoform"],
    "Etil Asetat": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)"],
    "Asam Asetat": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)", "Uji Barit (NaHCO3)"],
    "Heksana": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)", "Uji Barit (NaHCO3)"]
}

# Menyimpan hasil dari masing-masing langkah untuk senyawa tersebut
database_reaksi = {
    "1-Butanol": {
        "Ceric Nitrat": {"hasil": "(+) Merah Ceri", "alasan": "Positif gugus alkohol.", "warna_akhir": "#ef4444", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(+) Hijau", "alasan": "Alkohol primer dapat dioksidasi.", "warna_akhir": "#10b981", "efek": "none"},
        "Pereaksi Lucas (Panas)": {"hasil": "(-) Bening", "alasan": "Karbokation primer tidak stabil, tidak bereaksi meski dipanaskan.", "warna_akhir": "#f8fafc", "efek": "none"}
    },
    "2-Butanol": {
        "Ceric Nitrat": {"hasil": "(+) Merah Ceri", "alasan": "Positif gugus alkohol.", "warna_akhir": "#ef4444", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(+) Hijau", "alasan": "Alkohol sekunder dioksidasi menjadi keton.", "warna_akhir": "#10b981", "efek": "none"},
        "Pereaksi Lucas (Panas)": {"hasil": "(+) Emulsi Putih", "alasan": "Bereaksi moderat membentuk alkil klorida setelah dipanaskan.", "warna_akhir": "#e2e8f0", "efek": "cloudy"},
        "Uji Iodoform": {"hasil": "(+) Endapan Kuning", "alasan": "Memiliki struktur metil karbinol yang bereaksi dengan I2/NaOH.", "warna_akhir": "#fef08a", "efek": "precipitate"}
    },
    "t-Butil Alkohol": {
        "Ceric Nitrat": {"hasil": "(+) Merah Ceri", "alasan": "Positif gugus alkohol.", "warna_akhir": "#ef4444", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(-) Tetap Jingga", "alasan": "Alkohol tersier tidak dapat dioksidasi.", "warna_akhir": "#f97316", "efek": "none"},
        "Pereaksi Lucas": {"hasil": "(+) Emulsi Putih (Seketika)", "alasan": "Karbokation tersier stabil, bereaksi substitusi instan tanpa pemanasan.", "warna_akhir": "#94a3b8", "efek": "cloudy"}
    },
    "Formaldehida": {
        "Ceric Nitrat": {"hasil": "(-) Kuning", "alasan": "Bukan golongan alkohol bebas.", "warna_akhir": "#facc15", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(+) Emulsi/Endapan Putih", "alasan": "Adisi nukleofilik positif menandakan adanya aldehid/keton.", "warna_akhir": "#ffffff", "efek": "precipitate"},
        "Pereaksi Fehling": {"hasil": "(+) Merah Bata", "alasan": "Mereduksi ion Cu(II) setelah dipanaskan (khas Aldehid).", "warna_akhir": "#b91c1c", "efek": "precipitate"},
        "Pereaksi Schiff": {"hasil": "(+) Ungu / Magenta", "alasan": "Bereaksi spesifik memulihkan warna fuksin Schiff.", "warna_akhir": "#d946ef", "efek": "none"}
    },
    "Aseton": {
        "Ceric Nitrat": {"hasil": "(-) Kuning", "alasan": "Bukan alkohol.", "warna_akhir": "#facc15", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(+) Emulsi/Endapan Putih", "alasan": "Golongan karbonil (keton) berekasi adisi.", "warna_akhir": "#ffffff", "efek": "precipitate"},
        "Pereaksi Fehling": {"hasil": "(-) Tetap Biru", "alasan": "Keton tidak memiliki sifat reduktor, mengeliminasi kemungkinan aldehid.", "warna_akhir": "#3b82f6", "efek": "none"},
        "Uji Iodoform": {"hasil": "(+) Endapan Kuning", "alasan": "Keton dengan gugus metil spesifik menghasilkan kristal iodoform.", "warna_akhir": "#fef08a", "efek": "precipitate"}
    },
    "Etil Asetat": {
        "Ceric Nitrat": {"hasil": "(-) Kuning", "alasan": "Bukan alkohol.", "warna_akhir": "#facc15", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(-) Bening", "alasan": "Bukan aldehid/keton (karbonil ester tidak reaktif).", "warna_akhir": "#f8fafc", "efek": "none"},
        "Hidroksilamin (Uji Ester)": {"hasil": "(+) Merah Violet", "alasan": "Ester bereaksi dengan hidroksilamin dan FeCl3 membentuk asam hidroksamat berwarna ungu/violet.", "warna_akhir": "#c026d3", "efek": "none"}
    },
    "Asam Asetat": {
        "Ceric Nitrat": {"hasil": "(-) Kuning", "alasan": "Bukan alkohol.", "warna_akhir": "#facc15", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(-) Bening", "alasan": "Bukan aldehid/keton.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Hidroksilamin (Uji Ester)": {"hasil": "(-) Bening", "alasan": "Bukan golongan ester.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Uji Barit (NaHCO3)": {"hasil": "(+) Gelembung & Keruh", "alasan": "Asam karboksilat bereaksi membebaskan gas CO2 yang mengeruhkan air barit.", "warna_akhir": "#f8fafc", "efek": "bubbles"}
    },
    "Heksana": {
        "Ceric Nitrat": {"hasil": "(-) Kuning", "alasan": "Bukan alkohol.", "warna_akhir": "#facc15", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(-) Bening", "alasan": "Bukan aldehid/keton.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Hidroksilamin (Uji Ester)": {"hasil": "(-) Bening", "alasan": "Bukan ester.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Uji Barit (NaHCO3)": {"hasil": "(-) Bening", "alasan": "Bukan asam. Senyawa hidrokarbon jenuh bersifat inert (Heksana terkonfirmasi secara eliminasi).", "warna_akhir": "#f8fafc", "efek": "none"}
    }
}


# ================= UI UTAMA =================
st.title("🔀 Smart Flowchart Auto-Analyzer 2D")
st.write("Sistem ini mensimulasikan penelusuran **Skema Identifikasi Kualitatif** yang presisi. Mesin akan otomatis menavigasi jalur *decision tree* (Ceric Nitrat -> Jones -> Lucas, dst) untuk menemukan identitas senyawa.")

st.divider()

senyawa = st.selectbox("Pilih Senyawa yang Akan Diuji (Sebagai *Blind Sample*):", ["-- Pilih Senyawa --"] + list(flowchart_paths.keys()))

if st.button("Jalankan Alur Identifikasi 🚀", type="primary"):
    if senyawa == "-- Pilih Senyawa --":
        st.warning("⚠️ Harap pilih senyawa terlebih dahulu!")
    else:
        st.write("---")
        col_visual, col_log = st.columns([1, 2.5])
        
        with col_visual:
            st.markdown(f"<h4 style='text-align: center;'>Visual Lab</h4>", unsafe_allow_html=True)
            tube_placeholder = st.empty() 
            status_placeholder = st.empty()
            
        with col_log:
            st.markdown("#### 📑 Logbook Penelusuran (Sesuai Flowchart)")
            log_container = st.container()
            
        # LOOP PENGUJIAN SESUAI JALUR FLOWCHART
        urutan_tes = flowchart_paths[senyawa]
        
        for i, pereaksi in enumerate(urutan_tes):
            # 1. Animasi Kuras & Tambah Sampel
            tube_placeholder.markdown(render_tube("30%", "#f1f5f9", "none"), unsafe_allow_html=True)
            status_placeholder.markdown(f"<div style='text-align:center;'><em>Menyiapkan sampel untuk {pereaksi}...</em></div>", unsafe_allow_html=True)
            time.sleep(0.5)
            
            # 2. Animasi Memasukkan Reagen
            warna_reagen = reagen_colors[pereaksi]
            tube_placeholder.markdown(render_tube("65%", warna_reagen, "none"), unsafe_allow_html=True)
            status_placeholder.markdown(f"<div style='text-align:center;'><em>Meneteskan {pereaksi}...</em></div>", unsafe_allow_html=True)
            time.sleep(0.8)
            
            # 3. Animasi Hasil Reaksi Akhir
            res = database_reaksi[senyawa][pereaksi]
            tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
            status_placeholder.markdown(f"<div style='text-align:center; font-weight:bold;'>Selesai direaksikan!</div>", unsafe_allow_html=True)
            time.sleep(0.6)
            
            # 4. Cetak Logbook
            if "(+)" in res["hasil"]:
                log_container.success(f"**Tahap {i+1}: {pereaksi}** ➔ **{res['hasil']}**\n\n*Jalur Flowchart:* {res['alasan']}")
            else:
                log_container.error(f"**Tahap {i+1}: {pereaksi}** ➔ **{res['hasil']}**\n\n*Jalur Flowchart:* {res['alasan']}")
            
            time.sleep(1.2) 
            
        # Selesai: Kesimpulan Identifikasi
        status_placeholder.empty()
        tube_placeholder.markdown(render_tube("0%", "transparent", "none"), unsafe_allow_html=True)
        log_container.info(f"🎉 **KESIMPULAN:** Berdasarkan alur eliminasi dan uji spesifik, senyawa *blind sample* ini terkonfirmasi sah sebagai **{senyawa.upper()}**.")
