import streamlit as st
import time

# ================= KONFIGURASI HALAMAN =================
st.set_page_config(page_title="Auto-Analyzer Organik 2D", page_icon="🧪", layout="wide")

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
</style>
""", unsafe_allow_html=True)

# Fungsi bantuan untuk merender HTML tabung agar tidak terjadi bug markdown
def render_tube(tinggi, warna, efek):
    e_html = ""
    if efek == "precipitate":
        e_html = "<div class='precipitate-layer'></div>"
    elif efek == "cloudy":
        e_html = "<div class='cloudy-layer'></div>"
        
    return f"<div class='tube-wrap'><div class='tube-glass'><div class='tube-liquid' style='height:{tinggi}; background:{warna};'>{e_html}</div></div></div>"

# ================= DATABASE WARNA & REAKSI =================
reagen_colors = {
    "Ceric Nitrat": "#facc15", 
    "Pereaksi Jones": "#f97316", 
    "Pereaksi Lucas": "#f8fafc", 
    "Uji Iodoform": "#f8fafc", 
    "Na-Bisulfit": "#f8fafc", 
    "Pereaksi Fehling": "#3b82f6", 
    "Hidroksilamin": "#f8fafc", 
    "KMnO4": "#8b5cf6"
}

database_reaksi = {
    "Alkohol Primer": {
        "Ceric Nitrat": {"hasil": "(+) Merah", "alasan": "Membentuk kompleks merah dengan ion Cerium.", "warna_akhir": "#ef4444", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(+) Hijau", "alasan": "Dioksidasi menjadi asam karboksilat. Cr(VI) tereduksi menjadi Cr(III).", "warna_akhir": "#10b981", "efek": "none"},
        "Pereaksi Lucas": {"hasil": "(-) Bening", "alasan": "Karbokation primer sangat tidak stabil; tidak bereaksi pada suhu ruang.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Uji Iodoform": {"hasil": "(-) Bening", "alasan": "Secara umum negatif karena tidak membentuk metil keton (kecuali Etanol).", "warna_akhir": "#f8fafc", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(-) Bening", "alasan": "Tidak memiliki gugus karbonil reaktif.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Pereaksi Fehling": {"hasil": "(-) Tetap Biru", "alasan": "Bukan reduktor kuat yang bisa mereduksi ion tembaga(II).", "warna_akhir": "#3b82f6", "efek": "none"},
        "Hidroksilamin": {"hasil": "(-) Bening", "alasan": "Hanya bereaksi dengan gugus karbonil.", "warna_akhir": "#f8fafc", "efek": "none"},
        "KMnO4": {"hasil": "(+) Endapan Coklat", "alasan": "Dioksidasi kuat membentuk asam karboksilat dan endapan MnO2.", "warna_akhir": "#a16207", "efek": "precipitate"}
    },
    "Alkohol Sekunder": {
        "Ceric Nitrat": {"hasil": "(+) Merah", "alasan": "Membentuk kompleks merah dengan ion Cerium.", "warna_akhir": "#ef4444", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(+) Hijau", "alasan": "Dioksidasi menjadi keton. Cr(VI) tereduksi menjadi Cr(III).", "warna_akhir": "#10b981", "efek": "none"},
        "Pereaksi Lucas": {"hasil": "(+) Keruh", "alasan": "Reaksi substitusi SN1 berjalan lambat membentuk alkil klorida.", "warna_akhir": "#e2e8f0", "efek": "cloudy"},
        "Uji Iodoform": {"hasil": "(+) Endapan Kuning", "alasan": "Menghasilkan iodoform (Berlaku jika alkoholnya berstruktur metil karbinol).", "warna_akhir": "#fef08a", "efek": "precipitate"},
        "Na-Bisulfit": {"hasil": "(-) Bening", "alasan": "Tidak memiliki gugus karbonil bebas.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Pereaksi Fehling": {"hasil": "(-) Tetap Biru", "alasan": "Tidak memiliki sifat reduktor.", "warna_akhir": "#3b82f6", "efek": "none"},
        "Hidroksilamin": {"hasil": "(-) Bening", "alasan": "Tidak memiliki gugus karbonil.", "warna_akhir": "#f8fafc", "efek": "none"},
        "KMnO4": {"hasil": "(+) Endapan Coklat", "alasan": "Dioksidasi membentuk keton dan endapan MnO2.", "warna_akhir": "#a16207", "efek": "precipitate"}
    },
    "Alkohol Tersier": {
        "Ceric Nitrat": {"hasil": "(+) Merah", "alasan": "Membentuk kompleks merah dengan Cerium.", "warna_akhir": "#ef4444", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(-) Tetap Jingga", "alasan": "Tidak memiliki hidrogen alfa; kebal terhadap oksidasi.", "warna_akhir": "#f97316", "efek": "none"},
        "Pereaksi Lucas": {"hasil": "(+) Keruh Seketika", "alasan": "Karbokation tersier sangat stabil, bereaksi substitusi instan.", "warna_akhir": "#94a3b8", "efek": "cloudy"},
        "Uji Iodoform": {"hasil": "(-) Bening", "alasan": "Tidak bisa dioksidasi menjadi metil keton.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(-) Bening", "alasan": "Bukan senyawa karbonil.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Pereaksi Fehling": {"hasil": "(-) Tetap Biru", "alasan": "Bukan reduktor.", "warna_akhir": "#3b82f6", "efek": "none"},
        "Hidroksilamin": {"hasil": "(-) Bening", "alasan": "Bukan senyawa karbonil.", "warna_akhir": "#f8fafc", "efek": "none"},
        "KMnO4": {"hasil": "(-) Tetap Ungu", "alasan": "Kebal terhadap oksidator kuat.", "warna_akhir": "#8b5cf6", "efek": "none"}
    },
    "Aldehid": {
        "Ceric Nitrat": {"hasil": "(-) Tetap Kuning", "alasan": "Tidak memiliki gugus -OH alifatik.", "warna_akhir": "#facc15", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(+) Hijau", "alasan": "Sangat mudah dioksidasi menjadi asam karboksilat.", "warna_akhir": "#10b981", "efek": "none"},
        "Pereaksi Lucas": {"hasil": "(-) Bening", "alasan": "Spesifik hanya untuk alkohol.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Uji Iodoform": {"hasil": "(+) Endapan Kuning", "alasan": "Merespon positif HANYA JIKA aldehid tersebut adalah Asetaldehida.", "warna_akhir": "#fef08a", "efek": "precipitate"},
        "Na-Bisulfit": {"hasil": "(+) Endapan Putih", "alasan": "Gugus karbonil ujung mudah mengalami adisi nukleofilik.", "warna_akhir": "#ffffff", "efek": "precipitate"},
        "Pereaksi Fehling": {"hasil": "(+) Endapan Merah Bata", "alasan": "Reduktor kuat yang mereduksi ion Cu(II) menjadi Cu2O.", "warna_akhir": "#b91c1c", "efek": "precipitate"},
        "Hidroksilamin": {"hasil": "(+) Kristal Oksim", "alasan": "Berkondensasi dengan gugus karbonil membentuk oksim padat.", "warna_akhir": "#ffffff", "efek": "precipitate"},
        "KMnO4": {"hasil": "(+) Endapan Coklat", "alasan": "Mudah dioksidasi oleh permanganat.", "warna_akhir": "#a16207", "efek": "precipitate"}
    },
    "Keton": {
        "Ceric Nitrat": {"hasil": "(-) Tetap Kuning", "alasan": "Tidak memiliki gugus -OH.", "warna_akhir": "#facc15", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(-) Tetap Jingga", "alasan": "Keton stabil, tidak dapat dioksidasi oleh reagen ini.", "warna_akhir": "#f97316", "efek": "none"},
        "Pereaksi Lucas": {"hasil": "(-) Bening", "alasan": "Spesifik hanya untuk alkohol.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Uji Iodoform": {"hasil": "(+) Endapan Kuning", "alasan": "Akan bereaksi jika memiliki struktur metil keton.", "warna_akhir": "#fef08a", "efek": "precipitate"},
        "Na-Bisulfit": {"hasil": "(+) Endapan Putih", "alasan": "Adisi terjadi pada keton yang memiliki halangan sterik rendah.", "warna_akhir": "#ffffff", "efek": "precipitate"},
        "Pereaksi Fehling": {"hasil": "(-) Tetap Biru", "alasan": "Tidak memiliki sifat reduktor seperti aldehid.", "warna_akhir": "#3b82f6", "efek": "none"},
        "Hidroksilamin": {"hasil": "(+) Kristal Oksim", "alasan": "Berkondensasi membentuk turunan oksim.", "warna_akhir": "#ffffff", "efek": "precipitate"},
        "KMnO4": {"hasil": "(-) Tetap Ungu", "alasan": "Umumnya tahan terhadap oksidasi permanganat biasa.", "warna_akhir": "#8b5cf6", "efek": "none"}
    },
    "Asam Karboksilat": {
        "Ceric Nitrat": {"hasil": "(-) Tetap Kuning", "alasan": "Gugus karboksil sangat menarik elektron, O kurang nukleofilik untuk Cerium.", "warna_akhir": "#facc15", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(-) Tetap Jingga", "alasan": "Sudah berada dalam tingkat oksidasi maksimal.", "warna_akhir": "#f97316", "efek": "none"},
        "Pereaksi Lucas": {"hasil": "(-) Bening", "alasan": "Bukan golongan alkohol.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Uji Iodoform": {"hasil": "(-) Bening", "alasan": "Tidak membentuk gugus metil keton basa.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(-) Bening", "alasan": "Resonansi menstabilkan karbon karbonil sehingga tidak bisa diadisi.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Pereaksi Fehling": {"hasil": "(-) Tetap Biru", "alasan": "Tidak memiliki sifat reduktor.", "warna_akhir": "#3b82f6", "efek": "none"},
        "Hidroksilamin": {"hasil": "(-) Bening", "alasan": "Gugus karbonil terlindungi oleh resonansi internal.", "warna_akhir": "#f8fafc", "efek": "none"},
        "KMnO4": {"hasil": "(-) Tetap Ungu", "alasan": "Telah berada pada tingkat oksidasi maksimal.", "warna_akhir": "#8b5cf6", "efek": "none"}
    },
    "Alkana": {
        "Ceric Nitrat": {"hasil": "(-) Tetap Kuning", "alasan": "Senyawa jenuh sangat inert.", "warna_akhir": "#facc15", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(-) Tetap Jingga", "alasan": "Tidak memiliki gugus fungsional untuk dioksidasi.", "warna_akhir": "#f97316", "efek": "none"},
        "Pereaksi Lucas": {"hasil": "(-) Bening", "alasan": "Senyawa non-polar inert.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Uji Iodoform": {"hasil": "(-) Bening", "alasan": "Senyawa inert.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(-) Bening", "alasan": "Senyawa inert.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Pereaksi Fehling": {"hasil": "(-) Tetap Biru", "alasan": "Senyawa inert.", "warna_akhir": "#3b82f6", "efek": "none"},
        "Hidroksilamin": {"hasil": "(-) Bening", "alasan": "Senyawa inert.", "warna_akhir": "#f8fafc", "efek": "none"},
        "KMnO4": {"hasil": "(-) Tetap Ungu", "alasan": "Kebal terhadap oksidator karena tidak ada ikatan rangkap.", "warna_akhir": "#8b5cf6", "efek": "none"}
    }
}

urutan_pereaksi = [
    "Ceric Nitrat", "Pereaksi Jones", "Pereaksi Lucas", 
    "Uji Iodoform", "Na-Bisulfit", "Pereaksi Fehling", 
    "Hidroksilamin", "KMnO4"
]

# ================= UI UTAMA =================
st.title("⚙️ Mesin Auto-Analyzer 2D")
st.write("Sistem ini telah dirancang untuk menjalankan simulasi reaktivitas 8 pereaksi standar secara berurutan. Sangat cocok digunakan sebagai alat *cross-check* pada modul praktikum analisis.")

st.divider()

senyawa = st.selectbox("1. Masukkan Golongan Senyawa yang Akan Diuji:", ["-- Pilih Senyawa --"] + list(database_reaksi.keys()))

if st.button("Mulai Analisis Berurutan 🚀", type="primary"):
    if senyawa == "-- Pilih Senyawa --":
        st.warning("⚠️ Harap pilih senyawa terlebih dahulu!")
    else:
        st.write("---")
        # Pembuatan Layout: Tabung 2D di Kiri, Logbook di Kanan
        col_visual, col_log = st.columns([1, 2.5])
        
        with col_visual:
            st.markdown(f"<h4 style='text-align: center;'>Tabung Reaksi</h4>", unsafe_allow_html=True)
            # st.empty() ini adalah kuncinya: kita mengganti isi tabungnya di tempat yang sama (animasi)
            tube_placeholder = st.empty() 
            status_placeholder = st.empty()
            
        with col_log:
            st.markdown("#### 📑 Logbook Hasil Uji Berurutan")
            # st.container() menumpuk output ke bawah secara natural (cocok untuk log history)
            log_container = st.container()
            
        # LOOP PENGUJIAN OTOMATIS
        for i, pereaksi in enumerate(urutan_pereaksi):
            # 1. Animasi Kuras & Tambah Sampel (Warna bening)
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
            time.sleep(0.5)
            
            # 4. Mencetak ke Logbook di Kanan
            if "(+)" in res["hasil"]:
                log_container.success(f"**{i+1}. {pereaksi}** ➔ **{res['hasil']}**\n\n*Analisis:* {res['alasan']}")
            else:
                log_container.error(f"**{i+1}. {pereaksi}** ➔ **{res['hasil']}**\n\n*Analisis:* {res['alasan']}")
            
            # Delay sedikit sebelum pindah ke pereaksi berikutnya agar mata pengguna bisa menyimak
            time.sleep(1.2) 
            
        # Selesai
        status_placeholder.empty()
        tube_placeholder.markdown(render_tube("0%", "transparent", "none"), unsafe_allow_html=True)
        st.info(f"✅ **Analisis Auto-Sequencer untuk {senyawa} telah selesai.** Seluruh reaktivitas dicatat dengan sempurna.")
