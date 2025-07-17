#!/usr/bin/env sage

# Bu betik, 'output.raw' dosyasındaki Lagrange polinomunu okuyarak
# orijinal bayrağı yeniden oluşturmayı amaçlar.
# Orijinal 'interpol.sage' kodundaki üretim kurallarını tersine uygular.

try:
    # 'output.raw' dosyasını ikili okuma modunda aç
    with open('output.raw', 'rb') as f:
        # Serileştirilmiş polinom verisini SageMath'in loads() fonksiyonu ile yükle
        loaded_poly = loads(f.read())

    print("Polinom 'output.raw' dosyasından başarıyla yüklendi.")
    # Yüklenen polinomu görmek istersen aşağıdaki satırın yorumunu kaldırabilirsin:
    # print(f"Yüklenen Polinom: {loaded_poly}")

    # Potansiyel bayrak noktalarını depolayacak boş bir liste oluştur
    potential_flag_points = []

    # Orijinal kodda bayrak noktalarının x koordinatları negatif ve
    # -(1 + (19*n - 14) % len(flag)) formundaydı.
    # len(flag) bilinmediği için, x koordinatları -len(flag)'den -1'e kadar değişebilir.
    # Genellikle CTF bayrakları çok uzun olmaz (örn. 10-100 karakter).
    # Bu nedenle, x'i -350'den -1'e kadar kontrol etmek çoğu durum için yeterli olacaktır.
    # Daha uzun bir bayrak bekleniyorsa bu aralık genişletilebilir.
    x_start = -350 # Kontrol edilecek en küçük negatif x koordinatı
    x_end = -1     # Kontrol edilecek en büyük negatif x koordinatı

    # Belirtilen negatif x koordinatı aralığında döngü yap
    for x_coord in range(x_start, x_end + 1):
        # Polinomu mevcut x koordinatında değerlendirerek y değerini bul
        y_val = loaded_poly(x_coord)

        # Gürültü noktalarının y değerleri rasyonel sayılar (getPrime(32)/getPrime(32)) iken,
        # bayrak noktalarının y değerleri ASCII karakter kodları olduğu için tam sayıdır (ord()).
        # Bu nedenle, y_val'in bir tamsayı olup olmadığını ve ASCII aralığında (0-255) olup olmadığını kontrol et.
        if y_val.is_integer() and 0 <= int(y_val) <= 255:
            # Eğer koşullar sağlanıyorsa, bu bir potansiyel bayrak noktasıdır.
            potential_flag_points.append((x_coord, int(y_val)))

    # Bulunan potansiyel bayrak noktalarının sayısını ve kendilerini yazdır
    print(f"\nBulunan potansiyel bayrak noktaları ({len(potential_flag_points)} adet):")
    # Tüm noktaları görmek istersen aşağıdaki döngünün yorumunu kaldırabilirsin:
    # for p in potential_flag_points:
    #     print(f"  x: {p[0]}, y: {p[1]} (karakter: {chr(p[1])})")

    # Eğer hiç potansiyel bayrak noktası bulunamazsa bir hata mesajı göster
    if not potential_flag_points:
        print("Hiç potansiyel bayrak noktası bulunamadı. Polinomda hata olabilir veya bayrak çok kısa/uzun.")
    else:
        # Orijinal kodda, 'n' değeri len(flag)'e ulaştığında döngü durur.
        # Bu, tam olarak len(flag) adet bayrak noktasının DATA listesine eklendiği anlamına gelir.
        # Dolayısıyla, bulunan potansiyel bayrak noktalarının sayısı, bayrağın uzunluğuna eşit olmalıdır.
        estimated_flag_len = len(potential_flag_points)
        print(f"\nTahmini bayrak uzunluğu: {estimated_flag_len}")

        # Yeniden oluşturulan bayrak karakterlerini tutmak için bir liste oluştur
        # Başlangıçta boş karakterlerle doldurulur
        reconstructed_flag_chars = [''] * estimated_flag_len

        # Şimdi, 0'dan 'tahmini bayrak uzunluğu - 1'e kadar her 'n' değeri için
        # orijinal kodun beklediği x koordinatını hesaplayıp,
        # polinomu bu x koordinatında değerlendirerek ilgili y (ASCII) değerini bulalım.
        # Orijinal x koordinatı formülü: -(1 + (19*n - 14) % len(flag))
        # Orijinal y koordinatı formülü: ord(flag[(63 * n - 40) % len(flag)])
        for n_val in range(estimated_flag_len):
            # Orijinal kodun beklediği x koordinatını hesapla
            expected_x = -(1 + (19 * n_val - 14) % estimated_flag_len)

            # Polinomu bu beklenen x koordinatında değerlendirerek karakterin ASCII kodunu al
            y_char_code = loaded_poly(expected_x)

            # Y değerinin geçerli bir ASCII karakter kodu olduğundan emin ol
            if y_char_code.is_integer() and 0 <= int(y_char_code) <= 255:
                char_val = chr(int(y_char_code)) # ASCII kodunu karaktere dönüştür

                # Orijinal bayrak içindeki karakterin konumunu hesapla
                flag_index = (63 * n_val - 40) % estimated_flag_len

                # Karakteri doğru konumuna yerleştir
                reconstructed_flag_chars[flag_index] = char_val
            else:
                # Eğer beklenmedik bir y değeri bulunursa uyarı ver
                print(f"Uyarı: n={n_val} için beklenmeyen y değeri ({y_char_code}) veya x={expected_x} için geçersiz karakter kodu.")
                print("Bu durum, tahmini bayrak uzunluğunun yanlış olabileceğini gösterebilir.")

        # Eğer bayrak listesinde hala boş karakterler varsa, bazı karakterler bulunamamış demektir.
        if '' in reconstructed_flag_chars:
            print("\nUyarı: Bayrakta eksik karakterler var. Tahmini bayrak uzunluğu yanlış olabilir veya bazı noktalar bulunamadı.")
            print(f"Şu anki kısmi bayrak: {''.join(reconstructed_flag_chars)}")
        else:
            # Tüm karakterler başarıyla bulunursa, bayrağı birleştir ve yazdır
            reconstructed_flag = "".join(reconstructed_flag_chars)
            print(f"\nYeniden oluşturulan bayrak: {reconstructed_flag}")

except FileNotFoundError:
    print("Hata: 'output.raw' dosyası bulunamadı. Lütfen önce şifreleme kodunu çalıştırdığınızdan emin olun.")
except Exception as e:
    print(f"Polinomu yüklerken veya bayrağı yeniden oluştururken bir hata oluştu: {e}")
