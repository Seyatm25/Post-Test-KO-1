import streamlit as st
import time

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(page_title="Flowchart Auto-Analyzer 2D", page_icon="🧪", layout="wide")

# ================= FUNGSI ANTI-ERROR UNTUK STREAMLIT LAMA =================
def force_rerun():
    if hasattr(st, 'rerun'):
        st.rerun()
    elif hasattr(st, 'experimental_rerun'):
        st.experimental_rerun()
    else:
        st.warning("⚠️ Versi Streamlit sangat usang. Silakan refresh halaman secara manual (F5).")

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

# ================= DATABASE LOGIKA, REAKSI, & WARNA =================
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

# (PENTING: String Reaksi menggunakan r"..." untuk mencegah error Escape Character di Python)
database_reaksi = {
    "1-Butanol": {
        "Ceric Nitrat": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": r"$R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3$", 
            "alasan": "Gugus -OH bebas dari 1-butanol bereaksi menggantikan ligan nitrat pada ion Cerium(IV) membentuk senyawa kompleks koordinasi yang berwarna merah ceri.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Pereaksi Jones": {
            "hasil": "(+) Hijau", 
            "reaksi": r"$3 R-CH_2OH + 2 CrO_3 + 3 H_2SO_4 \rightarrow 3 R-CHO + Cr_2(SO_4)_3 + 6 H_2O$", 
            "alasan": "1-butanol adalah alkohol primer yang memiliki atom hidrogen alfa. Gugus -OH dioksidasi kuat menjadi asam karboksilat, sedangkan Kromium(VI) jingga tereduksi menjadi Kromium(III) hijau.", 
            "warna_akhir": "#10b981", "efek": "none"
        },
        "Pereaksi Lucas (Panas)": {
            "hasil": "(-) Bening", 
            "reaksi": r"$R-CH_2OH + HCl \xrightarrow{ZnCl_2, \Delta} \text{Tidak terjadi endapan}$", 
            "alasan": "Karbokation primer sangat tidak stabil. Reaksi substitusi nukleofilik (SN1) tidak berjalan membentuk alkil klorida yang tak larut, bahkan setelah dibantu pemanasan.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        }
    },
    "2-Butanol": {
        "Ceric Nitrat": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": r"$R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3$", 
            "alasan": "Ikatan koordinasi terbentuk antara atom oksigen pada gugus hidroksil sekunder dengan logam Cerium pusat, menghasilkan warna merah.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Pereaksi Jones": {
            "hasil": "(+) Hijau", 
            "reaksi": r"$3 R_2CH-OH + 2 CrO_3 + 3 H_2SO_4 \rightarrow 3 R_2C=O + Cr_2(SO_4)_3 + 6 H_2O$", 
            "alasan": "2-butanol dioksidasi oleh reagen Jones menjadi keton. Cr(VI) (jingga) tereduksi ke Cr(III) (hijau).", 
            "warna_akhir": "#10b981", "efek": "none"
        },
        "Pereaksi Lucas (Panas)": {
            "hasil": "(+) Emulsi Putih", 
            "reaksi": r"$R_2CH-OH + HCl \xrightarrow{ZnCl_2} R_2CH-Cl \downarrow + H_2O$", 
            "alasan": "Karbokation sekunder memiliki stabilitas menengah. Reaksi butuh pemanasan untuk mempercepat substitusi menjadi alkil klorida yang mengeruhkan larutan.", 
            "warna_akhir": "#e2e8f0", "efek": "cloudy"
        },
        "Uji Iodoform": {
            "hasil": "(+) Endapan Kuning", 
            "reaksi": r"$R-CH(OH)-CH_3 + 4 I_2 + 6 NaOH \rightarrow CHI_3 \downarrow + R-COONa + 5 NaI + 5 H_2O$", 
            "alasan": "2-Butanol adalah metil karbinol yang dioksidasi iodin menjadi metil keton. Gugus metilnya tersubstitusi menjadi kristal iodoform kuning.", 
            "warna_akhir": "#fef08a", "efek": "precipitate"
        }
    },
    "t-Butil Alkohol": {
        "Ceric Nitrat": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": r"$R-OH + [Ce(NO_3)_6]^{2-} \rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3$", 
            "alasan": "Terdapat gugus -OH bebas yang dapat berikatan koordinasi membentuk kompleks merah.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Pereaksi Jones": {
            "hasil": "(-) Tetap Jingga", 
            "reaksi": r"$R_3C-OH + CrO_3 + H^+ \rightarrow \text{Tidak bereaksi}$", 
            "alasan": "Alkohol tersier tidak memiliki atom hidrogen alfa, sehingga sangat kebal dan tidak bisa dioksidasi.", 
            "warna_akhir": "#f97316", "efek": "none"
        },
        "Pereaksi Lucas": {
            "hasil": "(+) Emulsi Putih (Seketika)", 
            "reaksi": r"$R_3C-OH + HCl \xrightarrow{ZnCl_2} R_3C-Cl \downarrow + H_2O$", 
            "alasan": "Membentuk karbokation tersier yang sangat stabil. Reaksi (SN1) terjadi seketika menghasilkan endapan alkil klorida.", 
            "warna_akhir": "#94a3b8", "efek": "cloudy"
        }
    },
    "Formaldehida": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", 
            "reaksi": r"$HCHO + [Ce(NO_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}$", 
            "alasan": "Formaldehida merupakan aldehid dan tidak memiliki gugus hidroksil bebas untuk bereaksi dengan Cerium.", 
            "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(+) Endapan Putih", 
            "reaksi": r"$H-CHO + NaHSO_3 \rightarrow H_2C(OH)SO_3Na \downarrow$", 
            "alasan": "Nukleofil bisulfit menyerang karbonil yang miskin elektron, membentuk garam padatan kristal.", 
            "warna_akhir": "#ffffff", "efek": "precipitate"
        },
        "Pereaksi Fehling": {
            "hasil": "(+) Merah Bata", 
            "reaksi": r"$H-CHO + 2 Cu^{2+} + 5 OH^- \rightarrow H-COO^- + Cu_2O \downarrow + 3 H_2O$", 
            "alasan": "Aldehid adalah reduktor kuat. Ia mereduksi Tembaga(II) sulfat biru menjadi endapan Tembaga(I) oksida (merah bata).", 
            "warna_akhir": "#b91c1c", "efek": "precipitate"
        },
        "Pereaksi Schiff": {
            "hasil": "(+) Ungu / Magenta", 
            "reaksi": r"$\text{Aldehid} + \text{Reagen Schiff} \rightarrow \text{Kompleks warna magenta}$", 
            "alasan": "Reaksi adisi spesifik yang memulihkan pewarna p-rosanilin hidroklorida.", 
            "warna_akhir": "#d946ef", "efek": "none"
        }
    },
    "Aseton": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", 
            "reaksi": r"$CH_3COCH_3 + [Ce(NO_3)_6]^{2-} \rightarrow \text{Tidak bereaksi}$", 
            "alasan": "Keton tidak memiliki gugus hidroksil alkoholik.", 
            "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(+) Endapan Putih", 
            "reaksi": r"$CH_3-CO-CH_3 + NaHSO_3 \rightarrow (CH_3)_2C(OH)SO_3Na \downarrow$", 
            "alasan": "Aseton masih memiliki halangan sterik rendah, sehingga bisa mengalami reaksi adisi membentuk garam bisulfit.", 
            "warna_akhir": "#ffffff", "efek": "precipitate"
        },
        "Pereaksi Fehling": {
            "hasil": "(-) Tetap Biru", 
            "reaksi": r"$CH_3-CO-CH_3 + Cu^{2+} \rightarrow \text{Tidak direduksi}$", 
            "alasan": "Keton tidak memiliki atom hidrogen pada karbon pengikat oksigen sehingga tidak memiliki sifat reduktor.", 
            "warna_akhir": "#3b82f6", "efek": "none"
        },
        "Uji Iodoform": {
            "hasil": "(+) Endapan Kuning", 
            "reaksi": r"$CH_3-CO-CH_3 + 3 I_2 + 4 NaOH \rightarrow CHI_3 \downarrow + CH_3COONa + 3 NaI + 3 H_2O$", 
            "alasan": "Atom hidrogen alfa pada metil keton sangat asam, tersubstitusi oleh Iodin lalu putus membentuk Iodoform kuning.", 
            "warna_akhir": "#fef08a", "efek": "precipitate"
        }
    },
    "Etil Asetat": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", 
            "reaksi": r"$\text{Ester} + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}$", 
            "alasan": "Gugus ester tidak bereaksi dengan uji alkohol.", 
            "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(-) Bening", 
            "reaksi": r"$\text{Ester} + NaHSO_3 \rightarrow \text{Tidak bereaksi}$", 
            "alasan": "Resonansi pasangan elektron bebas dari gugus etoksi menstabilkan karbon karbonil, menjadikannya tidak reaktif terhadap nukleofil lemah.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Hidroksilamin (Uji Ester)": {
            "hasil": "(+) Merah Violet", 
            "reaksi": r"$\text{1. } R-COOR' + NH_2OH \rightarrow R-CONHOH + R'OH \quad \text{2. } 3 R-CONHOH + FeCl_3 \rightarrow Fe(R-CONHO)_3 + 3 HCl$", 
            "alasan": "Ester diubah oleh hidroksilamin menjadi asam hidroksamat yang dapat mengikat ion Fe3+ menghasilkan kompleks berwarna violet.", 
            "warna_akhir": "#c026d3", "efek": "none"
        }
    },
    "Asam Asetat": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", 
            "reaksi": r"$CH_3COOH + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}$", 
            "alasan": "Oksigen karboksil ditarik oleh resonansi ikatan rangkap karbonil, menjadikannya kurang nukleofilik untuk berikatan dengan Cerium.", 
            "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(-) Bening", 
            "reaksi": r"$CH_3COOH + NaHSO_3 \rightarrow \text{Tidak bereaksi}$", 
            "alasan": "Bukan senyawa golongan aldehid atau keton.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Hidroksilamin (Uji Ester)": {
            "hasil": "(-) Bening", 
            "reaksi": r"$CH_3COOH + NH_2OH + FeCl_3 \rightarrow \text{Tidak bereaksi}$", 
            "alasan": "Bukan ester. Asam karboksilat tidak memicu pembentukan asam hidroksamat reaktif di kondisi ini.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Barit (NaHCO3)": {
            "hasil": "(+) Gelembung & Keruh", 
            "reaksi": r"$\text{1. } CH_3COOH + NaHCO_3 \rightarrow CH_3COONa + H_2O + CO_2 \uparrow \quad \text{2. } CO_2 + Ba(OH)_2 \rightarrow BaCO_3 \downarrow + H_2O$", 
            "alasan": "Asam karboksilat mendonasikan proton untuk mengurai bikarbonat. Gas CO2 yang terlepas bereaksi dengan air barit membentuk BaCO3 yang keruh.", 
            "warna_akhir": "#f8fafc", "efek": "bubbles"
        }
    },
    "Heksana": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", "reaksi": r"$\text{Heksana} + \text{Ceric Nitrat} \rightarrow \text{Tidak bereaksi}$", "alasan": "Tidak ada gugus fungsi -OH.", "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(-) Bening", "reaksi": r"$\text{Heksana} + NaHSO_3 \rightarrow \text{Tidak bereaksi}$", "alasan": "Tidak ada gugus karbonil.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Hidroksilamin (Uji Ester)": {
            "hasil": "(-) Bening", "reaksi": r"$\text{Heksana} + NH_2OH \rightarrow \text{Tidak bereaksi}$", "alasan": "Bukan gugus ester.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Barit (NaHCO3)": {
            "hasil": "(-) Bening", "reaksi": r"$\text{Heksana} + NaHCO_3 \rightarrow \text{Tidak bereaksi}$", 
            "alasan": "Senyawa hidrokarbon alifatik (jenuh) bersifat non-polar dan inert. Karena secara berturut-turut gagal bereaksi di seluruh uji fungsional, ini membuktikan senyawanya adalah alkana.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        }
    }
}

# ================= STATE MANAGEMENT =================
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
st.title("🔀 Smart Flowchart Auto-Analyzer (Step-by-Step)")
st.write("Sistem ini mensimulasikan penelusuran Identifikasi Kualitatif langkah demi langkah. Tekan tombol *Next* untuk melanjutkan ke tahap reaksi berikutnya.")

if not st.session_state.test_started:
    st.divider()
    senyawa = st.selectbox("Pilih Senyawa yang Akan Diuji (Sebagai *Blind Sample*):", ["-- Pilih Senyawa --"] + list(flowchart_paths.keys()))
    if st.button("Mulai Identifikasi 🚀", type="primary"):
        if senyawa == "-- Pilih Senyawa --":
            st.warning("⚠️ Harap pilih senyawa terlebih dahulu!")
        else:
            st.session_state.test_started = True
            st.session_state.senyawa_uji = senyawa
            st.session_state.current_step = 0
            st.session_state.log_history = []
            st.session_state.trigger_animation = True
            force_rerun()

else:
    st.write("---")
    senyawa = st.session_state.senyawa_uji
    urutan = flowchart_paths[senyawa]

    col_visual, col_log = st.columns([1, 2.5])
    
    with col_visual:
        st.markdown("<h4 style='text-align: center;'>Visual Lab</h4>", unsafe_allow_html=True)
        tube_placeholder = st.empty() 
        status_placeholder = st.empty()
        
    with col_log:
        st.markdown("#### 📑 Logbook & Analisis Teoritis")
        log_container = st.container()

    with log_container:
        for log in st.session_state.log_history:
            if "(+)" in log["hasil"]:
                st.success(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n**Reaksi:**\n{log['reaksi']}\n\n**Pembahasan:**\n{log['alasan']}")
            else:
                st.error(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n**Reaksi:**\n{log['reaksi']}\n\n**Pembahasan:**\n{log['alasan']}")

    # ---------------- LOGIKA ANIMASI & TOMBOL NEXT ----------------
    if st.session_state.trigger_animation and st.session_state.current_step < len(urutan):
        pereaksi = urutan[st.session_state.current_step]
        
        tube_placeholder.markdown(render_tube("30%", "#f1f5f9", "none"), unsafe_allow_html=True)
        status_placeholder.markdown(f"<div style='text-align:center;'><em>Menyiapkan sampel untuk {pereaksi}...</em></div>", unsafe_allow_html=True)
        time.sleep(1.0)
        
        warna_reagen = reagen_colors[pereaksi]
        tube_placeholder.markdown(render_tube("65%", warna_reagen, "none"), unsafe_allow_html=True)
        status_placeholder.markdown(f"<div style='text-align:center;'><em>Meneteskan {pereaksi}...</em></div>", unsafe_allow_html=True)
        time.sleep(1.5)
        
        res = database_reaksi[senyawa][pereaksi]
        tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
        status_placeholder.markdown("<div style='text-align:center; font-weight:bold;'>Melihat hasil reaksi...</div>", unsafe_allow_html=True)
        time.sleep(1.2)
        
        st.session_state.log_history.append({
            "step": st.session_state.current_step + 1,
            "pereaksi": pereaksi,
            "hasil": res["hasil"],
            "reaksi": res["reaksi"],
            "alasan": res["alasan"]
        })
        
        st.session_state.current_step += 1
        st.session_state.trigger_animation = False
        force_rerun()

    elif not st.session_state.trigger_animation:
        
        if st.session_state.current_step > 0:
            last_pereaksi = urutan[st.session_state.current_step - 1]
            res = database_reaksi[senyawa][last_pereaksi]
            tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
        
        if st.session_state.current_step < len(urutan):
            next_pereaksi = urutan[st.session_state.current_step]
            status_placeholder.markdown("<div style='text-align:center; color:#475569;'>Menunggu konfirmasi pembacaan...</div>", unsafe_allow_html=True)
            
            with col_visual:
                st.write("") 
                if st.button(f"Lanjutkan ke Uji {next_pereaksi} ⏭️", use_container_width=True, type="primary"):
                    st.session_state.trigger_animation = True
                    force_rerun()
                    
        else:
            status_placeholder.markdown("<div style='text-align:center; font-weight:bold; color:#10b981;'>Seluruh tahap identifikasi selesai!</div>", unsafe_allow_html=True)
            with log_container:
                st.info(f"🎉 **KESIMPULAN:** Berdasarkan alur eliminasi dan uji spesifik, senyawa *blind sample* ini terkonfirmasi sah sebagai **{senyawa.upper()}**.")
            
            with col_visual:
                st.write("")
                if st.button("🔄 Uji Senyawa Lain", use_container_width=True):
                    st.session_state.test_started = False
                    force_rerun()
