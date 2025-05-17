import csv
import random
from datetime import datetime, timedelta

# Konfigurasi
desa = sorted(["Kartasura", "Ngadirejo", "Ngabeyan", "Singopuran", "Gonilan", 
               "Pabelan", "Kertonatan", "Makamhaji", "Ngemplak", "Pucangan", 
               "Gumpang", "Wirogunan"])

sungai_desa = {
    "Sungai kertonatan": ["Kertonatan", "Ngabeyan", "Singopuran"],
    "Sungai krecekan": ["Ngadirejo", "Kartasura"],
    "Sungai larangan": ["Kartasura", "Pabelan"],
    "Sungai gede_tanggul": ["Gumpang", "Ngemplak", "Wirogunan"],
    "Irigasi permukaan": ["Pucangan", "Makamhaji", "Gonilan"]
}

def apakah_hari_hujan(tanggal):
    bulan = tanggal.month
    if bulan in [11, 12, 1, 2, 3]:  # Musim hujan
        return random.random() > 0.1  # 90% kemungkinan hujan
    else:
        return random.random() > 0.7  # 30% kemungkinan hujan

def generate_curah_hujan_per_hari(hari_hujan, tanggal):
    bulan = tanggal.month
    curah_hujan = [0.0] * 24
    
    if not hari_hujan:
        return curah_hujan
    
    # Tentukan jumlah jam hujan berdasarkan musim
    if bulan in [11, 12, 1, 2, 3]:  # Musim hujan
        jam_hujan = sorted(random.sample(range(24), random.randint(4, 8)))  # 4-8 jam hujan
        for jam in jam_hujan:
            curah_hujan[jam] = round(random.uniform(10.0, 25.0), 2)  # Hujan deras
    else:  # Musim kemarau
        jam_hujan = sorted(random.sample(range(24), random.randint(1, 3)))  # 1-3 jam hujan
        for jam in jam_hujan:
            curah_hujan[jam] = round(random.uniform(5.0, 15.0), 2)  # Hujan ringan
    
    # Pastikan minimal ada 2 jam berturut-turut untuk potensi banjir
    for i in range(len(jam_hujan) - 1):
        if jam_hujan[i+1] == jam_hujan[i] + 1:
            break
    else:
        jam_random = random.randint(0, 22)
        jam_hujan.extend([jam_random, jam_random + 1])
        jam_hujan = sorted(list(set(jam_hujan)))
        for jam in jam_hujan[-2:]:  # Tambahkan hujan untuk 2 jam berurutan
            if bulan in [11, 12, 1, 2, 3]:
                curah_hujan[jam] = round(random.uniform(10.0, 40.0), 2)
            else:
                curah_hujan[jam] = round(random.uniform(5.0, 20.0), 2)
    
    return curah_hujan

def cek_banjir(desa_pilihan, curah_hujan_per_jam):
    aliran_sungai = next((sungai for sungai, daftar in sungai_desa.items() 
                         if desa_pilihan in daftar), "")
    if not aliran_sungai:
        return False
    
    # Cek hujan berturut-turut >= 2 jam dengan curah > 5 mm/jam
    for i in range(len(curah_hujan_per_jam) - 1):
        if curah_hujan_per_jam[i] > 5.0 and curah_hujan_per_jam[i+1] > 5.0:
            return True
    return False

def generate_data():
    with open('data_banjir_intensif.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Desa", "Tanggal", "Jam", "Curah Hujan (mm)", "Aliran Sungai", "Banjir"])

        for desa_pilihan in desa:
            current_date = datetime(2024, 1, 1)
            while current_date <= datetime(2024, 12, 31):
                hari_hujan = apakah_hari_hujan(current_date)
                curah_hujan_per_jam = generate_curah_hujan_per_hari(hari_hujan, current_date)
                banjir = cek_banjir(desa_pilihan, curah_hujan_per_jam)
                
                for hour in range(24):
                    aliran_sungai = next((sungai for sungai, daftar in sungai_desa.items() 
                                         if desa_pilihan in daftar), "")
                    writer.writerow([
                        desa_pilihan,
                        current_date.strftime("%Y-%m-%d"),
                        f"{hour:02d}:00:00",
                        curah_hujan_per_jam[hour],
                        aliran_sungai,
                        banjir
                    ])
                current_date += timedelta(days=1)

generate_data()