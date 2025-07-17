#!/usr/bin/env python3

# Gerekli kütüphaneleri içe aktar
from quantcrypt.kem import MLKEM_1024
from quantcrypt.cipher import KryptonKEM
from pathlib import Path
import os

# --- Yapılandırma ---
# MLKEM_1024 algoritmasının özel anahtar boyutu (önceden belirlenmiş)
# Bu değeri kod içinde dinamik olarak alacağız.
MLKEM_1024_SK_SIZE = None # Başlangıçta bilinmiyor

# Başlangıç şifreli dosya (soruda verilen)
STARTING_ENCRYPTED_FILE = Path('flag_22.enc')

# output.raw dosyasının yolu
OUTPUT_RAW_FILE = Path('output.raw')

# --- KEM ve KRY Nesnelerini Başlat ---
try:
    kem = MLKEM_1024() # MLKEM_1024 KEM nesnesi
    kry = KryptonKEM(MLKEM_1024) # KryptonKEM şifreleyici nesnesi

    # MLKEM_1024'ün gerçek özel anahtar boyutunu al
    MLKEM_1024_SK_SIZE = kem.param_sizes.sk_size
    print(f"quantcrypt kütüphanesi başarıyla başlatıldı. MLKEM_1024 Özel Anahtar Boyutu: {MLKEM_1024_SK_SIZE} bayt.")

except ImportError:
    print("Hata: quantcrypt kütüphanesi bulunamadı. Lütfen yüklediğinizden emin olun (pip install quantcrypt).")
    exit(1)
except Exception as e:
    print(f"Hata: quantcrypt kütüphanesini başlatırken bir sorun oluştu: {e}")
    exit(1)

# --- output.raw Dosyasını Oku ve Anahtarları Parçalara Ayır ---
all_skeys = []
try:
    with open(OUTPUT_RAW_FILE, 'rb') as f:
        output_raw_data = f.read()

    # output.raw dosyasını MLKEM_1024_SK_SIZE boyutunda parçalara ayır
    # Her parça potansiyel bir özel anahtardır
    for i in range(0, len(output_raw_data), MLKEM_1024_SK_SIZE):
        skey_chunk = output_raw_data[i : i + MLKEM_1024_SK_SIZE]
        if len(skey_chunk) == MLKEM_1024_SK_SIZE:
            all_skeys.append(skey_chunk)
        else:
            # Sadece son parçanın eksik boyutlu olmasına izin veriyoruz, eğer dosya sonuysa
            if i + len(skey_chunk) == len(output_raw_data):
                print(f"Uyarı: output.raw dosyasının sonunda eksik boyutlu bir anahtar parçası bulundu. Boyut: {len(skey_chunk)}. Bu parça atlanıyor çünkü geçerli bir MLKEM anahtarı boyutu değil.")
                pass # Eksik parçayı ekleme
            else:
                print(f"Hata: output.raw dosyasının ortasında eksik boyutlu bir anahtar parçası bulundu. Konum: {i}, Boyut: {len(skey_chunk)}")
                print("Bu durum, output.raw dosyasının bozuk olduğunu veya yanlış MLKEM_1024_SK_SIZE kullanıldığını gösterebilir.")
                exit(1)


    print(f"'{OUTPUT_RAW_FILE.name}' dosyasından {len(all_skeys)} adet tam boyutlu anahtar parçası okundu. Toplam boyut: {len(output_raw_data)} bayt.")

except FileNotFoundError:
    print(f"Hata: '{OUTPUT_RAW_FILE.name}' dosyası bulunamadı. Lütfen 'mechanic.py' kodunu önce çalıştırdığınızdan emin olun.")
    exit(1)
except Exception as e:
    print(f"Hata: '{OUTPUT_RAW_FILE.name}' dosyasını okurken veya parçalara ayırırken bir sorun oluştu: {e}")
    exit(1)

# --- Şifre Çözme Zincirini Tersine Çevirme ---

# Mevcut şifreli dosya, başlangıç noktası olarak flag_22.enc
current_encrypted_file = STARTING_ENCRYPTED_FILE
# Şifre çözme adımlarını takip etmek için sayaç
# flag_22.enc'den flag.png'ye ulaşmak için 23 başarılı şifre çözme adımına ihtiyacımız var (0'dan 22'ye kadar olan c değerleri için).
current_c_value = 22 # flag_22.enc'nin c değeri
decryption_count = 0 # Başarılı şifre çözme sayısı

print(f"\nŞifre çözme zinciri başlatılıyor, '{current_encrypted_file.name}' dosyasından geriye doğru gidilecek...")

# Anahtar parçalarını tersten (en son üretilenden en eskiye) döngüye al
# output.raw dosyasındaki anahtarlar, m'nin bit sırasına göre yazılmıştır.
# flag_22.enc, m'nin 23. '1' bitiyle oluşan şifrelemedir.
# Bu nedenle, output.raw'ın sonundan başlayarak gerçek anahtarları arayacağız.
for i in range(len(all_skeys) - 1, -1, -1):
    skey_to_try = all_skeys[i]

    # Şifre çözme çıktısının dosya adını belirle
    # Eğer current_c_value 0'dan küçükse (yani flag_0.enc'yi çözdüysek), çıktı flag.png olmalı
    if current_c_value < 0:
        output_file_path = Path("flag.png")
    elif current_c_value == 0: # flag_0.enc'yi çözüyorsak, çıktı flag.png'dir
        output_file_path = Path("flag.png")
    else: # Diğer durumlarda, bir önceki c değerine sahip .enc dosyasıdır
        output_file_path = Path(f"flag_{current_c_value - 1}.enc")

    # --- Hata Ayıklama Bilgileri ---
    # print(f"\n--- Şifre Çözme Denemesi (Anahtar Index: {i}) ---")
    # print(f"Mevcut Şifreli Dosya: '{current_encrypted_file.name}'")
    # print(f"Hedef Düz Metin Dosyası: '{output_file_path.name}'")
    # print(f"KryptonKEM nesnesinin tipi: {type(kry)}")
    # print(f"KryptonKEM nesnesinin metodları: {dir(kry)}")
    # --- Hata Ayıklama Bilgileri Sonu ---

    # Şifre çözme işlemini dene
    try:
        # KryptonKEM'in decrypt_to_file metodu kullanılıyor: özel anahtar, şifreli dosya yolu, düz metin dosya yolu
        kry.decrypt_to_file(skey_to_try, current_encrypted_file, output_file_path)

        # Eğer şifre çözme başarılı olursa, bu bir gerçek özel anahtardı (m'nin biti '1' idi)
        decryption_count += 1
        print(f"Başarılı şifre çözme ({decryption_count}. adım): '{current_encrypted_file.name}' dosyasından '{output_file_path.name}' elde edildi.")

        # Şifre çözülen dosyayı bir sonraki adım için mevcut şifreli dosya olarak ayarla
        current_encrypted_file = output_file_path
        current_c_value -= 1 # c değerini bir azalt

        # Eğer flag.png'ye ulaştıysak döngüyü sonlandır
        if decryption_count == 23: # flag_22.enc'den flag.png'ye 23 adım var (c=0'dan c=22'ye)
            print(f"\nBaşarıyla 'flag.png' dosyasına ulaşıldı: {current_encrypted_file.resolve()}")
            break

    except Exception as e:
        # Şifre çözme başarısız olursa, hata mesajını yazdır
        # print(f"Anahtar '{i}' ({i+1}. anahtar) ile şifre çözme başarısız oldu. Hata: {e}. Atlanıyor.")
        pass # Hata mesajını yorum satırı yaparak çıktıyı temiz tutabiliriz

# Eğer döngü bittiğinde flag.png'ye ulaşılamadıysa
if current_encrypted_file.name != "flag.png":
    print("\nUyarı: Tüm anahtarlar denendi ancak 'flag.png' dosyasına ulaşılamadı.")
    print(f"Son ulaşılan dosya: {current_encrypted_file.name}")
    print("Olası nedenler: 'flag_22.enc' dosyası hatalı, 'output.raw' içeriği bozuk, veya 'm' sayısının yapısı beklenenden farklı.")
