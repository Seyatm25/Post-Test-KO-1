import streamlit as st
import time

# --- Setup halaman ---
st.set_page_config(page_title="Auto-Analyzer Kimia", page_icon="🧪", layout="wide")

# --- Konstanta dan Database ---
REAGEN_COLORS = {
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

# Jalur identifikasi berdasarkan flowchart
FLOWCHART_PATHS = {
    "1-Butanol": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas (Panas)"],
    "2-Butanol": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas (Panas)", "Uji Iodoform"],
    "t-Butil Alkohol": ["Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas"],
    "Formaldehida": ["Ceric Nitrat", "Na-Bisulfit", "Pereaksi Fehling", "Pereaksi Schiff"],
    "Aseton": ["Ceric Nitrat", "Na-Bisulfit", "Pereaksi Fehling", "Uji Iodoform"],
    "Etil Asetat": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)"],
    "Asam Asetat": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)", "Uji Barit (NaHCO3)"],
    "Heksana": ["Ceric Nitrat", "Na-Bisulfit", "Hidroksilamin (Uji Ester)", "Uji Barit (NaHCO3)"]
}

# Data hasil reaksi, alasan, dan efek visual
REAKSI_DB = {
    "1-Butanol": {
        "Ceric Nitrat": {"hasil": "(+) Merah Ceri", "reaksi": r"$R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3$", "alasan": "Gugus -OH bebas bereaksi menggantikan ligan nitrat pada ion Cerium(IV).", "warna_akhir": "#ef4444", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(+) Hijau", "reaksi": r"$3 R-CH_2OH + 2 CrO_3 + 3 H_2SO_4 \rightarrow 3 R-CHO + Cr_2(SO_4)_3 + 6 H_2O$", "alasan": "Alkohol primer dioksidasi kuat menjadi asam karboksilat, mereduksi Cr(VI) menjadi Cr(III).", "warna_akhir": "#10b981", "efek": "none"},
        "Pereaksi Lucas (Panas)": {"hasil": "(-) Bening", "reaksi": r"$R-CH_2OH + HCl \xrightarrow{ZnCl_2, \Delta} \text{Tidak terjadi endapan}$", "alasan": "Karbokation primer sangat tidak stabil. Reaksi SN1 tidak berjalan meski dipanaskan.", "warna_akhir": "#f8fafc", "efek": "none"}
    },
    "2-Butanol": {
        "Ceric Nitrat": {"hasil": "(+) Merah Ceri", "reaksi": r"$R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3$", "alasan": "Ikatan koordinasi terbentuk antara oksigen hidroksil dengan logam Cerium.", "warna_akhir": "#ef4444", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(+) Hijau", "reaksi": r"$3 R_2CH-OH + 2 CrO_3 + 3 H_2SO_4 \rightarrow 3 R_2C=O + Cr_2(SO_4)_3 + 6 H_2O$", "alasan": "Alkohol sekunder dioksidasi menjadi keton.", "warna_akhir": "#10b981", "efek": "none"},
        "Pereaksi Lucas (Panas)": {"hasil": "(+) Emulsi Putih", "reaksi": r"$R_2CH-OH + HCl \xrightarrow{ZnCl_2} R_2CH-Cl \downarrow + H_2O$", "alasan": "Karbokation sekunder butuh pemanasan untuk mempercepat pembentukan alkil klorida.", "warna_akhir": "#e2e8f0", "efek": "cloudy"},
        "Uji Iodoform": {"hasil": "(+) Endapan Kuning", "reaksi": r"$R-CH(OH)-CH_3 + 4 I_2 + 6 NaOH \rightarrow CHI_3 \downarrow + R-COONa + 5 NaI + 5 H_2O$", "alasan": "Metil karbinol dioksidasi iodin menjadi metil keton, lalu tersubstitusi menjadi iodoform.", "warna_akhir": "#fef08a", "efek": "precipitate"}
    },
    "t-Butil Alkohol": {
        "Ceric Nitrat": {"hasil": "(+) Merah Ceri", "reaksi": r"$R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3$", "alasan": "Terdapat gugus -OH bebas yang membentuk kompleks merah.", "warna_akhir": "#ef4444", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(-) Tetap Jingga", "reaksi": r"$R_3C-OH + CrO_3 + H^+ \rightarrow \text{Tidak bereaksi}$", "alasan": "Alkohol tersier tidak memiliki atom hidrogen alfa, tidak bisa dioksidasi.", "warna_akhir": "#f97316", "efek": "none"},
        "Pereaksi Lucas": {"hasil": "(+) Emulsi Putih (Seketika)", "reaksi": r"$R_3C-OH + HCl \xrightarrow{ZnCl_2} R_3C-Cl \downarrow + H_2O$", "alasan": "Karbokation tersier sangat stabil. Reaksi (SN1) terjadi seketika.", "warna_akhir": "#94a3b8", "efek": "cloudy"}
    },
    "Formaldehida": {
        "Ceric Nitrat": {"hasil": "(-) Kuning", "reaksi": r"$HCHO + [Ce(NO_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}$", "alasan": "Aldehid tidak memiliki gugus hidroksil alifatik.", "warna_akhir": "#facc15", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(+) Endapan Putih", "reaksi": r"$H-CHO + NaHSO_3 \rightarrow H_2C(OH)SO_3Na \downarrow$", "alasan": "Nukleofil bisulfit menyerang karbonil membentuk garam bisulfit padat.", "warna_akhir": "#ffffff", "efek": "precipitate"},
        "Pereaksi Fehling": {"hasil": "(+) Merah Bata", "reaksi": r"$H-CHO + 2 Cu^{2+} + 5 OH^- \rightarrow H-COO^- + Cu_2O \downarrow + 3 H_2O$", "alasan": "Aldehid adalah reduktor kuat yang mereduksi ion Cu(II).", "warna_akhir": "#b91c1c", "efek": "precipitate"},
        "Pereaksi Schiff": {"hasil": "(+) Ungu / Magenta", "reaksi": r"$\text{Aldehid} + \text{Reagen Schiff} \rightarrow \text{Kompleks warna magenta}$", "alasan": "Reaksi adisi spesifik yang memulihkan pewarna p-rosanilin.", "warna_akhir": "#d946ef", "efek": "none"}
    },
    "Aseton": {
        "Ceric Nitrat": {"hasil": "(-) Kuning", "reaksi": r"$CH_3COCH_3 + [Ce(NO_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}$", "alasan": "Keton tidak memiliki gugus hidroksil.", "warna_akhir": "#facc15", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(+) Endapan Putih", "reaksi": r"$CH_3-CO-CH_3 + NaHSO_3 \rightarrow (CH_3)_2C(OH)SO_3Na \downarrow$", "alasan": "Halangan sterik aseton cukup rendah untuk mengalami adisi bisulfit.", "warna_akhir": "#ffffff", "efek": "precipitate"},
        "Pereaksi Fehling": {"hasil": "(-) Tetap Biru", "reaksi": r"$CH_3-CO-CH_3 + Cu^{2+} \rightarrow \text{Tidak direduksi}$", "alasan": "Keton tidak memiliki hidrogen reduktif pada karbon karbonil.", "warna_akhir": "#3b82f6", "efek": "none"},
        "Uji Iodoform": {"hasil": "(+) Endapan Kuning", "reaksi": r"$CH_3-CO-CH_3 + 3 I_2 + 4 NaOH \rightarrow CHI_3 \downarrow + CH_3COONa + 3 NaI + 3 H_2O$", "alasan": "Hidrogen alfa pada metil keton tersubstitusi oleh iodin.", "warna_akhir": "#fef08a", "efek": "precipitate"}
    },
    "Etil Asetat": {
        "Ceric Nitrat": {"hasil": "(-) Kuning", "reaksi": r"$\text{Ester} + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}$", "alasan": "Gugus ester inert terhadap uji alkohol.", "warna_akhir": "#facc15", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(-) Bening", "reaksi": r"$\text{Ester} + NaHSO_3 \rightarrow \text{Tidak bereaksi}$", "alasan": "Resonansi menstabilkan karbon karbonil sehingga tidak reaktif terhadap bisulfit.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Hidroksilamin (Uji Ester)": {"hasil": "(+) Merah Violet", "reaksi": r"$R-COOR' \xrightarrow{NH_2OH} R-CONHOH \xrightarrow{FeCl_3} Fe(R-CONHO)_3$", "alasan": "Ester diubah menjadi asam hidroksamat yang mengikat ion Fe3+.", "warna_akhir": "#c026d3", "efek": "none"}
    },
    "Asam Asetat": {
        "Ceric Nitrat": {"hasil": "(-) Kuning", "reaksi": r"$CH_3COOH + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}$", "alasan": "Oksigen karboksil kurang nukleofilik akibat efek resonansi.", "warna_akhir": "#facc15", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(-) Bening", "reaksi": r"$CH_3COOH + NaHSO_3 \rightarrow \text{Tidak bereaksi}$", "alasan": "Bukan golongan aldehid atau keton.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Hidroksilamin (Uji Ester)": {"hasil": "(-) Bening", "reaksi": r"$CH_3COOH \xrightarrow{NH_2OH/FeCl_3} \text{Tidak bereaksi}$", "alasan": "Asam karboksilat tidak memicu pembentukan kompleks hidroksamat.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Uji Barit (NaHCO3)": {"hasil": "(+) Gelembung & Keruh", "reaksi": r"$CH_3COOH + NaHCO_3 \rightarrow CH_3COONa + H_2O + CO_2 \uparrow$", "alasan": "Asam mendonasikan proton untuk mengurai bikarbonat melepaskan gas CO2.", "warna_akhir": "#f8fafc", "efek": "bubbles"}
    },
    "Heksana": {
        "Ceric Nitrat": {"hasil": "(-) Kuning", "reaksi": r"$\text{Heksana} \rightarrow \text{Tidak bereaksi}$", "alasan": "Tidak ada gugus fungsi -OH.", "warna_akhir": "#facc15", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(-) Bening", "reaksi": r"$\text{Heksana} \rightarrow \text{Tidak bereaksi}$", "alasan": "Tidak ada gugus karbonil.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Hidroksilamin (Uji Ester)": {"hasil": "(-) Bening", "reaksi": r"$\text{Heksana} \rightarrow \text{Tidak bereaksi}$", "alasan": "Bukan gugus ester.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Uji Barit (NaHCO3)": {"hasil": "(-) Bening", "reaksi": r"$\text{Heksana} \rightarrow \text{Tidak bereaksi}$", "alasan": "Senyawa hidrokarbon jenuh inert terhadap pereaksi ini.", "warna_akhir": "#f8fafc", "efek": "none"}
    }
}

# --- Fungsi Helper ---
def inject_custom_css():
    """Injeksi CSS untuk merender tabung reaksi 2D."""
    st.markdown("""
    <style>
        .tube-wrap { display: flex; justify-content: center; height: 350px; padding-top: 20px;}
        .tube-glass { 
            width: 80px; height: 300px; border: 4px solid #cbd5e1; 
            border-top: none; border-radius: 0 0 40px 40px; 
            position: relative; overflow: hidden; background: transparent;
        }
        .tube-liquid { 
            position: absolute; bottom: 0; left: 0; right: 0; 
            transition: height 1.2s ease, background 1.2s ease; 
        }
        .precipitate-layer { position: absolute; bottom: 0; width: 100%; height: 40px; background: rgba(0,0,0,0.5); }
        .cloudy-layer { position: absolute; inset: 0; background: rgba(255,255,255,0.6); }
        .bubble-fx { 
            position: absolute; background: rgba(0,0,0,0.2); border-radius: 50%; 
            width: 8px; height: 8px; animation: floatUp 1.8s infinite ease-in; 
        }
        @keyframes floatUp { 0% { bottom: 0px; opacity: 1; } 100% { bottom: 250px; opacity: 0; } }
    </style>
    """, unsafe_allow_html=True)

def build_tube_html(height, color, effect="none"):
    """Mengembalikan string HTML untuk merender status tabung."""
    effect_html = ""
    if effect == "precipitate":
        effect_html = "<div class='precipitate-layer'></div>"
    elif effect == "cloudy":
        effect_html = "<div class='cloudy-layer'></div>"
    elif effect == "bubbles":
        effect_html = "<div class='bubble-fx' style='left:20px;'></div><div class='bubble-fx' style='left:50px; animation-delay:0.5s;'></div>"
        
    return f"""
    <div class='tube-wrap'>
        <div class='tube-glass'>
            <div class='tube-liquid' style='height:{height}; background:{color};'>{effect_html}</div>
        </div>
    </div>
    """

def refresh_app():
    """Fungsi pembantu untuk trigger rerun yang kompatibel dengan berbagai versi Streamlit."""
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()

# --- Inisialisasi State ---
def init_session():
    if 'is_running' not in st.session_state:
        st.session_state.is_running = False
        st.session_state.target_compound = ""
        st.session_state.step_index = 0
        st.session_state.logs = []
        st.session_state.play_animation = False

init_session()
inject_custom_css()

# --- Layout UI Utama ---
st.title("🔀 Flowchart Auto-Analyzer (Step-by-Step)")
st.write("Simulasi identifikasi senyawa organik kualitatif. Tekan tombol *Next* untuk melanjutkan ke pereaksi berikutnya.")
st.divider()

# Tampilan Menu Awal
if not st.session_state.is_running:
    selected_compound = st.selectbox("Pilih sampel uji:", ["-- Pilih Senyawa --"] + list(FLOWCHART_PATHS.keys()))
    
    if st.button("Mulai Identifikasi 🚀", type="primary"):
        if selected_compound != "-- Pilih Senyawa --":
            st.session_state.is_running = True
            st.session_state.target_compound = selected_compound
            st.session_state.step_index = 0
            st.session_state.logs = []
            st.session_state.play_animation = True
            refresh_app()
        else:
            st.warning("⚠️ Pilih senyawa terlebih dahulu.")

# Tampilan Saat Simulasi Berjalan
else:
    compound = st.session_state.target_compound
    path_sequence = FLOWCHART_PATHS[compound]

    col1, col2 = st.columns([1, 2.5])
    
    with col1:
        st.markdown("<h4 style='text-align: center;'>Visual Lab</h4>", unsafe_allow_html=True)
        tube_ui = st.empty() 
        status_ui = st.empty()
        
    with col2:
        st.markdown("#### 📑 Logbook & Analisis")
        log_view = st.container()

    # Cetak history log
    with log_view:
        for log in st.session_state.logs:
            if "(+)" in log["hasil"]:
                st.success(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n**Reaksi:**\n{log['reaksi']}\n\n**Pembahasan:** {log['alasan']}")
            else:
                st.error(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n**Reaksi:**\n{log['reaksi']}\n\n**Pembahasan:** {log['alasan']}")

    # --- Eksekusi Animasi per Langkah ---
    if st.session_state.play_animation and st.session_state.step_index < len(path_sequence):
        current_reagent = path_sequence[st.session_state.step_index]
        reagent_color = REAGEN_COLORS[current_reagent]
        reaction_data = REAKSI_DB[compound][current_reagent]
        
        # Animasi 1: Kuras & isi sampel
        tube_ui.markdown(build_tube_html("30%", "#f1f5f9"), unsafe_allow_html=True)
        status_ui.markdown(f"<div style='text-align:center;'>Menyiapkan uji {current_reagent}...</div>", unsafe_allow_html=True)
        time.sleep(1.0)
        
        # Animasi 2: Teteskan reagen
        tube_ui.markdown(build_tube_html("65%", reagent_color), unsafe_allow_html=True)
        status_ui.markdown(f"<div style='text-align:center;'>Meneteskan {current_reagent}...</div>", unsafe_allow_html=True)
        time.sleep(1.5)
        
        # Animasi 3: Hasil reaksi
        tube_ui.markdown(build_tube_html("65%", reaction_data["warna_akhir"], reaction_data["efek"]), unsafe_allow_html=True)
        status_ui.markdown("<div style='text-align:center; font-weight:bold;'>Mengamati hasil...</div>", unsafe_allow_html=True)
        time.sleep(1.2)
        
        # Simpan ke log
        st.session_state.logs.append({
            "step": st.session_state.step_index + 1,
            "pereaksi": current_reagent,
            "hasil": reaction_data["hasil"],
            "reaksi": reaction_data["reaksi"],
            "alasan": reaction_data["alasan"]
        })
        
        st.session_state.step_index += 1
        st.session_state.play_animation = False
        refresh_app()

    # --- Mode Menunggu Input User (Animasi Berhenti) ---
    elif not st.session_state.play_animation:
        # Kembalikan gambar tabung terakhir
        if st.session_state.step_index > 0:
            last_reagent = path_sequence[st.session_state.step_index - 1]
            last_data = REAKSI_DB[compound][last_reagent]
            tube_ui.markdown(build_tube_html("65%", last_data["warna_akhir"], last_data["efek"]), unsafe_allow_html=True)
        
        # Tombol Next jika masih ada sisa pengujian
        if st.session_state.step_index < len(path_sequence):
            next_reagent = path_sequence[st.session_state.step_index]
            status_ui.markdown("<div style='text-align:center; color:#475569;'>Menunggu tindakan...</div>", unsafe_allow_html=True)
            
            with col1:
                st.write("") 
                if st.button(f"Lanjutkan ke {next_reagent} ⏭️", use_container_width=True, type="primary"):
                    st.session_state.play_animation = True
                    refresh_app()
                    
        # Tombol Reset jika semua pengujian selesai
        else:
            status_ui.markdown("<div style='text-align:center; font-weight:bold; color:#10b981;'>Identifikasi Selesai!</div>", unsafe_allow_html=True)
            log_view.info(f"🎉 **KESIMPULAN:** Senyawa teridentifikasi sebagai **{compound.upper()}**.")
            
            with col1:
                st.write("")
                if st.button("🔄 Uji Senyawa Lain", use_container_width=True):
                    st.session_state.is_running = False
                    refresh_app()
