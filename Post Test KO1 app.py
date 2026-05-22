import streamlit as st

# Konfigurasi Halaman
st.set_page_config(page_title="Prediktor Uji Senyawa", page_icon="🧪", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    .kotak {
        border: 2px solid #2ecc71;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        background-color: #f9fbf9;
    }
    .label {
        font-weight: bold;
        color: #27ae60;
        font-size: 1.2em;
        margin-bottom: 5px;
        border-bottom: 2px solid #2ecc71;
        display: inline-block;
    }
    </style>
""", unsafe_allow_html=True)

st.title("🧪 Prediktor Uji Senyawa Organik")
st.write("Pilih senyawa dan pereaksi untuk melihat hasil serta alasan spesifik di balik reaksinya.")

# ================= KOTAK INPUT =================
col1, col2 = st.columns(2)

with col1:
    senyawa = st.selectbox("Senyawa", [
        "Alkohol Primer", 
        "Alkohol Sekunder", 
        "Alkohol Tersier", 
        "Formaldehida", 
        "Aseton", 
        "Heksana", 
        "Etil Asetat", 
        "Asam Asetat"
    ])

with col2:
    pereaksi = st.selectbox("Pereaksi", [
        "Oksidator (K2Cr2O7 / H+)", 
        "Pereaksi Lucas (ZnCl2 / HCl)", 
        "Pereaksi Tollens", 
        "Pereaksi Fehling",
        "Uji Iodoform (I2 / NaOH)",
        "Pereaksi Jones (CrO3 / H2SO4)",
        "Pereaksi Schiff",
        "Natrium Bisulfit (NaHSO3)",
        "Hidroksilamin (NH2OH)",
        "NaHCO3 + Uji Barit (Ba(OH)2)",
        "Uji Ceric Nitrat"
    ])

# ================= LOGIKA DATABASE REAKSI & ALASAN =================
hasil = "(-) Tidak Bereaksi"
reaksi = "Tidak ada persamaan reaksi."
pembahasan = ""

def alasan_negatif_umum(senyawa):
    if senyawa == "Heksana": return "Heksana adalah alkana rantai lurus (non-polar dan jenuh) yang sangat stabil dan tidak memiliki gugus fungsi reaktif."
    if senyawa == "Etil Asetat": return "Etil asetat adalah ester yang cukup stabil. Gugus karbonilnya terstabilkan oleh resonansi sehingga kurang reaktif terhadap pereaksi ini."
    return f"{senyawa} tidak memiliki gugus fungsi yang sesuai untuk berinteraksi dengan pereaksi ini."

# 1. K2Cr2O7
if pereaksi == "Oksidator (K2Cr2O7 / H+)":
    if senyawa in ["Alkohol Primer", "Alkohol Sekunder", "Formaldehida"]:
        hasil = "(+) Warna berubah jingga menjadi hijau"
        reaksi = "Cr₂O₇²⁻ (jingga) + Senyawa → Cr³⁺ (hijau) + Hasil Oksidasi"
        pembahasan = "✅ **Kenapa bereaksi:** Senyawa ini memiliki atom Hidrogen yang terikat pada atom Karbon pembawa gugus fungsi, sehingga dapat dioksidasi. Ion dikromat (jingga) tereduksi menjadi ion Cr³⁺ (hijau)."
    elif senyawa == "Alkohol Tersier":
        pembahasan = "❌ **Kenapa TIDAK bereaksi:** Karbon yang mengikat gugus -OH pada alkohol tersier tidak memiliki atom hidrogen (hidrogen alfa) sama sekali, sehingga ikatan C-C harus diputus untuk oksidasi, yang mana tidak bisa dilakukan oleh dikromat."
    elif senyawa in ["Aseton", "Asam Asetat"]:
        pembahasan = f"❌ **Kenapa TIDAK bereaksi:** {senyawa} sudah berada pada tingkat oksidasi yang tinggi (karbonil keton/asam karboksilat stabil) sehingga tidak dapat dioksidasi lebih lanjut oleh oksidator sedang."
    else:
        pembahasan = "❌ **Kenapa TIDAK bereaksi:** " + alasan_negatif_umum(senyawa)

# 2. LUCAS
elif pereaksi == "Pereaksi Lucas (ZnCl2 / HCl)":
    if senyawa == "Alkohol Tersier":
        hasil = "(+) Keruh seketika"
        reaksi = "R₃C-OH + HCl → R₃C-Cl↓ + H₂O"
        pembahasan = "✅ **Kenapa bereaksi:** Alkohol tersier sangat mudah mengalami reaksi substitusi nukleofilik (SN1) karena membentuk karbokation tersier yang sangat stabil, langsung menghasilkan alkil klorida yang tak larut air."
    elif senyawa == "Alkohol Sekunder":
        hasil = "(+) Keruh setelah 5-10 menit"
        reaksi = "R₂CH-OH + HCl → R₂CH-Cl↓ + H₂O"
        pembahasan = "✅ **Kenapa bereaksi:** Reaksi berjalan lambat melalui mekanisme SN1 karena karbokation sekunder kurang stabil dibanding tersier. Butuh waktu untuk menghasilkan endapan alkil klorida."
    elif senyawa == "Alkohol Primer":
        pembahasan = "❌ **Kenapa TIDAK bereaksi:** Karbokation primer sangat tidak stabil. Tanpa pemanasan ekstrem, alkohol primer tidak akan bereaksi dengan pereaksi Lucas."
    else:
        pembahasan = "❌ **Kenapa TIDAK bereaksi:** Pereaksi Lucas dirancang khusus untuk mensubstitusi gugus hidroksil (-OH) pada alkohol. Senyawa ini tidak memiliki gugus -OH alkoholik bebas."

# 3. TOLLENS
elif pereaksi == "Pereaksi Tollens":
    if senyawa == "Formaldehida":
        hasil = "(+) Terbentuk Cermin Perak"
        reaksi = "R-CHO + 2[Ag(NH₃)₂]⁺ + 3OH⁻ → R-COO⁻ + 2Ag↓ + 4NH₃ + 2H₂O"
        pembahasan = "✅ **Kenapa bereaksi:** Gugus aldehid sangat mudah dioksidasi. Ia mampu mereduksi ion perak kompleks menjadi logam perak murni (Ag) yang menempel mengkilap di dinding tabung."
    elif senyawa == "Aseton":
        pembahasan = "❌ **Kenapa TIDAK bereaksi:** Keton (aseton) tidak memiliki atom hidrogen yang menempel pada gugus karbonil, sehingga tidak bisa dioksidasi oleh oksidator lemah seperti Tollens."
    else:
        pembahasan = "❌ **Kenapa TIDAK bereaksi:** Senyawa ini tidak mengandung gugus aldehid yang punya sifat pereduksi."

# 4. FEHLING
elif pereaksi == "Pereaksi Fehling":
    if senyawa == "Formaldehida":
        hasil = "(+) Terbentuk Endapan Merah Bata"
        reaksi = "R-CHO + 2Cu²⁺ + 5OH⁻ → R-COO⁻ + Cu₂O↓ (merah bata) + 3H₂O"
        pembahasan = "✅ **Kenapa bereaksi:** Aldehid memiliki sifat pereduksi yang kuat, mereduksi ion tembaga(II) kompleks berwarna biru menjadi endapan tembaga(I) oksida yang berwarna merah bata."
    elif senyawa == "Aseton":
        pembahasan = "❌ **Kenapa TIDAK bereaksi:** Sama seperti Tollens, keton tidak bisa dioksidasi oleh oksidator lemah seperti Fehling karena ketiadaan ikatan C-H pada gugus karbonilnya."
    else:
        pembahasan = "❌ **Kenapa TIDAK bereaksi:** Hanya senyawa aldehid alifatik yang memiliki sifat pereduksi untuk mereduksi ion Cu²⁺ pada suhu pemanasan."

# 5. IODOFORM
elif pereaksi == "Uji Iodoform (I2 / NaOH)":
    if senyawa == "Aseton":
        hasil = "(+) Endapan Kuning Iodoform"
        reaksi = "CH₃-CO-CH₃ + 3I₂ + 4NaOH → CHI₃↓ (kuning) + CH₃COONa + 3NaI + 3H₂O"
        pembahasan = "✅ **Kenapa bereaksi:** Aseton memiliki gugus metil keton ($CH_3-C=O$). Atom hidrogen alfa pada metil ini sangat asam, sehingga tersubstitusi oleh iodin lalu terputus membentuk endapan kuning iodoform ($CHI_3$)."
    else:
        pembahasan = "❌ **Kenapa TIDAK bereaksi:** Senyawa ini tidak memiliki struktur metil keton ($CH_3-CO-$) ataupun alkohol sekunder dengan struktur metil di sebelahnya ($CH_3-CH(OH)-$)."

# 6. JONES
elif pereaksi == "Pereaksi Jones (CrO3 / H2SO4)":
    if senyawa in ["Alkohol Primer", "Alkohol Sekunder", "Formaldehida"]:
        hasil = "(+) Warna berubah merah-jingga ke hijau/biru-hijau"
        reaksi = "CrO₃ (jingga) + H₂SO₄ + Senyawa → Cr³⁺ (hijau) + Hasil Oksidasi"
        pembahasan = "✅ **Kenapa bereaksi:** Jones adalah oksidator kuat. Memiliki atom hidrogen alfa membuat senyawa ini teroksidasi, sementara Kromium(VI) tereduksi menjadi Kromium(III) hijau."
    elif senyawa == "Alkohol Tersier":
        pembahasan = "❌ **Kenapa TIDAK bereaksi:** Tidak ada hidrogen pada karbon pengikat -OH. Oksidasi gagal terjadi."
    else:
        pembahasan = "❌ **Kenapa TIDAK bereaksi:** Senyawa sudah berada pada titik oksidasi maksimumnya (seperti asam asetat) atau tidak punya gugus yang bisa dioksidasi (seperti heksana)."

# 7. SCHIFF
elif pereaksi == "Pereaksi Schiff":
    if senyawa == "Formaldehida":
        hasil = "(+) Larutan berwarna Merah / Magenta"
        reaksi = "Aldehid + Pereaksi Schiff → Kompleks warna magenta"
        pembahasan = "✅ **Kenapa bereaksi:** Aldehid mudah bereaksi dengan fuksin-asam sulfit (Schiff) tanpa hambatan sterik (ruang), memulihkan kembali warna asli magenta dari fuksin."
    elif senyawa == "Aseton":
        pembahasan = "❌ **Kenapa TIDAK bereaksi:** Keton memiliki hambatan sterik (ruang lingkup molekul yang lebih besar) sehingga tidak bisa berikatan kuat dengan pereaksi Schiff untuk memunculkan warna."
    else:
        pembahasan = "❌ **Kenapa TIDAK bereaksi:** Pereaksi ini sangat spesifik bereaksi secara adisi nukleofilik hanya dengan gugus aldehid."

# 8. NA-BISULFIT
elif pereaksi == "Natrium Bisulfit (NaHSO3)":
    if senyawa in ["Formaldehida", "Aseton"]:
        hasil = "(+) Endapan Putih Kristalin"
        re