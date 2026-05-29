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

database_reaksi = {
    "1-Butanol": {
        "Ceric Nitrat": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": "$R-OH + [Ce(NO_3)_6]^{2-} \\rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3$", 
            "alasan": "Gugus -OH bebas dari 1-butanol bereaksi menggantikan ligan nitrat pada ion Cerium(IV) membentuk senyawa kompleks koordinasi yang berwarna merah ceri.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Pereaksi Jones": {
            "hasil": "(+) Hijau", 
            "reaksi": "$3 R-CH_2OH + 2 CrO_3 + 3 H_2SO_4 \\rightarrow 3 R-CHO + Cr_2(SO_4)_3 + 6 H_2O$", 
            "alasan": "1-butanol adalah alkohol primer yang memiliki atom hidrogen alfa. Gugus -OH dioksidasi kuat menjadi asam karboksilat, sedangkan Kromium(VI) yang berwarna jingga tereduksi menjadi ion Kromium(III) yang berwarna hijau.", 
            "warna_akhir": "#10b981", "efek": "none"
        },
        "Pereaksi Lucas (Panas)": {
            "hasil": "(-) Bening", 
            "reaksi": "$R-CH_2OH + HCl \\xrightarrow{ZnCl_2, \\Delta} \\text{Tidak terjadi endapan}$", 
            "alasan": "Karbokation primer yang dihasilkan dari pemutusan gugus -OH sangatlah tidak stabil. Reaksi substitusi nukleofilik (SN1) tidak dapat berjalan untuk membentuk alkil klorida yang tak larut, bahkan setelah dibantu pemanasan.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        }
    },
    "2-Butanol": {
        "Ceric Nitrat": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": "$R-OH + [Ce(NO_3)_6]^{2-} \\rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3$", 
            "alasan": "Ikatan koordinasi terbentuk antara atom oksigen pada gugus hidroksil (-OH) sekunder dengan logam Cerium pusat, menghasilkan perubahan warna larutan.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Pereaksi Jones": {
            "hasil": "(+) Hijau", 
            "reaksi": "$3 R_2CH-OH + 2 CrO_3 + 3 H_2SO_4 \\rightarrow 3 R_2C=O + Cr_2(SO_4)_3 + 6 H_2O$", 
            "alasan": "2-butanol dioksidasi oleh reagen Jones menjadi keton (butanon). Cr(VI) (jingga) tereduksi ke Cr(III) (hijau).", 
            "warna_akhir": "#10b981", "efek": "none"
        },
        "Pereaksi Lucas (Panas)": {
            "hasil": "(+) Emulsi Putih", 
            "reaksi": "$R_2CH-OH + HCl \\xrightarrow{ZnCl_2} R_2CH-Cl \\downarrow + H_2O$", 
            "alasan": "Karbokation sekunder memiliki stabilitas menengah. Reaksi berjalan lambat, sehingga pemanasan dibutuhkan untuk mempercepat substitusi menjadi 2-klorobutana yang tidak larut dalam air (berwujud emulsi/keruh).", 
            "warna_akhir": "#e2e8f0", "efek": "cloudy"
        },
        "Uji Iodoform": {
            "hasil": "(+) Endapan Kuning", 
            "reaksi": "$R-CH(OH)-CH_3 + 4 I_2 + 6 NaOH \\rightarrow CHI_3 \\downarrow + R-COONa + 5 NaI + 5 H_2O$", 
            "alasan": "2-Butanol adalah struktur alkohol spesifik (metil karbinol) yang dapat dioksidasi oleh iodin menjadi metil keton. Gugus metilnya kemudian tersubstitusi menjadi kristal iodoform ($CHI_3$) kuning.", 
            "warna_akhir": "#fef08a", "efek": "precipitate"
        }
    },
    "t-Butil Alkohol": {
        "Ceric Nitrat": {
            "hasil": "(+) Merah Ceri", 
            "reaksi": "$R-OH + [Ce(NO_3)_6]^{2-} \\rightarrow [Ce(OR)(NO_3)_5]^{2-} + HNO_3$", 
            "alasan": "Terdapat gugus -OH bebas yang dapat berikatan koordinasi membentuk kompleks merah.", 
            "warna_akhir": "#ef4444", "efek": "none"
        },
        "Pereaksi Jones": {
            "hasil": "(-) Tetap Jingga", 
            "reaksi": "$R_3C-OH + CrO_3 + H^+ \\rightarrow \\text{Tidak ada reaksi}$", 
            "alasan": "Alkohol tersier tidak memiliki atom hidrogen alfa (ikatan C-H pada karbon pengikat OH), sehingga sangat kebal dan tidak bisa dioksidasi tanpa memutus kerangka karbonnya.", 
            "warna_akhir": "#f97316", "efek": "none"
        },
        "Pereaksi Lucas": {
            "hasil": "(+) Emulsi Putih (Seketika)", 
            "reaksi": "$R_3C-OH + HCl \\xrightarrow{ZnCl_2} R_3C-Cl \\downarrow + H_2O$", 
            "alasan": "Alkohol tersier sangat mudah terprotonasi melepaskan air, membentuk karbokation tersier yang sangat stabil. Reaksi (SN1) ini terjadi seketika menghasilkan endapan alkil klorida.", 
            "warna_akhir": "#94a3b8", "efek": "cloudy"
        }
    },
    "Formaldehida": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", 
            "reaksi": "$HCHO + [Ce(NO_3)_6]^{2-} \\rightarrow \\text{Tidak bereaksi}$", 
            "alasan": "Formaldehida merupakan senyawa karbonil (aldehid) dan tidak memiliki gugus hidroksil (-OH) bebas alifatik untuk bereaksi dengan Cerium.", 
            "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(+) Endapan Putih", 
            "reaksi": "$H-CHO + NaHSO_3 \\rightarrow H_2C(OH)SO_3Na \\downarrow$", 
            "alasan": "Ikatan C=O pada aldehid sangat polar. Nukleofil bisulfit ($HSO_3^-$) menyerang karbonil yang miskin elektron, membentuk garam bisulfit yang berbentuk padatan kristal.", 
            "warna_akhir": "#ffffff", "efek": "precipitate"
        },
        "Pereaksi Fehling": {
            "hasil": "(+) Merah Bata", 
            "reaksi": "$H-CHO + 2 Cu^{2+} + 5 OH^- \\rightarrow H-COO^- + Cu_2O \\downarrow + 3 H_2O$", 
            "alasan": "Aldehid adalah reduktor kuat karena adanya hidrogen karbonil yang sangat reaktif. Ia mereduksi Tembaga(II) sulfat yang berwarna biru menjadi endapan Tembaga(I) oksida ($Cu_2O$) merah bata.", 
            "warna_akhir": "#b91c1c", "efek": "precipitate"
        },
        "Pereaksi Schiff": {
            "hasil": "(+) Ungu / Magenta", 
            "reaksi": "$\\text{Aldehid} + \\text{Reagen Schiff} \\rightarrow \\text{Kompleks warna magenta}$", 
            "alasan": "Reaksi khas untuk membedakan aldehid. Aldehid melakukan reaksi adisi memulihkan pewarna p-rosanilin hidroklorida dari pengaruh asam sulfit.", 
            "warna_akhir": "#d946ef", "efek": "none"
        }
    },
    "Aseton": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", 
            "reaksi": "$CH_3COCH_3 + [Ce(NO_3)_6]^{2-} \\rightarrow \\text{Tidak bereaksi}$", 
            "alasan": "Keton tidak memiliki gugus hidroksil alkoholik.", 
            "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(+) Endapan Putih", 
            "reaksi": "$CH_3-CO-CH_3 + NaHSO_3 \\rightarrow (CH_3)_2C(OH)SO_3Na \\downarrow$", 
            "alasan": "Aseton tidak memiliki halangan sterik yang besar pada gugus karbonilnya, sehingga masih bisa mengalami reaksi adisi nukleofilik membentuk garam bisulfit.", 
            "warna_akhir": "#ffffff", "efek": "precipitate"
        },
        "Pereaksi Fehling": {
            "hasil": "(-) Tetap Biru", 
            "reaksi": "$CH_3-CO-CH_3 + Cu^{2+} \\rightarrow \\text{Tidak direduksi}$", 
            "alasan": "Keton tidak memiliki atom hidrogen yang menempel pada karbon di gugus karbonil, sehingga ia tidak memiliki sifat reduktor (berbeda dengan aldehid).", 
            "warna_akhir": "#3b82f6", "efek": "none"
        },
        "Uji Iodoform": {
            "hasil": "(+) Endapan Kuning", 
            "reaksi": "$CH_3-CO-CH_3 + 3 I_2 + 4 NaOH \\rightarrow CHI_3 \\downarrow + CH_3COONa + 3 NaI + 3 H_2O$", 
            "alasan": "Aseton memiliki struktur R-CO-CH3. Ketiga atom hidrogen alfa pada gugus metil sangat asam, tersubstitusi oleh Iodin, lalu putus membentuk Iodoform ($CHI_3$).", 
            "warna_akhir": "#fef08a", "efek": "precipitate"
        }
    },
    "Etil Asetat": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", "reaksi": "$\\text{Ester} + \\text{Ceric Nitrat} \\rightarrow \\text{Tidak bereaksi}$", 
            "alasan": "Gugus ester ($R-COO-R$) tidak bereaksi dengan uji alkohol.", 
            "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(-) Bening", "reaksi": "$\\text{Ester} + NaHSO_3 \\rightarrow \\text{Tidak bereaksi}$", 
            "alasan": "Pasangan elektron bebas dari gugus etoksi ($O-CH_2CH_3$) memberikan efek resonansi yang menstabilkan karbon karbonil, menjadikannya tidak reaktif terhadap nukleofil lemah seperti bisulfit.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Hidroksilamin (Uji Ester)": {
            "hasil": "(+) Merah Violet", 
            "reaksi": "$\\text{1. } R-COOR' + NH_2OH \\xrightarrow{NaOH} R-CONHOH + R'OH \\\\ \\text{2. } 3 R-CONHOH + FeCl_3 \\rightarrow Fe(R-CONHO)_3 + 3 HCl$", 
            "alasan": "Ester diubah oleh hidroksilamin menjadi asam hidroksamat. Asam hidroksamat kemudian mengikat ion $Fe^{3+}$ (dari Feriklorida) menghasilkan kompleks berwarna violet/ungu.", 
            "warna_akhir": "#c026d3", "efek": "none"
        }
    },
    "Asam Asetat": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", "reaksi": "$CH_3COOH + \\text{Ceric Nitrat} \\rightarrow \\text{Tidak bereaksi}$", 
            "alasan": "Atom oksigen pada gugus karboksil tertarik oleh resonansi ikatan rangkap karbonil (electron-withdrawing), menjadikannya kurang nukleofilik untuk berikatan dengan Cerium.", 
            "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(-) Bening", "reaksi": "$CH_3COOH + NaHSO_3 \\rightarrow \\text{Tidak bereaksi}$", 
            "alasan": "Bukan senyawa golongan aldehid atau keton.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Hidroksilamin (Uji Ester)": {
            "hasil": "(-) Bening", "reaksi": "$CH_3COOH + NH_2OH + FeCl_3 \\rightarrow \\text{Tidak membentuk warna kompleks}$", 
            "alasan": "Bukan ester. Asam karboksilat tidak memicu pembentukan asam hidroksamat reaktif di kondisi yang sama.", 
            "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Barit (NaHCO3)": {
            "hasil": "(+) Gelembung & Keruh", 
            "reaksi": "$CH_3COOH + NaHCO_3 \\rightarrow CH_3COONa + H_2O + CO_2 \\uparrow$ \\\\ $\\text{Lalu: } CO_2 + Ba(OH)_2 \\rightarrow BaCO_3 \\downarrow + H_2O$", 
            "alasan": "Asam karboksilat cukup kuat mendonasikan proton (H+) untuk menetralisir dan mengurai senyawa bikarbonat. Gas karbondioksida ($CO_2$) yang terlepas ini kemudian diuji dengan air barit ($Ba(OH)_2$) membentuk padatan $BaCO_3$ yang keruh.", 
            "warna_akhir": "#f8fafc", "efek": "bubbles"
        }
    },
    "Heksana": {
        "Ceric Nitrat": {
            "hasil": "(-) Kuning", "reaksi": "$\\text{Heksana} + \\text{Ceric Nitrat} \\rightarrow \\text{Tidak bereaksi}$", "alasan": "Tidak ada gugus fungsi -OH.", "warna_akhir": "#facc15", "efek": "none"
        },
        "Na-Bisulfit": {
            "hasil": "(-) Bening", "reaksi": "$\\text{Heksana} + NaHSO_3 \\rightarrow \\text{Tidak bereaksi}$", "alasan": "Tidak ada gugus karbonil.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Hidroksilamin (Uji Ester)": {
            "hasil": "(-) Bening", "reaksi": "$\\text{Heksana} + NH_2OH \\rightarrow \\text{Tidak bereaksi}$", "alasan": "Bukan gugus ester.", "warna_akhir": "#f8fafc", "efek": "none"
        },
        "Uji Barit (NaHCO3)": {
            "hasil": "(-) Bening", "reaksi": "$\\text{Heksana} + NaHCO_3 \\rightarrow \\text{Tidak bereaksi}$", 
            "alasan": "Senyawa hidrokarbon alifatik (jenuh) bersifat non-polar dan inert. Karena secara berturut-turut dieliminasi dan gagal bereaksi di seluruh uji fungsional, ini membuktikan senyawanya adalah alkana.", 
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
            st.rerun()

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
        st.markdown("#### 📑 Logbook & Analisis Teoritis")
        log_container = st.container()

    # Mencetak rekam jejak + REAKSI & ALASAN
    with log_container:
        for log in st.session_state.log_history:
            if "(+)" in log["hasil"]:
                st.success(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n**Reaksi:**\n{log['reaksi']}\n\n**Pembahasan:**\n{log['alasan']}")
            else:
                st.error(f"**Tahap {log['step']}: {log['pereaksi']}** ➔ **{log['hasil']}**\n\n**Reaksi:**\n{log['reaksi']}\n\n**Pembahasan:**\n{log['alasan']}")

    # ---------------- LOGIKA ANIMASI & TOMBOL NEXT ----------------
    if st.session_state.trigger_animation and st.session_state.current_step < len(urutan):
        pereaksi = urutan[st.session_state.current_step]
        
        # Animasi Kuras & Tambah
        tube_placeholder.markdown(render_tube("30%", "#f1f5f9", "none"), unsafe_allow_html=True)
        status_placeholder.markdown(f"<div style='text-align:center;'><em>Menyiapkan sampel untuk {pereaksi}...</em></div>", unsafe_allow_html=True)
        time.sleep(1.0)
        
        # Animasi Meneteskan Reagen
        warna_reagen = reagen_colors[pereaksi]
        tube_placeholder.markdown(render_tube("65%", warna_reagen, "none"), unsafe_allow_html=True)
        status_placeholder.markdown(f"<div style='text-align:center;'><em>Meneteskan {pereaksi}...</em></div>", unsafe_allow_html=True)
        time.sleep(1.5)
        
        # Animasi Hasil Akhir
        res = database_reaksi[senyawa][pereaksi]
        tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
        status_placeholder.markdown(f"<div style='text-align:center; font-weight:bold;'>Melihat hasil reaksi...</div>", unsafe_allow_html=True)
        time.sleep(1.2)
        
        # Simpan lengkap dengan persamaan reaksi
        st.session_state.log_history.append({
            "step": st.session_state.current_step + 1,
            "pereaksi": pereaksi,
            "hasil": res["hasil"],
            "reaksi": res["reaksi"],
            "alasan": res["alasan"]
        })
        
        st.session_state.current_step += 1
        st.session_state.trigger_animation = False
        st.rerun()

    elif not st.session_state.trigger_animation:
        
        if st.session_state.current_step > 0:
            last_pereaksi = urutan[st.session_state.current_step - 1]
            res = database_reaksi[senyawa][last_pereaksi]
            tube_placeholder.markdown(render_tube("65%", res["warna_akhir"], res["efek"]), unsafe_allow_html=True)
        
        if st.session_state.current_step < len(urutan):
            next_pereaksi = urutan[st.session_state.current_step]
            status_placeholder.markdown(f"<div style='text-align:center; color:#475569;'>Menunggu konfirmasi pembacaan...</div>", unsafe_allow_html=True)
            
            with col_visual:
                st.write("") 
                if st.button(f"Lanjutkan ke Uji {next_pereaksi} ⏭️", use_container_width=True, type="primary"):
                    st.session_state.trigger_animation = True
                    st.rerun()
                    
        else:
            status_placeholder.markdown(f"<div style='text-align:center; font-weight:bold; color:#10b981;'>Seluruh tahap identifikasi selesai!</div>", unsafe_allow_html=True)
            with log_container:
                st.info(f"🎉 **KESIMPULAN:** Berdasarkan alur eliminasi dan uji spesifik, senyawa *blind sample* ini terkonfirmasi sah sebagai **{senyawa.upper()}**.")
            
            with col_visual:
                st.write("")
                if st.button("🔄 Uji Senyawa Lain", use_container_width=True):
                    st.session_state.test_started = False
                    st.rerun()
