# Proje 3 — Dışsal Bellek Tabanlı Büyük Dosya Sıralayıcısı

Büyük CSV dosyalarını tamamını belleğe yüklemeden küçükten büyüğe sıralayan Python projesi. External Merge Sort algoritmasıyla veri bloklara ayrılır, sıralı geçici parçalar diske yazılır ve `heapq.merge()` ile birleştirilir.

## Özellikler

- Flask web arayüzünden CSV yükleme ve sonuç indirme.
- Konsol ve Tkinter masaüstü arayüzü.
- Ayarlanabilir blok boyutu; varsayılan 10.000 satır.
- Her birleştirme grubunda en fazla 64 girdi dosyası açan aşamalı birleştirme.
- Negatif sayıları ve tekrarlı değerleri destekleme.
- Geçici sıralama parçalarının otomatik temizlenmesi.
- Web arayüzünde satır sayısı, ilk parça sayısı ve işlem süresi.

## Gereksinimler

Python 3.10 veya üzeri. Konsol sürümü yalnızca standart kütüphaneyi kullanır. Web arayüzü için Flask, masaüstü arayüzü için Tkinter gerekir. Bazı Linux kurulumlarında Tkinter ayrıca kurulmalıdır.

## Kurulum ve web arayüzü

ZIP dosyasını ayıklayın, proje klasörünü VS Code ile açın ve terminalde çalıştırın:

```bash
python -m pip install -r requirements.txt
python web_app.py
```

Tarayıcıda **http://127.0.0.1:5000** adresini açın. `girdi.csv` dosyasını seçin, blok boyutunu belirleyin ve **Sıralamayı Başlat** düğmesine basın. İşlem bitince sıralanmış CSV dosyasını indirin. Durdurmak için terminalde `Ctrl+C` kullanın.

### Konsol

```bash
python main.py
```

`girdi.csv` sıralanarak aynı klasörde `sirali_sonuc.csv` oluşturulur. Girdi yoksa 100.000 satırlık örnek veri üretilir.

### Masaüstü

```bash
python arayuz.py
```

CSV dosyası ve blok boyutu seçilir; çıktı proje klasörüne kaydedilir.

## Girdi biçimi

Başlıksız, tek sütunlu, UTF-8 kodlamalı tam sayı CSV dosyası kullanın. UTF-8 BOM desteklenir. Boş satırlar atlanır. Ek sütun, başlık veya ondalıklı sayı kabul edilmez.

```csv
42
-7
15
42
0
```

Çıktı:

```csv
-7
0
15
42
42
```

## Algoritma

1. Dosyadan en fazla blok boyutu kadar sayı okunur.
2. Blok `list.sort()` ile sıralanır ve geçici CSV dosyasına yazılır.
3. Sıralı parçalar `heapq.merge()` ile akış hâlinde birleştirilir.
4. 64'ten fazla parça varsa ara birleştirme turları uygulanır.
5. Sonuç yazılır ve geçici parça klasörleri temizlenir.

Bellekte bir veri bloğu, parça yolları ve sınırlı sayıdaki akışın tamponları tutulur. Bellek kullanımı dosya büyüklüğünden tamamen bağımsız değildir; parça yollarının listesi parça sayısıyla büyür. Çok küçük bloklar disk işlemlerini ve süreyi artırır.

## Doğrulama

100.000 satırlık örnek veri, 10.000 satırlık bloklarla 10 parçaya ayrıldı. Çıktı, girdinin `sorted()` sonucu ile birebir karşılaştırıldı.

- İlk 10 sayı: `10, 38, 54, 55, 62, 63, 64, 74, 82, 90`
- Son 5 sayı: `999931, 999942, 999982, 999987, 999992`
- Negatif ve tekrarlı sayılar, boş dosya, UTF-8 BOM ve 4.201 tek satırlık parça kontrol edildi.
- Web üzerinden yükleme, sıralama ve indirme doğrulandı; hatalı veri, geçersiz blok, bulunamayan sonuç ve yükleme sınırı yanıtları kontrol edildi.

İşlem süresi bilgisayarın ve diskin hızına göre değişir.

## Dosyalar

| Dosya | İşlev |
| --- | --- |
| `main.py` | Ortak sıralama algoritması ve konsol çalıştırıcısı |
| `web_app.py` | Flask web arayüzü |
| `arayuz.py` | Tkinter masaüstü arayüzü |
| `girdi.csv` | 100.000 satırlık örnek veri |
| `requirements.txt` | Web arayüzü bağımlılığı |
| `Proje_3_Kod_Cikti_Kisa_Tanimlar.docx` | Kısa ödev özeti |

## Kullanım sınırları

Web uygulaması yerel ders demosudur; `127.0.0.1:5000` adresinde çalışır. HTTP yükleme gövdesinin sınırı 100 MiB'dir; dosya, form başlıklarıyla birlikte bu sınırın altında olmalıdır. Yükleme katmanı bellekte tamponlama yapabilir; parça tabanlı okuma sıralama aşamasında uygulanır. Diskte girdi, sıralı parçalar ve sonuç için yeterli boş alan gerekir.

Web sonuçları indirme için işletim sisteminin geçici klasöründeki `external_merge_sort_outputs` dizininde saklanır; sonuç dosyaları otomatik silinmez. Gerektiğinde uygulamayı durdurup bu klasörü temizleyebilirsiniz. Tkinter arayüzünde ilerleme çubuğu işlem sürdüğünü gösterir; yüzde hesabı yapmaz.

GitHub kaynak kodunu ve README'yi barındırır. Flask uygulaması GitHub Pages üzerinde doğrudan çalışmaz; yukarıdaki komutla yerel olarak başlatılır.
