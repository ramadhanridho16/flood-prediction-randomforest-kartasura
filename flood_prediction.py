# Konfigurasi
desa = sorted(["Kartasura", "Ngadirejo", "Ngabeyan", "Singopuran", "Gonilan", 
               "Pabelan", "Kertonatan", "Makamhaji", "Ngemplak", "Pucangan", 
               "Gumpang", "Wirogunan"])

luas_desa = {
    "Kartasura": 134,
    "Ngadirejo": 121,
    "Ngabeyan": 118,
    "Singopuran": 133,
    "Gonilan": 232,
    "Pabelan": 131,
    "Kertonatan": 120,
    "Makamhaji": 211,
    "Ngemplak": 170,
    "Pucangan": 228,
    "Gumpang": 192,
    "Wirogunan": 133,
}

# 1. Daftar sungai dan desa yang dilalui
sungai_desa = {
    "Sungai kertonatan": ["Kertonatan", "Ngabeyan", "Singopuran"],
    "Sungai krecekan": ["Pucangan" ,"Ngadirejo", "Kartasura"],
    "Sungai larangan": ["Kartasura", "Pabelan"],
    "Sungai gede_tanggul": ["Gumpang", "Ngemplak", "Wirogunan"]
}

debit_maks = {
    "Sungai kertonatan": 19.80,
    "Sungai krecekan": 34.08,
    "Sungai larangan": 37.02,
    "Sungai gede_tanggul": 20.90 
}

import streamlit as st
import pandas as pd
import joblib
# from data import debit_maks, luas_desa, sungai_desa  # Import dictionary

# Judul Aplikasi
st.title("Prediksi Banjir dan Kalkulator Debit Air Otomatis")

# 1. Load Model
@st.cache_resource
def load_model():
    return joblib.load('TrainModel/model_banjir_rf.pkl')

model = load_model()

# 2. Input Pengguna
st.sidebar.header("Parameter Input")

# Dropdown Pilih Desa
desa_list = list(luas_desa.keys())
selected_desa = st.sidebar.selectbox("Pilih Desa", desa_list)

# Input Curah Hujan
curah_hujan = st.number_input("Curah Hujan per Jam (mm)", min_value=0.0, value=5.0)

# 3. Hitung Debit Air Otomatis
luas = luas_desa[selected_desa]
debit_air_jam = curah_hujan * luas * 10  # Rumus debit air

# Hitung Debit Maks berdasarkan sungai
debit_maks_per_desa = {}
for sungai, desas in sungai_desa.items():
    for desa in desas:
        debit_maks_per_desa[desa] = debit_maks[sungai]

debit_maks_value = debit_maks_per_desa.get(selected_desa, 10.0) * 3600  # Konversi ke m³/jam

# Tampilkan Hasil Perhitungan
st.subheader("Hasil Kalkulasi Debit Air")
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Luas Desa (ha)", f"{luas} ha")
with col2:
    st.metric("Debit Air (m³/jam)", f"{debit_air_jam:.2f}")
with col3:
    st.metric("Debit Maks (m³/jam)", f"{debit_maks_value:.2f}")

# 4. Prediksi Banjir
if st.button("Prediksi Banjir"):
    input_data = pd.DataFrame({
        'rolling_rain_3h': [curah_hujan * 0.8],  # Contoh: rolling mean 80% dari curah hujan
        'Debit Air (m³/jam)': [debit_air_jam],
        'Debit Maks (m³/jam)': [debit_maks_value],
        'lag_1': [curah_hujan * 0.7]  # Contoh: lag 70% dari curah hujan
    })
    
    prediction = model.predict(input_data)[0]
    probability = model.predict_proba(input_data)[0][1]
    
    st.subheader("Hasil Prediksi")
    if prediction == 1:
        st.error(f"🚨 **BANJIR** (Probabilitas: {probability:.2%})")
    else:
        st.success(f"✅ **AMAN** (Probabilitas: {probability:.2%})")
    
    # Tampilkan detail input
    st.json({
        "Desa": selected_desa,
        "Curah Hujan (mm)": curah_hujan,
        "Debit Air (m³/jam)": debit_air_jam,
        "Debit Maks (m³/jam)": debit_maks_value
    })

# 5. Tampilkan Data Referensi
if st.checkbox("Lihat Tabel Referensi"):
    st.subheader("Data Referensi")
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Luas Desa (ha):**")
        st.dataframe(pd.DataFrame.from_dict(luas_desa, orient='index', columns=['Luas (ha)']))
    with col2:
        st.write("**Debit Maks Sungai (m³/detik):**")
        st.dataframe(pd.DataFrame.from_dict(debit_maks, orient='index', columns=['Debit Maks']))