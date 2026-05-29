import streamlit as st
import time

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(page_title="Virtual Lab & Post-Test", page_icon="🧪", layout="wide")

# ================= MANAJEMEN STATE =================
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'post_senyawa' not in st.session_state:
    st.session_state.post_senyawa = ""
if 'post_reagen' not in st.session_state:
    st.session_state.post_reagen = ""

# ================= CSS MURNI UNTUK VISUAL 2D =================
st.markdown("""
<style>
    .tube-wrap { display: flex; justify-content: center; height: 320px; padding-top: 20px;}
    .tube-glass { width: 75px; height: 280px; border: 4px solid #cbd5e1; border-top: none; border-radius: 0 0 35px 35px; position: relative; overflow: hidden; background: transparent; }
    .tube-liquid { position: absolute; bottom: 0; left: 0; right: 0; transition: height 0.8s ease, background 0.8s ease; }
    .precipitate-layer { position: absolute; bottom: 0; left: 0; right: 0; height: 35px; background-color: rgba(0,0,0,0.5); }
    .bubble-fx { position: absolute; background: rgba(0,0,0,0.2); border-radius: 50%; width: 8px; height: 8px; animation: floatUp 1.2s infinite ease-in; }
    @keyframes floatUp { 0% { bottom: 0px; opacity: 1; } 100% { bottom: 250px; opacity: 0; } }
    .kontrol-panel { background: #f8fafc; padding: 25px; border-radius: 12px; border: 1px solid #e2e8f0; }
    .info-card { background: #ffffff; padding: 20px; border-left: 5px solid #0f766e; border-radius: 8px; margin-bottom: 15px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR MENU =================
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/3039/3039938.png", width=80)
    st.title("Menu Praktikum")
    
    menu_utama = st.radio("Navigasi:", [
        "📖 Modul 1: Hidrokarbon",
        "📖 Modul 2: Alkohol & Fenol",
        "📖 Modul 3: Aldehid & Keton",
        "📖 Modul 4: Asam Karboksilat",
        "🎯 Simulator Post-Test (2D)"
    ])
    st.divider()
    st.caption("Mode: Laporan Analitik & Uji Kualitatif")

# ================= KONTEN MODUL TEORI (TANPA 2D) =================
if menu_utama != "🎯 Simulator Post-Test (2D)":
    st.header(menu_utama)
    st.write("Gunakan panduan teori di bawah ini sebagai referensi untuk menyusun logbook atau pembahasan laporan resmi.")
    
    if "Modul 1" in menu_utama:
        st.markdown("""
        <div class="info-card">
        <h4>1. Uji Ketidakjenuhan (I₂ / Iodium)</h4>
        <b>Heksana (Alkana):</b> Warna I₂ tetap (tidak bereaksi). Alkana stabil dan tidak dapat mengalami adisi.<br>
        <b>Minyak Tanah (Alkena):</b> Warna I₂ pudar menjadi bening. Terjadi reaksi adisi pada ikatan rangkap.
        </div>
        <div class="info-card">
        <h4>2. Uji Bayer (KMnO₄)</h4>
        <b>Heksana:</b> Warna ungu tetap.<br>
        <b>Minyak Tanah:</b> Terbentuk endapan coklat (MnO₂). Ikatan tak jenuh dioksidasi membentuk senyawa diol.
        </div>
        """, unsafe_allow_html=True)
        
    elif "Modul 2" in menu_utama:
        st.markdown("""
        <div class="info-card">
        <h4>1. Uji Lucas (ZnCl₂/HCl)</h4>
        <b>Tersier:</b> Keruh seketika (Karbokation stabil, SN1 sangat cepat).<br>
        <b>Sekunder:</b> Keruh dalam 5-10 menit dengan pemanasan.<br>
        <b>Primer:</b> Bening (tidak bereaksi pada suhu ruang).
        </div>
        <div class="info-card">
        <h4>2. Uji Keasaman Fenol</h4>
        Fenol dapat melarut sempurna dalam basa kuat (NaOH) membentuk natrium fenoksida karena ion fenoksida distabilkan oleh resonansi cincin aromatik.
        </div>
        """, unsafe_allow_html=True)
        
    elif "Modul 3" in menu_utama:
        st.markdown("""
        <div class="info-card">
        <h4>1. Uji Fehling & Tollens</h4>
        <b>Aldehid:</b> Bereaksi positif. Fehling menghasilkan endapan merah bata (Cu₂O), Tollens menghasilkan cermin perak (Ag). Keduanya membutuhkan proses <b>pemanasan</b>.<br>
        <b>Keton:</b> Negatif untuk kedua uji (tidak memiliki hidrogen reaktif pada gugus karbonil).
        </div>
        """, unsafe_allow_html=True)
        
    elif "Modul 4" in menu_utama:
        st.markdown("""
        <div class="info-card">
        <h4>1. Uji Penggaraman (NaHCO₃ + Barit)</h4>
        <b>Asam Karboksilat (Asam Asetat):</b> Menghasilkan gelembung gas CO₂ yang dapat mengeruhkan larutan air barit (membentuk BaCO₃).<br>
        <b>Alkohol (Etanol):</b> Tidak bereaksi, kurang asam untuk mengurai bikarbonat.
        </div>
        """, unsafe_allow_html=True)

# ================= KONTEN SIMULATOR POST-TEST (DENGAN 2D) =================
else:
    st.title("🎯 Simulator 2D Post-Test")
    st.write("Lakukan simulasi pengujian kualitatif. Perhatikan langkah kerja yang membutuhkan **pemanasan** khusus.")
    
    # --- LOGIKA DATABASE 2D ---
    # Warna dasar reagen
    warna_reagen_map = {
        "I₂ (Iodium)": "#8b4513", "KMnO₄": "#8b5cf6", "Pereaksi Lucas": "#f8fafc", 
        "Uji Iodoform": "#f8fafc", "Pereaksi Fehling": "#3b82f6", "Pereaksi Tollens": "#f8fafc", 
        "NaHCO₃ + Uji Barit": "#f8fafc", "FeCl₃": "#facc15"
    }

    # Aturan Pemanasan Khusus
    reagen_pemanasan = ["Pereaksi Lucas", "Uji Iodoform", "Pereaksi Fehling", "NaHCO₃ + Uji Barit"]
    
    col_vis, col_kon = st.columns([1, 1.5])
    
    with col_kon:
        st.markdown("<div class='kontrol-panel'>", unsafe_allow_html=True)
        st.markdown("#### 🛠️ Meja Analisis")
        
        # 1. Pilih Senyawa Utama
        seny_post = st.selectbox("1. Ambil Sampel:", ["-- Pilih --", "Alkana", "Alkena", "Alkohol Primer", "Alkohol Sekunder", "Alkohol Tersier", "Fenol", "Aldehid", "Keton", "Asam Karboksilat"], disabled=(st.session_state.step > 0))
        
        # 2. Pilih Pereaksi
        reag_post = st.selectbox("2. Siapkan Reagen:", ["-- Pilih --", "I₂ (Iodium)", "KMnO₄", "Pereaksi Lucas", "Uji Iodoform", "Pereaksi Fehling", "Pereaksi Tollens", "NaHCO₃ + Uji Barit", "FeCl₃"], disabled=(st.session_state.step > 0))
        
        if st.button("🧪 Masukkan ke Tabung", disabled=(st.session_state.step > 0 or seny_post == "-- Pilih --" or reag_post == "-- Pilih --")):
            st.session_state.post_senyawa = seny_post
            st.session_state.post_reagen = reag_post
            st.session_state.step = 2
            st.rerun()

        # 3. Tombol Aksi (Otomatis berubah berdasarkan reagen)
        is_heating = st.session_state.post_reagen in reagen_pemanasan
        btn_teks = "🔥 Panaskan Penangas Air" if is_heating else "🧫 Kocok Tabung"
        
        if st.button(btn_teks, disabled=(st.session_state.step != 2)):
            with st.spinner("Menunggu reaksi berlangsung..."):
                time.sleep(1.2)
            st.session_state.step = 3
            st.rerun()

        st.write("---")
        if st.button("🔄 Cuci Tabung"):
            st.session_state.step = 0
            st.session_state.post_senyawa = ""
            st.session_state.post_reagen = ""
            st.rerun()
            
        st.markdown("</div>", unsafe_allow_html=True)

    with col_vis:
        t_cairan = "0%"
        w_cairan = "transparent"
        e_html = ""
        
        # Matriks Logika Hasil
        hasil_teks = "(-) Tidak Bereaksi"
        alasan_teks = "Senyawa inert atau gugus fungsi tidak cocok dengan pereaksi ini."
        w_akhir = "transparent"
        efek_akhir = "none"

        if st.session_state.step >= 2:
            w_cairan = warna_reagen_map.get(st.session_state.post_reagen, "#f8fafc")
            t_cairan = "65%"
            w_akhir = w_cairan # Default warna akhir sama dengan reagen
            
            # Logika Kimiawi saat di-klik (Step 3)
            if st.session_state.step == 3:
                s = st.session_state.post_senyawa
                r = st.session_state.post_reagen
                
                if r == "I₂ (Iodium)" and s == "Alkena":
                    w_akhir, efek_akhir, hasil_teks, alasan_teks = "#f8fafc", "none", "(+) Warna Pudar", "Ikatan rangkap memutus molekul I₂ melalui reaksi adisi."
                elif r == "KMnO₄" and s == "Alkena":
                    w_akhir, efek_akhir, hasil_teks, alasan_teks = "#a16207", "precipitate", "(+) Endapan Coklat", "Ikatan pi dioksidasi menghasilkan endapan MnO₂."
                elif r == "Pereaksi Lucas":
                    if s == "Alkohol Tersier":
                        w_akhir, efek_akhir, hasil_teks, alasan_teks = "#94a3b8", "cloudy", "(+) Keruh Seketika", "Substitusi SN1 instan karena karbokation sangat stabil."
                    elif s == "Alkohol Sekunder":
                        w_akhir, efek_akhir, hasil_teks, alasan_teks = "#e2e8f0", "cloudy", "(+) Keruh", "Membentuk alkil klorida dengan laju moderat setelah dipanaskan."
                elif r == "Uji Iodoform" and s in ["Keton", "Alkohol Sekunder"]:
                    w_akhir, efek_akhir, hasil_teks, alasan_teks = "#fef08a", "precipitate", "(+) Endapan Kuning", "Metil keton (atau alkohol yang dapat dioksidasi menjadi metil keton) menghasilkan kristal iodoform setelah dipanaskan."
                elif r == "Pereaksi Fehling" and s == "Aldehid":
                    w_akhir, efek_akhir, hasil_teks, alasan_teks = "#b91c1c", "precipitate", "(+) Endapan Merah Bata", "Pemanasan memicu aldehid untuk mereduksi ion Cu(II) menjadi Cu₂O."
                elif r == "Pereaksi Tollens" and s == "Aldehid":
                    w_akhir, efek_akhir, hasil_teks, alasan_teks = "#cbd5e1", "none", "(+) Cermin Perak", "Aldehid mereduksi ion perak menjadi lapisan logam Ag."
                elif r == "NaHCO₃ + Uji Barit" and s == "Asam Karboksilat":
                    w_akhir, efek_akhir, hasil_teks, alasan_teks = "#f8fafc", "bubbles", "(+) Gelembung Gas CO₂", "Pemanasan mempercepat pelepasan gas CO₂ akibat netralisasi asam karboksilat."
                elif r == "FeCl₃" and s == "Fenol":
                    w_akhir, efek_akhir, hasil_teks, alasan_teks = "#4c1d95", "none", "(+) Kompleks Ungu/Hitam",
