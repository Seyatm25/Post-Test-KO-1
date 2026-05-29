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
    "Pereaksi Schiff": "#f8fafc" # Awalnya bening
}

database_reaksi = {
    "Alkohol Primer": {
        "Ceric Nitrat": {"hasil": "(+) Merah", "alasan": "Membentuk kompleks merah dengan ion Cerium.", "warna_akhir": "#ef4444", "efek": "none"},
        "Pereaksi Jones": {"hasil": "(+) Hijau", "alasan": "Dioksidasi menjadi asam karboksilat. Cr(VI) tereduksi menjadi Cr(III).", "warna_akhir": "#10b981", "efek": "none"},
        "Pereaksi Lucas": {"hasil": "(-) Bening", "alasan": "Karbokation primer sangat tidak stabil; tidak bereaksi pada suhu ruang.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Uji Iodoform": {"hasil": "(-) Bening", "alasan": "Secara umum negatif karena tidak membentuk metil keton.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Na-Bisulfit": {"hasil": "(-) Bening", "alasan": "Tidak memiliki gugus karbonil reaktif.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Pereaksi Fehling": {"hasil": "(-) Tetap Biru", "alasan": "Bukan reduktor kuat yang bisa mereduksi ion tembaga(II).", "warna_akhir": "#3b82f6", "efek": "none"},
        "Hidroksilamin": {"hasil": "(-) Bening", "alasan": "Hanya bereaksi dengan gugus karbonil.", "warna_akhir": "#f8fafc", "efek": "none"},
        "Pereaksi Schiff": {"hasil": "(-) Bening", "alasan": "Hanya spesifik bereaksi dengan aldehid.", "warna_akhir": "#f8fafc", "efek": "none"}
    },
    "Alkohol Sekunder": {
        "Ceric Nitrat": {"hasil": "(+) Merah", "
