import csv
import random
from datetime import datetime, timedelta

# Konfigurasi
desa = sorted(["Kartasura", "Ngadirejo", "Ngabeyan", "Singopuran", "Gonilan", 
               "Pabelan", "Kertonatan", "Makamhaji", "Ngemplak", "Pucangan", 
               "Gumpang", "Wirogunan"])

# 1. Daftar sungai dan desa yang dilalui
sungai_desa = {
    "Sungai kertonatan": ["Kertonatan", "Ngabeyan", "Singopuran"],
    "Sungai krecekan": ["Ngadirejo", "Kartasura"],
    "Sungai larangan": ["Kartasura", "Pabelan"],
    "Sungai gede_tanggul": ["Gumpang", "Ngemplak", "Wirogunan"]
}

debit_maks = {
    "Sungai kertonatan": 19.80,
    "Sungai krecekan": 34.08,
    "Sungai larangan": 37.02,
    "Sungai gede_tanggul": 20.90 
}

# 2. Daftar desa dengan drainase buruk (termasuk yang punya irigasi)
daerah_rawan_banjir = ["Pucangan", "Makamhaji", "Gonilan"]

def generate_transisi_hujan(jam_hujan):
    curah_hujan = [0.0] * 24
    current_rain = 0.0
    
    for jam in range(24):
        if jam in jam_hujan:
            if current_rain < 5.0:  # Mulai hujan baru
                current_rain = random.uniform(5.0, 30.0 if jam_hujan else 20.0)
            else:  # Lanjutan hujan
                current_rain *= random.uniform(0.8, 1.5)  # Fluktuasi +-20%
        else:
            if current_rain > 0:  # Fade-out
                current_rain *= random.uniform(0.3, 0.8)  # Turun 20-70%
                if current_rain < 1.0:
                    current_rain = 0.0
        
        curah_hujan[jam] = round(current_rain, 2)
    return curah_hujan

def generate_curah_hujan_per_hari(hari_hujan, tanggal):
    if not hari_hujan:
        return [0.0] * 24
    
    bulan = tanggal.month
    # Tentukan jam hujan (musim hujan lebih banyak jam)
    if bulan in [11, 12, 1, 2, 3]:
        n_jam = random.randint(4, 12)  # Musim hujan: 4-12 jam
    else:
        n_jam = random.randint(1, 4)   # Musim kemarau: 1-4 jam
    
    jam_hujan = sorted(random.sample(range(24), n_jam))
    return generate_transisi_hujan(jam_hujan)

# ... (fungsi lainnya sama seperti sebelumnya)
def apakah_hari_hujan(tanggal):
    bulan = tanggal.month
    if bulan in [11, 12, 1, 2, 3]:  # Musim hujan (Nov-Mar)
        return random.random() > 0.1  # 90% kemungkinan hujan
    else:  # Musim kemarau (Apr-Okt)
        return random.random() > 0.7  # 30% kemungkinan hujan

def cek_banjir(desa_pilihan, curah_hujan_per_jam):
    # 1. Cek apakah desa termasuk daerah drainase buruk
    if desa_pilihan in daerah_rawan_banjir:
        # Kriteria banjir untuk drainase buruk:
        # - Ada hujan (>0 mm) DAN minimal 1 jam ≥5 mm
        ada_hujan = any(curah > 0 for curah in curah_hujan_per_jam)
        ada_hujan_deras = any(curah >= 5 for curah in curah_hujan_per_jam)
        return ada_hujan and ada_hujan_deras
    
    # 2. Cek apakah desa dilalui sungai
    dilalui_sungai = any(
        desa_pilihan in daftar_desa 
        for daftar_desa in sungai_desa.values()
    )
    
    # 3. Jika dilalui sungai, gunakan kriteria hujan ekstrem
    if dilalui_sungai:
        # Kriteria 1: Akumulasi 3 jam >15 mm
        for i in range(len(curah_hujan_per_jam) - 2):
            if sum(curah_hujan_per_jam[i:i+3]) > 15:
                return True
        
        # Kriteria 2: 2 jam berturut-turut >10 mm/jam
        for i in range(len(curah_hujan_per_jam) - 1):
            if curah_hujan_per_jam[i] > 10 and curah_hujan_per_jam[i+1] > 10:
                return True
    
    return False

def generate_data():
    with open('data_banjir_transisi_realistis.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Desa", "Tanggal", "Jam", "Curah Hujan (mm)", "Aliran Sungai", "Banjir"])

        for desa_pilihan in desa:
            current_date = datetime(2024, 1, 1)
            while current_date <= datetime(2024, 12, 31):
                hari_hujan = apakah_hari_hujan(current_date)
                curah_hujan = generate_curah_hujan_per_hari(hari_hujan, current_date)
                banjir = cek_banjir(desa_pilihan, curah_hujan)
                
                for hour in range(24):
                    aliran_sungai = next((sungai for sungai, daftar in sungai_desa.items() 
                                         if desa_pilihan in daftar), "")
                    writer.writerow([
                        desa_pilihan,
                        current_date.strftime("%Y-%m-%d"),
                        f"{hour:02d}:00:00",
                        curah_hujan[hour],
                        aliran_sungai,
                        banjir
                    ])
                current_date += timedelta(days=1)

generate_data()