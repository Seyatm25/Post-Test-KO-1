import streamlit as st
import time

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(page_title="Flowchart Auto-Analyzer 2D", page_icon="🧪", layout="wide")

# ================= CSS UNTUK TABUNG 2D =================
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
        transition: height 1.2s ease, background 1.2s ease; 
    }
    .precipitate-layer { position: absolute; bottom: 0; left: 0; right: 0; height: 40px; background-color: rgba(0,0,0,0.5); }
    .cloudy-layer { position: absolute; top: 0; bottom: 0; left: 0; right: 0; background-color: rgba(255,255,255,0.6); }
    .bubble-fx { position: absolute; background: rgba(0,0,0,0.2); border-radius: 50%; width: 8px; height: 8px; animation: floatUp 1.8s infinite ease-in; }
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
        e_html = "<div class='bubble-fx' style='left:20px;'></div><div class='bubble-fx' style='left:50px; animation-delay:0.5s;'></div>"
        
    return f"<div class='tube-wrap'><div class='tube-glass'><div class='tube-liquid' style='height:{tinggi}; background:{warna};'>{e_html}</div></div></div>"

# ================= DATABASE LOGIKA & WARNA =================
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
        "Hidroksilamin (Uji Ester)": {"hasil": "(+) Merah Violet", "alasan": "Ester bereaksi dengan hidroksilamin dan FeCl3 membentuk kompleks warna ungu/violet.", "warna_akhir": "#c026d3", "efek": "none"}
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
        "Uji Barit (NaHCO3)": {"hasil": "(-) Bening", "alasan": "Bukan asam. Senyawa hidrokarbon jenuh bersifat inert.", "warna_akhir": "#f8fafc", "efek": "none"}
    }
}

# ================= STATE MANAGEMENT (Mesin Waktu Interaktif) =================
if 'test_started' not in st.session_state:
    st.session_state.test_started = False
if 'senyawa_uji' not in st.session_state:
    st.session_state.senyawa_uji = ""
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'log_history' not in st.session_state:
    st.session_state.log_history = []
if 'trigger_animation' not in st.session_state:
    st.session_state.trigger_animation = False

# ================= UI UTAMA =================
st.title("🔀 Smart Flowchart Auto-Analyzer (Mode Step-by-Step)")
st.write("Sistem ini mensimulasikan penelusuran **Skema Identifikasi Kualitatif** langkah demi langkah. Tekan tombol *Next* untuk melanjutkan ke pereaksi berikutnya.")

# Tampilan Awal (Pemilihan Senyawa)
if not st.session_state.test_started:
    st.divider()
    senyawa = st.selectbox("Pilih Senyawa yang Akan Diuji (Sebagai *Blind Sample*):", ["-- Pilih Senyawa --"] + list(flowchart_paths.keys()))
    if st.button("Mulai Identifikasi 🚀", type="primary"):
        if senyawa == "-- Pilih Senyawa --":
            st.warning("⚠️ Harap pilih senyawa terlebih dahulu!")
        else:
            # Mereset dan memulai pengujian baru
            st.session_state.test_started = True
            st.session_state.senyawa_uji = senyawa
            st.session_state.current_step = 0
            st.session_state.log_history = []
            st.session_state.trigger_animation = True
            st.rerun()

# Tampilan Saat Pengujian Berlangsung
else:
    st.write("---")
    senyawa = st.session_state.senyawa_uji
    urutan = flowchart_paths[senyawa]

    col_visual, col_log = st.columns([1, 2.5])
    
    with col_visual:
        st.markdown(f"<h4 style='text-align: center;'>Visual Lab</h4>", unsafe_allow_html=True)
        tube_placeholder = st.empty() 
        status_placeholder = st.empty()
        
    with col_log:
        st.markdown("#### 📑 Logbook Penelusuran")
        log_container = st.container()

    # Mencetak rekam jejak yang sudah dilewati sejauh ini
    with log_container:
        for log in st.session_state.log_history:
            if "(+)" in log["hasil"]:
                st.success(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n*Jalur Flowchart:* {log['alasan']}")
            else:
                st.error(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n*Jalur Flowchart:* {log['alasan']}")

    # ---------------- LOGIKA ANIMASI & TOMBOL NEXT ----------------
    # Jika trigger_animation aktif (Saat pengguna baru tekan Mulai atau menekan tombol Next)
    if st.session_state.trigger_animation and st.session_state.current_step < len(urutan):
        pereaksi = urutan[st.session_state.current_step]
        
        # 1. Animasi Kuras & Tambah Sampel
        tube_placeholder.markdown(render_tube("30%", "#f1f5f9", "none"), unsafe_allow_html=True)
        status_placeholder.markdown(f"<div style='text-align:center;'><em>Menyiapkan sampel untuk {pereaksi}...</em></div>", unsafe_allow_html=True)
        time.sleep(1.0)
        
        # 2. Animasi Meneteskan Reagen
        warna_reagen = reagen_colors[pereaksi]
        tube_placeholder.markdown(render_tube("65%", warna_reagen, "none"), unsafe_allow_html=True)
        status_placeholder.markdown(f"<div style='text-align:center;'><em>Meneteskan {pereaksi}...</em></div>", unsafe_allow_html=True)
        time.sleep(1.5)
        
        # 3. Animasi Hasil Akhir
        res = database_reaksi[senyawa][pereaksi]
        tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
        status_placeholder.markdown(f"<div style='text-align:center; font-weight:bold;'>Melihat hasil reaksi...</div>", unsafe_allow_html=True)
        time.sleep(1.2)
        
        # Simpan hasil ke dalam log history
        st.session_state.log_history.append({
            "step": st.session_state.current_step + 1,
            "pereaksi": pereaksi,
            "hasil": res["hasil"],
            "alasan": res["alasan"]
        })
        
        # Matikan trigger animasi, naikkan hitungan step, dan muat ulang halaman untuk memunculkan tombol
        st.session_state.current_step += 1
        st.session_state.trigger_animation = False
        st.rerun()

    # Jika animasi sedang TIDAK berjalan (Menunggu pengguna menekan tombol)
    elif not st.session_state.trigger_animation:
        
        # Tampilkan tabung dalam kondisi terakhirnya (bekas uji sebelumnya)
        if st.session_state.current_step > 0:
            last_pereaksi = urutan[st.session_state.current_step - 1]
            res = database_reaksi[senyawa][last_pereaksi]
            tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
        
        # Cek apakah masih ada uji selanjutnya di dalam flowchart
        if st.session_state.current_step < len(urutan):
            next_pereaksi = urutan[st.session_state.current_step]
            status_placeholder.markdown(f"<div style='text-align:center; color:#475569;'>Menunggu konfirmasi tindakan...</div>", unsafe_allow_html=True)
            
            with col_visual:
                st.write("") # Memberi jarak spasial
                # TOMBOL NEXT
                if st.button(f"Lanjutkan ke Uji {next_pereaksi} ⏭️", use_container_width=True, type="primary"):
                    st.session_state.trigger_animation = True
                    st.rerun()
                    
        # Jika semua uji dalam flowchart sudah selesai
        else:
            status_placeholder.markdown(f"<div style='text-align:center; font-weight:bold; color:#10b981;'>Seluruh tahap identifikasi selesai!</div>", unsafe_allow_html=True)
            with log_container:
                st.info(f"🎉 **KESIMPULAN:** Berdasarkan alur eliminasi dan uji spesifik, senyawa *blind sample* ini terkonfirmasi sah sebagai **{senyawa.upper()}**.")
            
            with col_visual:
                st.write("")
                if st.button("🔄 Uji Senyawa Lain", use_container_width=True):
                    st.session_state.test_started = False
                    st.rerun()
