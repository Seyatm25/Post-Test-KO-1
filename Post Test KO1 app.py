import streamlit as st
import time

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(page_title="Virtual Lab Kimia Organik", page_icon="🧪", layout="wide")

# ================= MANAJEMEN STATE =================
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'current_exp' not in st.session_state:
    st.session_state.current_exp = ""
if 'current_sample' not in st.session_state:
    st.session_state.current_sample = ""

# ================= DATABASE PERCOBAAN =================
percobaan_db = {
    # --- MODUL 1: HIDROKARBON ---
    "Uji Ketidakjenuhan (I₂/Iodium)": {
        "modul": "Modul 1: Hidrokarbon",
        "sampel_opsi": ["Heksana (Alkana)", "Minyak Tanah (Alkena)"],
        "reagen": "Larutan I₂ (Iodium)",
        "warna_reagen": "#8b4513", # Coklat
        "aksi_teks": "Kocok Tabung",
        "hasil": {
            "Heksana (Alkana)": {
                "warna_akhir": "#8b4513", "efek": "none",
                "pengamatan": "Warna coklat I₂ TETAP (tidak pudar)[cite: 46].",
                "reaksi": "$Heksana + I_2 \\rightarrow \\text{Tidak ada reaksi}$",
                "alasan": "Heksana adalah hidrokarbon jenuh yang stabil, tidak dapat mengalami reaksi adisi untuk memutus ikatan I₂[cite: 49, 50, 51, 52]."
            },
            "Minyak Tanah (Alkena)": {
                "warna_akhir": "#f8fafc", "efek": "none",
                "pengamatan": "Warna coklat I₂ PUDAR menjadi bening[cite: 46, 53].",
                "reaksi": "$R-CH=CH-R' + I_2 \\rightarrow R-CHI-CHI-R'$",
                "alasan": "Ikatan rangkap pada minyak tanah memutus molekul I₂ melalui reaksi adisi, sehingga warna asli Iodium hilang[cite: 48, 53]."
            }
        }
    },
    "Uji Bayer (KMnO₄)": {
        "modul": "Modul 1: Hidrokarbon",
        "sampel_opsi": ["Heksana", "Minyak Tanah"],
        "reagen": "KMnO₄ (Ungu)",
        "warna_reagen": "#8b5cf6", # Ungu
        "aksi_teks": "Kocok Tabung",
        "hasil": {
            "Heksana": {
                "warna_akhir": "#8b5cf6", "efek": "none",
                "pengamatan": "Warna ungu KMnO₄ TETAP.",
                "reaksi": "$Heksana + KMnO_4 \\rightarrow \\text{Tidak bereaksi}$",
                "alasan": "Alkana jenuh tidak dapat dioksidasi oleh kalium permanganat."
            },
            "Minyak Tanah": {
                "warna_akhir": "#a16207", "efek": "precipitate",
                "pengamatan": "Warna pudar dan terbentuk ENDAPAN COKLAT[cite: 66, 69, 77].",
                "reaksi": "$3R-CH=CH-R' + 2KMnO_4 + 4H_2O \\rightarrow 3R-CH(OH)-CH(OH)-R' + 2MnO_2 \\downarrow + 2KOH$",
                "alasan": "Senyawa tak jenuh dioksidasi menjadi diol (glikol). Permanganat tereduksi membentuk endapan coklat mangan dioksida (MnO₂)[cite: 77]."
            }
        }
    },
    
    # --- MODUL 2: ALKOHOL & FENOL ---
    "Uji Lucas": {
        "modul": "Modul 2: Alkohol & Fenol",
        "sampel_opsi": ["1-Butanol (Primer)", "2-Butanol (Sekunder)", "t-Butil Alkohol (Tersier)"],
        "reagen": "Pereaksi Lucas (ZnCl₂/HCl)",
        "warna_reagen": "#f8fafc", 
        "aksi_teks": "Diamkan & Amati",
        "hasil": {
            "1-Butanol (Primer)": {
                "warna_akhir": "#f8fafc", "efek": "none",
                "pengamatan": "Larutan tetap bening/jernih[cite: 213, 218].",
                "reaksi": "$R-CH_2OH + HCl \\xrightarrow{ZnCl_2} \\text{Tidak bereaksi pada suhu ruang}$",
                "alasan": "Karbokation primer sangat tidak stabil untuk melakukan substitusi (SN1) pada suhu ruang."
            },
            "2-Butanol (Sekunder)": {
                "warna_akhir": "#e2e8f0", "efek": "cloudy",
                "pengamatan": "Larutan menjadi keruh setelah 5 - 10 menit[cite: 218].",
                "reaksi": "$R_2CH-OH + HCl \\xrightarrow{ZnCl_2} R_2CH-Cl \\downarrow + H_2O$",
                "alasan": "Bereaksi moderat membentuk alkil klorida yang tidak larut."
            },
            "t-Butil Alkohol (Tersier)": {
                "warna_akhir": "#94a3b8", "efek": "cloudy",
                "pengamatan": "Larutan seketika menjadi KERUH tebal[cite: 218].",
                "reaksi": "$R_3C-OH + HCl \\xrightarrow{ZnCl_2} R_3C-Cl \\downarrow + H_2O$",
                "alasan": "Karbokation tersier sangat stabil, sehingga substitusi pembentukan alkil klorida terjadi seketika."
            }
        }
    },
    "Uji Keasaman Fenol": {
        "modul": "Modul 2: Alkohol & Fenol",
        "sampel_opsi": ["Fenol"],
        "reagen": "Larutan NaOH 10%",
        "warna_reagen": "#f8fafc", 
        "aksi_teks": "Kocok Kuat",
        "hasil": {
            "Fenol": {
                "warna_akhir": "#f8fafc", "efek": "none",
                "pengamatan": "Fenol yang awalnya kurang larut menjadi LARUT SEMPURNA[cite: 284, 295, 297].",
                "reaksi": "$C_6H_5OH + NaOH \\rightarrow C_6H_5ONa + H_2O$",
                "alasan": "Fenol bersifat asam lemah akibat stabilitas resonansi ion fenoksida, sehingga dapat bereaksi dengan basa kuat (NaOH) membentuk garam natrium fenoksida yang mudah larut air[cite: 275, 297]."
            }
        }
    },

    # --- MODUL 3: ALDEHID & KETON ---
    "Uji Fehling": {
        "modul": "Modul 3: Aldehid & Keton",
        "sampel_opsi": ["Asetaldehida (Aldehid)", "Aseton (Keton)"],
        "reagen": "Pereaksi Fehling (Cu²⁺ biru)",
        "warna_reagen": "#3b82f6", 
        "aksi_teks": "Panaskan",
        "hasil": {
            "Asetaldehida (Aldehid)": {
                "warna_akhir": "#b91c1c", "efek": "precipitate",
                "pengamatan": "Terbentuk ENDAPAN MERAH BATA[cite: 372, 403].",
                "reaksi": "$R-CHO + 2Cu^{2+} + 5OH^- \\rightarrow R-COO^- + Cu_2O \\downarrow + 3H_2O$ [cite: 317, 318, 319, 320, 321]",
                "alasan": "Aldehid mereduksi ion Cu(II) menjadi endapan Cu(I) Oksida (Cu₂O)[cite: 312, 313, 314, 315, 316]."
            },
            "Aseton (Keton)": {
                "warna_akhir": "#3b82f6", "efek": "none",
                "pengamatan": "Larutan tetap berwarna biru jernih[cite: 403].",
                "reaksi": "$Keton + Fehling \\rightarrow \\text{Tidak ada reaksi}$",
                "alasan": "Keton tidak memiliki daya pereduksi karena tidak ada atom H reaktif pada karbon pengikat oksigen[cite: 312]."
            }
        }
    },
    "Uji Tollens (Cermin Perak)": {
        "modul": "Modul 3: Aldehid & Keton",
        "sampel_opsi": ["Asetaldehida (Aldehid)", "Aseton (Keton)"],
        "reagen": "Pereaksi Tollens (Ag⁺)",
        "warna_reagen": "#f8fafc", 
        "aksi_teks": "Panaskan",
        "hasil": {
            "Asetaldehida (Aldehid)": {
                "warna_akhir": "linear-gradient(to right, #64748b, #cbd5e1, #64748b)", "efek": "none",
                "pengamatan": "Terbentuk lapisan CERMIN PERAK[cite: 388, 403].",
                "reaksi": "$R-CHO + 2Ag^+ + 3OH^- \\rightarrow R-COO^- + 2Ag \\downarrow + 2H_2O$ [cite: 323, 324, 325, 326, 327, 328, 329, 330]",
                "alasan": "Aldehid mengoksidasi dirinya sendiri dan mereduksi ion perak (Ag⁺) menjadi logam perak (Ag) yang menempel pada kaca."
            },
            "Aseton (Keton)": {
                "warna_akhir": "#f8fafc", "efek": "none",
                "pengamatan": "Tetap bening[cite: 390, 403].",
                "reaksi": "$Keton + Tollens \\rightarrow \\text{Tidak ada reaksi}$",
                "alasan": "Keton tidak dapat dioksidasi oleh oksidator lemah seperti Tollens."
            }
        }
    },

    # --- MODUL 4: ASAM KARBOKSILAT ---
    "Uji Penggaraman (NaHCO₃)": {
        "modul": "Modul 4: Asam Karboksilat",
        "sampel_opsi": ["Asam Asetat", "Etanol"],
        "reagen": "Larutan NaHCO₃ 5%",
        "warna_reagen": "#f8fafc", 
        "aksi_teks": "Salurkan ke Air Barit",
        "hasil": {
            "Asam Asetat": {
                "warna_akhir": "#f8fafc", "efek": "bubbles",
                "pengamatan": "Timbul GELEMBUNG GAS (CO₂) dan Air Barit keruh[cite: 453, 460].",
                "reaksi": "$CH_3COOH + NaHCO_3 \\rightarrow CH_3COONa + H_2O + CO_2 \\uparrow$",
                "alasan": "Asam asetat mendonasikan proton ke bikarbonat, menghasilkan gas CO₂ yang mengeruhkan air barit ($BaCO_3$)."
            },
            "Etanol": {
                "warna_akhir": "#f8fafc", "efek": "none",
                "pengamatan": "Tidak ada perubahan.",
                "reaksi": "$Etanol + NaHCO_3 \\rightarrow \\text{Tidak bereaksi}$",
                "alasan": "Etanol tidak cukup asam untuk bereaksi dengan garam bikarbonat."
            }
        }
    }
}

# ================= CSS MURNI & ANTI-BUG =================
st.markdown("""
<style>
    /* Desain Tabung Reaksi Super Clean tanpa celah */
    .tube-wrap { display: flex; justify-content: center; height: 320px; padding-top: 20px;}
    .tube-glass { 
        width: 75px; 
        height: 280px; 
        border: 4px solid #cbd5e1; 
        border-top: none; 
        border-radius: 0 0 35px 35px; 
        position: relative; 
        overflow: hidden;
        background: transparent;
    }
    .tube-liquid { 
        position: absolute; 
        bottom: 0; left: 0; right: 0; 
        transition: height 0.8s ease, background 0.8s ease; 
    }
    
    /* Efek Endapan & Gas */
    .precipitate-layer { position: absolute; bottom: 0; left: 0; right: 0; height: 30px; background-color: rgba(0,0,0,0.5); }
    .bubble-fx { position: absolute; background: rgba(0,0,0,0.2); border-radius: 50%; width: 8px; height: 8px; animation: floatUp 1.2s infinite ease-in; }
    @keyframes floatUp { 0% { bottom: 0px; opacity: 1; } 100% { bottom: 250px; opacity: 0; } }
    
    /* Layout Kartu UI */
    .kontrol-panel { background: #f8fafc; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; }
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR MENU =================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3039/3039938.png", width=80)
    st.title("Asisten Lab KO")
    
    menu_utama = st.radio("Pilih Menu:", [
        "Modul 1: Hidrokarbon",
        "Modul 2: Alkohol & Fenol",
        "Modul 3: Aldehid & Keton",
        "Modul 4: Asam Karboksilat",
        "🎯 Prediktor Post-Test"
    ])
    st.divider()

# ================= KONTEN HALAMAN =================
if menu_utama != "🎯 Prediktor Post-Test":
    # Filter percobaan berdasarkan Modul yang dipilih di Sidebar
    opsi_percobaan = [k for k, v in percobaan_db.items() if v["modul"] == menu_utama]
    
    if opsi_percobaan:
        pilihan = st.selectbox("Pilih Jenis Percobaan:", opsi_percobaan)
        
        # Reset visual jika pengguna mengganti percobaan
        if pilihan != st.session_state.current_exp:
            st.session_state.current_exp = pilihan
            st.session_state.step = 0
            st.session_state.current_sample = ""
            st.rerun()

        data_exp = percobaan_db[st.session_state.current_exp]
        st.markdown(f"### 🔬 Simulasi: {st.session_state.current_exp}")
        
        # --- LAYOUT DUA KOLOM (Kiri Visual, Kanan Panel Kendali) ---
        col_vis, col_kon = st.columns([1, 1.5])
        
        with col_vis:
            # Render HTML/CSS untuk Tabung Reaksi (Tanpa spasi ganda agar tidak jadi markdown bug)
            t_cairan = "0%"
            w_cairan = "transparent"
            e_html = ""

            if st.session_state.step == 1:
                t_cairan = "35%"
                w_cairan = "#f1f5f9"
            elif st.session_state.step == 2:
                t_cairan = "65%"
                w_cairan = data_exp["warna_reagen"]
            elif st.session_state.step == 3:
                t_cairan = "65%"
                hasil_dt = data_exp["hasil"][st.session_state.current_sample]
                w_cairan = hasil_dt["warna_akhir"]
                
                if hasil_dt["efek"] == "bubbles":
                    e_html = "<div class='bubble-fx' style='left:15px;'></div><div class='bubble-fx' style='left:40px; animation-delay:0.4s;'></div>"
                elif hasil_dt["efek"] == "precipitate":
                    e_html = "<div class='precipitate-layer'></div>"
                elif hasil_dt["efek"] == "cloudy":
                    e_html = "<div style='position:absolute; width:100%; height:100%; background:rgba(255,255,255,0.4);'></div>"

            # Injeksi HTML dirapatkan agar aman
            st.markdown(f"<div class='tube-wrap'><div class='tube-glass'><div class='tube-liquid' style='height:{t_cairan}; background:{w_cairan};'>{e_html}</div></div></div>", unsafe_allow_html=True)

        with col_kon:
            st.markdown("<div class='kontrol-panel'>", unsafe_allow_html=True)
            st.markdown("#### 🛠️ Meja Praktikum")
            
            # Step 1
            spl = st.selectbox("1. Pilih Sampel", ["-- Pilih --"] + data_exp["sampel_opsi"], disabled=(st.session_state.step > 0))
            if st.button("💧 Masukkan Sampel", disabled=(st.session_state.step > 0 or spl == "-- Pilih --")):
                st.session_state.current_sample = spl
                st.session_state.step = 1
                st.rerun()

            # Step 2
            if st.button(f"🧪 Tambah {data_exp['reagen']}", disabled=(st.session_state.step != 1)):
                st.session_state.step = 2
                st.rerun()

            # Step 3
            if st.button(f"🔥 {data_exp['aksi_teks']}", disabled=(st.session_state.step != 2)):
                with st.spinner("Reaksi sedang berlangsung..."):
                    time.sleep(1)
                st.session_state.step = 3
                st.rerun()

            # Step Reset
            st.write("---")
            if st.button("🔄 Cuci Tabung"):
                st.session_state.step = 0
                st.session_state.current_sample = ""
                st.rerun()
                
            st.markdown("</div>", unsafe_allow_html=True)

        # --- JURNAL HASIL PRAKTIKUM ---
        if st.session_state.step == 3:
            st.divider()
            hasil_dt = data_exp["hasil"][st.session_state.current_sample]
            st.markdown("#### 📑 Catatan Logbook Praktikum")
            st.write("Bahas bagian analisis ini ke dalam format pembahasan di laporan resmi:")
            
            c1, c2 = st.columns(2)
            with c1:
                st.success(f"**Pengamatan Fisis:**\n\n{hasil_dt['pengamatan']}")
                st.info("**Persamaan Reaksi:**")
                st.markdown(hasil_dt['reaksi'])
            with c2:
                st.warning(f"**Pembahasan:**\n\n{hasil_dt['alasan']}")

else:
    # ================= MENU 5: PREDIKTOR POST-TEST =================
    st.title("🎯 Prediktor Cepat Post-Test KO")
    st.write("Gunakan fitur ini untuk memeriksa silang (*cross-check*) jawaban teori reaktivitas senyawamu.")
    
    col1, col2 = st.columns(2)
    with col1:
        seny_post = st.selectbox("Pilih Senyawa Utama:", ["Alkana Rantai Lurus", "Alkena/Alkuna", "Alkohol Primer", "Alkohol Tersier", "Aldehid", "Keton", "Asam Karboksilat", "Fenol"])
    with col2:
        reag_post = st.selectbox("Pilih Pereaksi:", ["I₂ / KMnO₄", "Pereaksi Lucas", "FeCl₃", "Pereaksi Tollens / Fehling", "NaHCO₃"])

    st.write("---")
    
    # Logika Cepat Post-Test
    hasil_post = "(-) Tidak Terjadi Reaksi"
    alasan_post = "Sifat fisis dan struktur kimiawi senyawa tidak merespon spesifisitas pereaksi ini."
    
    if reag_post == "I₂ / KMnO₄":
        if seny_post == "Alkena/Alkuna":
            hasil_post = "(+) Reaksi Adisi / Oksidasi"
            alasan_post = "Ikatan rangkap (pi) memutus molekul I₂ (hilang warna) atau dioksidasi oleh KMnO₄ menghasilkan endapan coklat MnO₂."
    elif reag_post == "Pereaksi Lucas":
        if seny_post == "Alkohol Tersier":
            hasil_post = "(+) Keruh Sangat Cepat"
            alasan_post = "Mekanisme SN1 berjalan spontan akibat tingginya stabilitas karbokation tersier yang dihasilkan."
    elif reag_post == "FeCl₃":
        if seny_post == "Fenol":
            hasil_post = "(+) Terbentuk Kompleks Berwarna"
            alasan_post = "Gugus -OH yang terikat pada cincin aromatik (benzena) membentuk kompleks koordinasi khas dengan ion Fe(III)."
    elif reag_post == "Pereaksi Tollens / Fehling":
        if seny_post == "Aldehid":
            hasil_post = "(+) Cermin Perak / Endapan Merah Bata"
            alasan_post = "Aldehid adalah agen pereduksi kuat yang mampu mereduksi ion perak atau ion tembaga."
    elif reag_post == "NaHCO₃":
        if seny_post == "Asam Karboksilat":
            hasil_post = "(+) Gelembung Gas CO₂"
            alasan_post = "Reaksi netralisasi penggaraman. Asam karboksilat mengurai ion bikarbonat melepaskan gas karbondioksida."

    if "(+)" in hasil_post:
        st.success(f"**Prediksi Hasil:** {hasil_post}\n\n**Alasan Teoritis:** {alasan_post}")
    else:
        st.error(f"**Prediksi Hasil:** {hasil_post}\n\n**Alasan Teoritis:** {alasan_post}")
